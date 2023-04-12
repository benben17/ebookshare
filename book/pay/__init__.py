from datetime import datetime


def create_order(cancel_url, return_url, product_name, amount, description):
    return {
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "cancel_url": cancel_url,
            "return_url": return_url
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": product_name,
                    "sku": "sku",
                    "price": amount,
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": amount,
                "currency": "USD"
            },
            "description": description
        }]
    }


def format_time(time):
    return datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
