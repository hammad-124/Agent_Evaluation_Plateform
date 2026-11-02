from langchain.tools import tool
from data import users_data
from dotenv import load_dotenv
import logging
from object import PurchaseItem
from datetime import date, timedelta


REFUND_WINDOW_DAYS = 30


def _parse_date(value: str) -> date:
    """Parse a 'YYYY-M-D' purchase date (padding optional) into a date."""
    year, month, day = (int(part) for part in value.split("-"))
    return date(year, month, day)



load_dotenv()

@tool
def get_user_purchase_history(user:str) -> dict:
    """
    this tool takes the user username as input and returns the 
    purchase history of the user in a dictionary format.
    """
    logging.info(f"Getting purchase history for user: {user}")
    if users_data.get(user):
        return users_data[user]
    return {"status": "User not found"
    }


@tool
def calculate_right_refund(user: str, items: list[PurchaseItem]) -> dict:
    """
    Takes the username and the list of items the user asked to be refunded.
    Pass every item the user requested; this tool applies the refund policy
    (item must be in the purchase history and purchased within the last 30
    days, not in the future) and returns the refundable amount together with
    which items are eligible and which are rejected and why.
    """

    logging.info(f"Calculating refund for user: {user}")

    history = users_data.get(user)
    if not history:
        return {
            "status": "user not found",
            "refund_amount": 0,
            "eligible_items": [],
            "rejected_items": [],
        }

    today = date.today()
    cutoff = today - timedelta(days=REFUND_WINDOW_DAYS)
    refund_amount = 0
    eligible_items = []
    rejected_items = []

    for item in items:
        record = history.get(item.name)
        if not record:
            rejected_items.append(
                {"name": item.name, "reason": "not in the user's purchase history"}
            )
            continue

        purchase_date = _parse_date(record["date"])
        if purchase_date > today:
            rejected_items.append(
                {"name": item.name, "reason": "the purchase date is in the future"}
            )
        elif purchase_date < cutoff:
            rejected_items.append(
                {"name": item.name, "reason": "purchased more than 30 days ago"}
            )
        else:
            refund_amount += record["price"]
            eligible_items.append({"name": item.name, "price": record["price"]})

    return {
        "status": "ok",
        "refund_amount": refund_amount,
        "eligible_items": eligible_items,
        "rejected_items": rejected_items,
    }


@tool
def issue_refund_ticket(user:str,refund_amount:int) -> str:
    """
    this tool will send a ticket to the right team to return a refund
    """

    logging.info(f"Issuing refund ticket for user : {user} of amount: {refund_amount}")

    return f"Your refund ticket with the amount {refund_amount} has been created and it will be processed within 5-7 business days."



# print(get_user_purchase_history.invoke("user123"))

# book = PurchaseItem(name="book")  
# pen = PurchaseItem(name="pen")
# print(calculate_right_refund.invoke({
#     "user": "user123",
#     "items": [book, pen]})) 
# print(check_current_date.invoke("user123"))
# print(issue_refund_ticket.invoke("user123", 30))    