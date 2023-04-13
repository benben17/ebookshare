from datetime import datetime


EventType =[
    'PAYMENT-NETWORKS.ALTERNATIVE-PAYMENT.COMPLETED',
    'PAYMENT.CAPTURE.COMPLETED'
    ]

WEBHOOK_ID = '3MM33169T1180223E'
WEBHOOK_URL = "https://ebook.stararea.cn/api/v2/paypal/notification/event"

sandbox_config = {
    "mode": "sandbox",  # sandbox or live
    "client_id": "AZ_sKR0Z1DqfWvxxqMEuGp_eKbzpw6UxVY_eru3tMtVT6lynFpXtqnpBvEGgnnFezwUQqZ1ub4KP7yKU",
    "client_secret": 'EIV9UQUC768yB_Gvfxrw0NMvX2XQ4s8mCLj3snSGWPVNWUg32ehGJ1jFu1GRG54fKsfkM6BwFU4FJJLa'
}
live_config = {
    "mode": "live",  # sandbox or live
    "client_id": "AV80RXlauTbODxEXDTyqQZw2NFWKiltlAMT0LYpueV53-Wlv063OJSzQym1cCjOGPf0CAVz2tFnwDyJC",
    "client_secret": 'EAWMwD_L9LXCEMzOUBwLNdcta4gun77p19VWVKlzrPLsps4ThI3P017An6jFkta9hznvmfFKk2dSP3jl'
}
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
