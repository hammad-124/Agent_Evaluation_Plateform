from langchain.tools import tool
from data import users_data
from dotenv import load_dotenv
import logging
from object import PurchaseItem
from datetime import date





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
def calculate_right_refund(user:str, items:list[PurchaseItem]) -> str:
    """
    this tool takes the user username and  list of item  to be returned 
      as input and returns how much refund is worth.
    """

    logging.info(f"Calculating right refund  tool to get user: {user} refund")

    if users_data.get(user):
        total_refund = 0

        for item in items:
            if users_data[user].get(item.name):
                total_refund += users_data[user][item.name]["price"]
        return f"Total refund amount for useris: {total_refund}"
        return {"status":"Item not found in user's purchase history"}


@tool
def issue_refund_ticket(user:str,refund_amount:int) -> str:
    """
    this tool will send a ticket to the right team to return a refund
    """

    logging.info(f"Issuing refund ticket for user : {user} of amount: {refund_amount}")

    return f"Your refund ticket with the amount {refund_amount} has been created and it will be processed within 5-7 business days."

@tool
def check_current_date(user:str) -> str:


    """
    this tool will check the current date and return it in a string format.
    """
    logging.info(f"Checking current date for user: {user}")
    return date.today()



# print(get_user_purchase_history.invoke("user123"))

# book = PurchaseItem(name="book")  
# pen = PurchaseItem(name="pen")
# print(calculate_right_refund.invoke({
#     "user": "user123",
#     "items": [book, pen]})) 
# print(check_current_date.invoke("user123"))
# print(issue_refund_ticket.invoke("user123", 30))    