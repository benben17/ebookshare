import json
import logging
from datetime import datetime, timedelta
import paypalrestsdk
from flask import request, Blueprint, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from paypalrestsdk import WebhookEvent
import book.dicts
import config
from book import db
from book.dicts import PaymentStatus, Product, UserRole
from book.models import UserPay, User
from book.pay import paypal_order, sandbox_config, WEBHOOK_URL, live_config
from book.upgradeUser import upgrade_user_by_paypal
from book.utils import get_file_name, utc_now
from book.utils.ApiResponse import *

blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2/paypal')

# paypalrestsdk.set_config(sandbox_config)
paypalrestsdk.set_config(live_config)


@blueprint.route("/payment", methods=['GET', 'POST'])
@jwt_required()
def create_payment():
    cancel_url = "https://rss2ebook.com/user/upgrade"
    return_url = config.MY_DOMAIN + "/api/v2/paypal/execute"
    data = request.get_json()
    product = data.get('product')
    if str(product).lower() not in ("month", "year", 'rss2ebook'):
        return APIResponse.bad_request(msg="Missing required product")

    p_dict = Product(str(product).lower()).get_product()
    p_name, p_amount, p_desc = p_dict['name'], p_dict['amount'], p_dict['desc']

    try:
        order = paypal_order(cancel_url=cancel_url, return_url=return_url, amount=p_amount,
                             description=p_desc)
        paypal_payment = paypalrestsdk.Payment(order)
        logging.error(paypal_payment)
        paypal_payment.create()
        print(paypal_payment.id)
        if paypal_payment.state != "created" or paypal_payment.error is not None:
            return APIResponse.created_failed(msg="Payment create failed!")
        # Create pay in database
        user_pay = UserPay(
            user_id=get_jwt_identity().get("id"), product_name=p_name, pay_type="paypal", amount=p_amount,
            description=p_desc, create_time=utc_now(), currency='USD', payment_id=paypal_payment.id,
            status=PaymentStatus.created, user_name=get_jwt_identity().get("name")
        )
        # logging.info(model_to_dict(user_pay))
        for link in paypal_payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                user_pay.pay_url = approval_url
                db.session.add(user_pay)
                db.session.commit()
                logging.error(f"Redirect for approval: {approval_url}")
                return APIResponse.success(data=approval_url)
    except Exception as e:
        logging.error(str(e))
        logging.error("-------")
        # logging.error(paypal_payment.error)
        APIResponse.bad_request(msg="Failed, Change payment method ")


@blueprint.route("/execute", methods=['GET', 'POST'])
def execute_payment():
    paymentid = request.args.get("paymentId")  # 订单id
    payerid = request.args.get("PayerID")  # 支付者id

    if not (paymentid and payerid):
        return redirect(config.UPGRADE_USER_URL)

    # Get pay from database
    user_pay = UserPay.query.filter_by(payment_id=paymentid, status=PaymentStatus.created).first()
    if not user_pay:
        return redirect(config.UPGRADE_USER_URL)
    # Capture PayPal order
    try:
        payment = paypalrestsdk.Payment.find(paymentid)
        res = payment.execute({"payer_id": payerid})
        logging.info(payment)
        if res:
            # 更新订单状态和支付时间
            user_pay.status = payment.state
            user_pay.pay_time = datetime.strptime(payment.update_time, "%Y-%m-%dT%H:%M:%SZ")
            db.session.add(user_pay)

            # 更新用户信息
            product = Product(user_pay.product_name).get_product()
            days = product['days']
            user = User.get_by_id(user_pay.user_id)
            if user.expires:
                expires = user.expires + timedelta(days=days)
            else:
                expires = datetime.utcnow() + timedelta(days=days)
            if upgrade_user_by_paypal(user_name=user_pay.user_name, days=days, expires=expires):
                user.role = UserRole.role_name('plus')
                user.expires = expires
                db.session.add(user)
            db.session.commit()

    except paypalrestsdk.exceptions.ResourceNotFound:
        logging.error("PayPal payment not found")
    except paypalrestsdk.exceptions.MissingParam as e:
        logging.error("Invalid PayPal payment parameters: %s" % str(e))
    except Exception as e:
        logging.exception("Failed to execute PayPal payment: %s" % str(e))
    return redirect(config.UPGRADE_USER_URL)


@blueprint.route("/refund", methods=['GET'])
def refund_payment():
    payment_id = request.args.get("paymentId")
    pay = UserPay.query.filter_by(payment_id=payment_id).first()
    if pay is None or pay.pay_time is None:
        return APIResponse.bad_request(msg="not payment")
    try:
        if pay.pay_time + timedelta(weeks=2) > datetime.utcnow():
            payment = paypalrestsdk.Payment.find(payment_id)
            logging.error(payment.transactions)
            sale_info = payment.transactions[0]
            sale_id = sale_info.related_resources[0].sale.id
            if not sale_id:
                return APIResponse.bad_request(msg="not found sale")
            sale = paypalrestsdk.Sale.find(sale_id)

            refund = sale.refund({"amount": {"total": pay.amount, "currency": "USD"}})
            # logging.error("paypal refund")
            logging.error(refund)
            if refund.success():  # Check refund status
                if refund.create_time:
                    refund_time = datetime.strptime(payment.update_time, "%Y-%m-%dT%H:%M:%SZ")
                else:
                    refund_time = utc_now()
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
    return redirect(config.UPGRADE_USER_URL)


@blueprint.route("/notification/event")
def notify_event():
    try:
        paypalrestsdk.configure
        request_body = json.loads(request.body.decode("utf-8"))
        webhook_event = WebhookEvent(request_body)

        webhook_event.verify(WEBHOOK_URL)
        print(webhook_event)
    except Exception as e:
        logging.error("event_error")
        logging.error(e)
    return jsonify({'status': book.dicts.RequestStatus.OK}), 200


if __name__ == '__main__':
    # payment = paypalrestsdk.Payment.find("PAYID-MQ3LZAQ9YU170557M3119926")
    # paypalrestsdk.Sale.find()
    # print(payment)
    # order = paypalrestsdk.Order.find("O-1A134413LR267235M")
    # print(order)
    print(paypalrestsdk.WebhookEventType.all())
