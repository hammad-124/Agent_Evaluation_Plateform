# Agent Evaluation Platform

A customer-support **refund agent** built with LangChain / LangGraph, together with a
[DeepEval](https://github.com/confident-ai/deepeval) test suite that measures the agent's
behaviour across six metrics.

The agent handles refund requests end to end: it identifies the customer, looks up their
purchase history, applies the refund policy, and either issues a refund ticket or explains
why no refund was given.

## Refund policy

An item is refundable only when **all** of these hold:

1. it exists in the customer's purchase history,
2. it was purchased within the **last 30 days** and not in the future, and
3. the customer actually asked to refund it.

The refund amount is the sum of the eligible items' prices. The 30-day / future-date rule is
enforced in code inside the `calculate_right_refund` tool, so eligibility does not depend on
the model reasoning about dates.

## Project layout

```
agent/
  agent.py     # builds the LangGraph agent (tools + prompt + structured output)
  prompt.py    # system prompt / refund guidelines
  tools.py     # get_user_purchase_history, calculate_right_refund, issue_refund_ticket
  data.py      # mock purchase history (dates are relative to today, so eligibility is stable)
  object.py    # Pydantic models (Answer, PurchaseItem)
  model.py     # chat model init

evaluation/
  dataset.py            # 13 goldens covering the refund scenarios
  eval_all.py           # single runner for all six metrics  <-- use this
  evalmodel.py          # evaluator ("judge") model
  task.completion.py    # individual metric scripts (optional)
  step_evaluation.py
  plan_Adherence.py
  arguments_correctness.py
  tool_correctness.py
  answer_correctness.py
```

## Running the evaluation

```bash
uv sync
cd evaluation
python eval_all.py
```

`eval_all.py` runs the agent once per test case and scores every metric in a single pass.

## Results

Latest run — **13 test cases**, evaluated with DeepEval.

| Metric | Avg. Score | Pass Rate | Passed / Total |
| --- | --- | --- | --- |
| Answer Correctness | 0.98 | 100% | 13 / 13 |
| Tool Correctness | 1.00 | 100% | 13 / 13 |
| Step Efficiency | 1.00 | 100% | 13 / 13 |
| Task Completion | 0.91 | 92% | 12 / 13 |
| Plan Adherence | 0.94 | 92% | 12 / 13 |
| Argument Correctness | 0.87 | 62% | 8 / 13 |

**What the metrics mean**

- **Answer Correctness** — the final reply matches the expected outcome.
- **Tool Correctness** — the right tools were called for each request.
- **Step Efficiency** — no redundant or wasted tool calls.
- **Task Completion** — the end state satisfies the full task.
- **Plan Adherence** — execution follows the agent's own plan.
- **Argument Correctness** — tool-call arguments are appropriate. The remaining gap here is
  largely a judge artifact: the evaluator flags the refund amount as "unsupported" because the
  user never types a dollar figure, even though the amount legitimately comes from the refund
  tool's output.

> Note: `PlanQualityMetric` was intentionally **not** included. It grades an explicit plan
> extracted from the trace, which this ReAct-style agent does not emit, so it measured the
> architecture rather than the agent's behaviour.

## Test scenarios covered

Two eligible items, single eligible item, information-only request, unknown username, item
outside the 30-day window, mixed eligibility (some items in-window, some not), item never
purchased, missing username, refund-all, future-dated purchase, and an item owned by a
different user.
