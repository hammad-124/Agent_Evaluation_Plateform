from model import model
from tools import (
    get_user_purchase_history,
    calculate_right_refund,
    issue_refund_ticket,
    check_current_date
)
import logging
from dotenv import load_dotenv
from langchain.agents import create_agent
from prompt import agent_system_prompt as agent_prompt
from object import Answer
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage
from uuid import uuid4

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
agent = create_agent(
    model=model,
    tools=[
        get_user_purchase_history,
        calculate_right_refund,
        issue_refund_ticket,
        check_current_date
    ],
    system_prompt=agent_prompt,
    checkpointer=InMemorySaver(),
    response_format=Answer,
    name="refund_agent",
    # debug=True
)


def run_conversation():

    # Same thread_id maintains conversation memory
    config = {
        "configurable": {
            "thread_id": str(uuid4())
        }
    }
    text = "Hello, I want to request a refund for an item I purchased."
    print(f"User: {text}")
    question = HumanMessage(
        content=text
    )

    conversation = True

    while conversation:

        response = agent.invoke(
            {"messages": [question]},
            config=config
        )

        structured_response = response["structured_response"]

        print(f"Agent Response: {structured_response}")

        conversation = structured_response.conversation

        if conversation:
            user_input = input("Reply: \n")
            question = HumanMessage(content=user_input)

    print("The job is done")


# if __name__ == "__main__":
#     run_conversation()
