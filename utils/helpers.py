import json


def load_customers():
    with open("data/customers.json", "r", encoding="utf-8") as file:
        return json.load(file)


def format_currency(value):
    return f"₹{value:,.0f}"
