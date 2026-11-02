import sys
from pathlib import Path
from uuid import uuid4

# deepeval's rich summary prints emoji; force UTF-8 so the run does not crash
# when stdout is redirected to a file or pipe on Windows (cp1252 default).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from dotenv import load_dotenv

from deepeval import evaluate
from deepeval.evaluate import CacheConfig, DisplayConfig
from deepeval.integrations.langchain import CallbackHandler
from deepeval.metrics import (
    ArgumentCorrectnessMetric,
    GEval,
    PlanAdherenceMetric,
    StepEfficiencyMetric,
    TaskCompletionMetric,
    ToolCorrectnessMetric,
)
from deepeval.test_case import LLMTestCase, SingleTurnParams, ToolCall

if __package__:
    from .dataset import dataset
    from evalmodel import eval_model
else:
    from dataset import dataset
    from evalmodel import eval_model


SUCCESSFUL_TASK_DESCRIPTION = """
If the username is missing, ask the user to provide it.
For a refund request, identify the customer and the requested purchases, and
check that each purchase is no more than 30 days old and is not in the future.
Refund only the items requested by the user. If the customer or requested item
cannot be found, do not issue a refund ticket and explain why.
Once the necessary information is available, tell the user whether a refund
ticket was issued and its amount, or explain why no refund was issued.
For an information-only request, answer the question without issuing a ticket.
"""


def build_metrics():
    """Keep the thresholds and evaluator model used by the individual scripts."""
    # PlanQualityMetric was removed on purpose: it grades an explicit plan
    # extracted from the trace, but this is a ReAct agent with no planner
    # (and gpt-6-luna's reasoning is encrypted in the trace), so the metric
    # measured the architecture, not the agent's behaviour. Task Completion,
    # Plan Adherence and Step Efficiency already cover planning quality here.
    trace_metrics = [
        TaskCompletionMetric(
            threshold=0.8,
            model=eval_model,
            task=SUCCESSFUL_TASK_DESCRIPTION,
            include_reason=True,
        ),
        StepEfficiencyMetric(
            threshold=0.8, model=eval_model, include_reason=True,
        ),
        PlanAdherenceMetric(
            threshold=0.8, model=eval_model, include_reason=True,
        ),
    ]
    single_turn_metrics = [
        ArgumentCorrectnessMetric(
            threshold=0.7,
            model=eval_model,
            include_reason=True,
        ),
        # Tool Correctness checks the right tools were called (by name).
        # Argument quality is judged separately by ArgumentCorrectnessMetric,
        # so we do not gate on exact input parameters here.
        ToolCorrectnessMetric(
            threshold=0.9,
            model=eval_model,
            include_reason=True,
        ),
        GEval(
            name="Answer Correctness",
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
                SingleTurnParams.EXPECTED_OUTPUT,
            ],
            evaluation_steps=[
                "Check that the actual output and expected output have the same "
                "logical conclusion about the user's request.",
            ],
            threshold=0.8,
            model=eval_model,
            verbose_mode=True,
        ),
    ]
    return trace_metrics, single_turn_metrics


def main():
    load_dotenv()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))
    from agent import agent

    trace_metrics, single_turn_metrics = build_metrics()
    cache_config = CacheConfig(use_cache=False, write_cache=False)
    display_config = DisplayConfig(inspect_after_run=False)
    test_cases = []

    # The callback captures the trace required by the four agentic metrics.
    for golden in dataset.evals_iterator(
        metrics=trace_metrics,
        cache_config=cache_config,
        display_config=display_config,
    ):
        response = agent.invoke(
            {"messages": [{"role": "user", "content": golden.input}]},
            config={
                "configurable": {"thread_id": str(uuid4())},
                "callbacks": [CallbackHandler()],
            },
        )

        tools_called = []
        for message in response["messages"]:
            for tool_call in getattr(message, "tool_calls", []) or []:
                tools_called.append(
                    ToolCall(
                        name=tool_call["name"],
                        input_parameters=tool_call["args"],
                    )
                )

        # Reuse the same response for the three remaining metrics. Keep these
        # cases local so repeated runs do not accumulate dataset.test_cases.
        test_cases.append(
            LLMTestCase(
                input=golden.input,
                actual_output=response["structured_response"].answer,
                expected_output=golden.expected_output,
                tools_called=tools_called,
                expected_tools=golden.expected_tools,
            )
        )

    evaluate(
        test_cases=test_cases,
        metrics=single_turn_metrics,
        cache_config=cache_config,
        display_config=display_config,
    )
    metric_count = len(trace_metrics) + len(single_turn_metrics)
    print(f"\nCompleted all {metric_count} metrics for {len(test_cases)} test cases.")


if __name__ == "__main__":
    main()