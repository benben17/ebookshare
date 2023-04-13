import json
import logging
from datetime import datetime, timedelta

import paypalrestsdk
from flask import request, Blueprint, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from paypalrestsdk import Sale, WebhookEvent
from sqlalchemy.exc import SQLAlchemyError

import config
from book import db
from book.dateUtil import get_days_later
from book.dicts import PaymentStatus, Product, UserRole
from book.models import UserPay, User

from book.pay import paypal_order
from book.upgradeUser import upgrade_user_by_paypal
from book.utils import get_file_name, get_now, model_to_dict
from book.utils.ApiResponse import *

blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2/paypal')

paypalrestsdk.set_config({
    "mode": "sandbox",  # sandbox or live
    "client_id": "AZ_sKR0Z1DqfWvxxqMEuGp_eKbzpw6UxVY_eru3tMtVT6lynFpXtqnpBvEGgnnFezwUQqZ1ub4KP7yKU",
    "client_secret": 'EIV9UQUC768yB_Gvfxrw0NMvX2XQ4s8mCLj3snSGWPVNWUg32ehGJ1jFu1GRG54fKsfkM6BwFU4FJJLa'
})

client_id = "AV80RXlauTbODxEXDTyqQZw2NFWKiltlAMT0LYpueV53-Wlv063OJSzQym1cCjOGPf0CAVz2tFnwDyJC"
secret = "EAWMwD_L9LXCEMzOUBwLNdcta4gun77p19VWVKlzrPLsps4ThI3P017An6jFkta9hznvmfFKk2dSP3jl"
##sb-txxuw25469952@business.example.com


# 定义路由
# host = 'https://rss2ebook.azurewebsites.net'
host = 'https://ebook.stararea.cn'


@blueprint.route("/payment", methods=['GET', 'POST'])
@jwt_required()
def create_payment():
    cancel_url = host + "/api/v2/paypal/cancel"
    return_url = host + "/api/v2/paypal/execute"
    data = request.get_json()
    product = data.get("product")
    print(str(product).lower())
    if str(product).lower() not in ("month", "year"):
        return APIResponse.bad_request(msg="Missing required product")
    user = get_jwt_identity()

    p_dict = Product(str(product).lower()).get_product()
    p_name = p_dict['name']
    p_amount = p_dict['amount']
    p_desc = p_dict['desc']

    try:
        order = paypal_order(cancel_url=cancel_url, return_url=return_url, amount=p_amount,
                             description=p_desc, product_name=p_name)
        payment = paypalrestsdk.Payment(order)
        logging.error(payment)
        # print(pay.create(cancel_url, return_url)
        payment.create()
        # Create pay in database
        print(payment.id)
        if payment.state != "created" and payment.error is None:
            return APIResponse.created_failed(msg="Payment create failed!")

        user_pay = UserPay(user_id=user['id'], product_name=p_name, pay_type="paypal", amount=p_amount,
                           description=p_desc,
                           create_time=get_now(), currency='USD', payment_id=payment.id, status=PaymentStatus.created,
                           user_name=user['name'])

        # logging.info(model_to_dict(user_pay))
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                user_pay.pay_url = approval_url
                db.session.add(user_pay)
                db.session.commit()
                logging.error("Redirect for approval: %s" % (approval_url))
                return redirect(approval_url)
    except Exception as e:
        logging.error(str(e))
        logging.error("-------")
        logging.error(payment.error)
        return "Failed to create pay"


@blueprint.route("/execute", methods=['GET', 'POST'])
def execute_payment():
    paymentid = request.args.get("paymentId")  # 订单id
    payerid = request.args.get("PayerID")  # 支付者id
    if not paymentid:
        return jsonify({"message": "Missing pay ID"}), 400

    # Get pay from database
    user_pay = UserPay.query.filter_by(payment_id=paymentid, status=PaymentStatus.created).first()
    if not user_pay:
        return APIResponse.bad_request(msg="Invalid pay ID or pay has already been processed")
    # Capture PayPal order
    try:
        payment = paypalrestsdk.Payment.find(paymentid)
        res = payment.execute({"payer_id": payerid})
        logging.info(payment)
        if res:
            user_pay.status = payment.state
            user_pay.pay_time = datetime.strptime(payment.update_time, "%Y-%m-%dT%H:%M:%SZ")
            db.session.add(user_pay)
            db.session.commit()

            product = Product(user_pay.product_name).get_product()
            days = product['days']
            user = User.get_by_id(user_pay.user_id)
            if user.expires:
                start_time = user.expires
            else:
                start_time = datetime.utcnow()
            expires = start_time + timedelta(days=days)
            print(expires)
            print("type", type(expires))
            if upgrade_user_by_paypal(user_name=user_pay.user_name, days=days, expires=expires):
                user.role = UserRole.role_name('plus')
                user.expires = expires
                db.session.add(user)
                db.session.commit()
                return APIResponse.success(msg="success")
            else:
                return APIResponse.internal_server_error(msg="server error")
        else:
            return APIResponse.bad_request(msg=payment.error)
    except SQLAlchemyError as e:
        logging.error(e)
        db.session.rollback()
        return APIResponse.internal_server_error(msg="error")
    except Exception as e:
        logging.error(e)
        return APIResponse.bad_request(msg=e)


@blueprint.route("/refund", methods=['GET', 'POST'])
def refund_payment():
    payment_id = request.args.get("paymentId")
    pay = UserPay.query.filter_by(payment_id=payment_id).first()
    if pay is None:
        return APIResponse.bad_request(msg="no payment")

    try:
        two_weeks_ago = datetime.utcnow() - timedelta(weeks=2)
        if not pay.pay_time < two_weeks_ago:
            payment = paypalrestsdk.Payment.find(payment_id)
            logging.error(payment.transactions)
            sale_info = payment.transactions[0]
            order_id = sale_info.related_resources[0].order.id
            if not order_id:
                return APIResponse.bad_request(msg="not found sale")
            order = paypalrestsdk.Order.find(order_id)

            refund = order.refund({"amount": {"total": pay.amount, "currency": "USD"}})
            logging.error("paypal refund")
            logging.error(refund)
            if refund.success():  # Check refund status
                if refund.create_time:
                    refund_time = datetime.strptime(payment.update_time, "%Y-%m-%dT%H:%M:%SZ")
                else:
                    refund_time = get_now()
                pay.refund_time = refund_time
                pay.refund_amount = pay.amount
                db.session.add(pay)
                db.session.commit()

                p_dict = Product(pay.product_name).get_product()
                days = p_dict['days']
                # 退款退费 更新用户
                user = User.get_by_id(pay.user_id)
                if user:
                    user.expires = user.expires + timedelta(days=-days)
                    if user.expires < datetime.utcnow():
                        user.role = UserRole.role_name()  # 设置为默认角色
                    if upgrade_user_by_paypal(user_name=user.name, days=-days, expires=user.expires):
                        db.session.add(user)
                        db.session.commit()
                return APIResponse.success(msg="refund success")
            else:
                logging.error(refund.error)
                return APIResponse.bad_request(msg="refund failed")
    except Exception as e:
        logging.error("Exception:" + str(e))
        return APIResponse.bad_request(msg=str(e))


@blueprint.route("/cancel", methods=['GET', 'POST'])
def cancel_payment():
    return redirect("/")


WEBHOOK_URL = "https//ebook.stararea.cn/api/v2/paypal/notification/event"
@blueprint.route("/notification/event")
def notify_event():
    try:
        request_body = json.loads(request.body.decode("utf-8"))
        hook_event = WebhookEvent(request_body)
        hook_event.verify(WEBHOOK_URL)
        print(hook_event)
    except Exception as e:
        logging.error("event_error")
        logging.error(e)


if __name__ == '__main__':
    payment = paypalrestsdk.Payment.find("PAYID-MQ3LZAQ9YU170557M3119926")
    # paypalrestsdk.Sale.find()
    print(payment)
    order = paypalrestsdk.Order.find("O-1A134413LR267235M")
    print(order)
    print(paypalrestsdk.WebhookEventType.all())
