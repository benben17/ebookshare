import logging

import paypalrestsdk
from flask import jsonify, request, Blueprint, redirect
from paypalrestsdk import Sale

from book import db
from book.dicts import PaymentStatus
from book.models import UserPay

from book.pay import create_order
from book.utils import get_file_name

blueprint = Blueprint(get_file_name(__file__), __name__, url_prefix='/api/v2/paypal')

paypalrestsdk.set_config({
    "mode": "sandbox", # sandbox or live
    "client_id": "AZ_sKR0Z1DqfWvxxqMEuGp_eKbzpw6UxVY_eru3tMtVT6lynFpXtqnpBvEGgnnFezwUQqZ1ub4KP7yKU",
    "client_secret": 'EIV9UQUC768yB_Gvfxrw0NMvX2XQ4s8mCLj3snSGWPVNWUg32ehGJ1jFu1GRG54fKsfkM6BwFU4FJJLa'
})


##sb-txxuw25469952@business.example.com


# 定义路由

@blueprint.route("/payment", methods=['GET', 'POST'])
def create_payment():
    cancel_url = "https://ebook.stararea.cn/api/v2/paypal/execute"
    return_url = "https://ebook.stararea.cn/api/v2/paypal/cancel"
    data = request.get_json()
    amount = data.get("amount")
    description = data.get("description")

    if not all([amount]):
        return jsonify({"message": "Missing required fields"}), 400

    # Create pay in database
    order = create_order(cancel_url, return_url, amount=amount, description=description,product_name="test product")
    print(order)
    try:
        payment = paypalrestsdk.Payment(order)
        print(payment.http_headers())
        print(payment)
        # print(pay.create(cancel_url, return_url)
        payment.create()

        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                print("Redirect for approval: %s" % (approval_url))
                return redirect(approval_url)
    except Exception as e:
        print(str(e))
        print(payment.error)
        return "Failed to create pay"


@blueprint.route("/execute", methods=['GET', 'POST'])
def execute_payment():
    paymentid = request.args.get("paymentId")  # 订单id
    payerid = request.args.get("PayerID")  # 支付者id
    if not paymentid:
        return jsonify({"message": "Missing pay ID"}), 400

    # Get pay from database
    # payment = UserPay.query.filter_by(payment_id=paymentid, status=PaymentStatus.created).first()
    # if not payment:
    #     return jsonify({"message": "Invalid pay ID or pay has already been processed"}), 400

    # Capture PayPal order
    try:
        payment = paypalrestsdk.Payment.find(paymentid)
        res = payment.execute({"payer_id": payerid})

        return jsonify({"message": "Payment successful"}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({"message": "Payment error"}), 440


@blueprint.route("/refund", methods=['GET', 'POST'])
def refund_payment():
    payment_id = request.args.get("paymentId")
    # pay = UserPay.query.filter_by(payment_id=payment_id).first()

    sale = Sale.find(payment_id)
    refund = sale.refund({
        "amount": {
            "total": "1.00",
            "currency": "USD"}})
    # Check refund status
    if refund.success():
        print("Refund[%s] Success" % (refund.id))
    else:
        print("Unable to Refund")
        print(refund.error)


@blueprint.route("/cancel", methods=['GET', 'POST'])
def cancel_payment():
    return jsonify({"status":200}),200

