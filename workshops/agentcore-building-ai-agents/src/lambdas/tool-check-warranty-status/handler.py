import json


MOCK_WARRANTY_DB = {
    "ABC11111111": {
        "customer_email": "alice@example.com",
        "product": "Laptop Pro 15",
        "covered": True,
        "expires": "2026-12-31",
    },
    "DEF22222222": {
        "customer_email": "bob@example.com",
        "product": "Gaming Console Pro",
        "covered": True,
        "expires": "2025-09-30",
    },
    "GHI33333333": {
        "customer_email": "carol@example.com",
        "product": "Wireless Headphones",
        "covered": False,
        "expires": "2024-01-15",
    },
    "JKL44444444": {
        "customer_email": "dave@example.com",
        "product": "Smart Monitor 27",
        "covered": True,
        "expires": "2027-03-01",
    },
    "MNO33333333": {
        "customer_email": "eve@example.com",
        "product": "Gaming Console Pro",
        "covered": True,
        "expires": "2026-06-30",
    },
}


def lambda_handler(event, context):
    serial_number = event.get("serial_number", "")
    customer_email = event.get("customer_email")

    record = MOCK_WARRANTY_DB.get(serial_number.upper())
    if not record:
        return {
            "covered": False,
            "message": f"Serial number {serial_number} not found in warranty database.",
        }

    if customer_email and record["customer_email"].lower() != customer_email.lower():
        return {
            "covered": False,
            "message": "Email address does not match the registered owner.",
        }

    status = "active" if record["covered"] else "expired"
    return {
        "covered": record["covered"],
        "product": record["product"],
        "warranty_status": status,
        "expiry_date": record["expires"],
        "message": f"Warranty for {record['product']} (SN: {serial_number}) is {status} until {record['expires']}.",
    }
