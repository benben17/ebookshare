from datetime import datetime


EventType =[
    'PAYMENT-NETWORKS.ALTERNATIVE-PAYMENT.COMPLETED',
    'PAYMENT.CAPTURE.COMPLETED'
    ]

def paypal_order(cancel_url, return_url, product_name, amount, description):
    return {
        "intent": "order",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "cancel_url": cancel_url,
            "return_url": return_url
        },
        "transactions": [{
            "amount": {
                "total": amount,
                "currency": "USD"
            },
            "description": description
        }]
    }


def handle_webhook(event):
    event_type = event.event_type
    resource_type = event.resource_type
    resource_id = event.resource_id
