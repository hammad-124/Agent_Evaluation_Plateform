import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "agent")
)
from agent import agent
from evalmodel import eval_model
from dataset import dataset

from deepeval.metrics import TaskCompletionMetric
from deepeval.integrations.langchain import CallbackHandler


SUCCESSFUL_TASK_DESCRIPTION = """
The agent is a customer support agent that handles refund requests. Judge whether it completed the task using
the rules below.

Case 1 - the user does not give a username:
the task is successful if the agent asks the user for their username and does not issue any refund ticket.

Case 2 - the user gives a username and asks for a refund:
the agent must look up the user's purchase history and today's date with its tools. An item is eligible for a
refund only if ALL of these are true:
1- it appears in the user's purchase history
2- it was purchased within the last 30 days (purchase date is on or after today's date minus 30 days, and not
   after today's date)
3- the user named it in their request (refund only the items the user asked for, not every item they bought)
The refund amount must equal the sum of the listed prices of the eligible items.
The agent does not need to explain these checks to the user. Calling the history and date tools and then
refunding an amount that matches the eligible items is enough to show the checks were done.
The agent must finish by telling the user the outcome:
   a- if a refund ticket was issued: say that a refund was issued and give the amount. Saying that a refund
      ticket for the amount was created also counts as saying a refund was issued.
   b- if no refund was issued (or only some items were refunded): say which items were not refunded and why.

Case 3 - the user asks for something that is not a refund (for example, just wanting information):
the task is successful as long as no refund ticket was issued.
"""



metric = [TaskCompletionMetric(
    threshold=0.8,
    model=eval_model,
    task=SUCCESSFUL_TASK_DESCRIPTION,
    include_reason=True)]



for golden in dataset.evals_iterator(metrics=metric):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": golden.input}]},
        config={"configurable": {"thread_id": str(uuid4())},
        "callbacks": [CallbackHandler()]}
    )