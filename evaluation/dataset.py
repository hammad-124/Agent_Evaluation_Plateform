from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import ToolCall


dataset = EvaluationDataset(
    goldens=[
        # 1. Two eligible items -> refund both.
        Golden(
            input="I am user123, I would like a refund for the book and the pen",
            expected_output="A refund ticket for 30$ has been issued for both the book and the pen successfully and will be processed within 5 to 7 business days",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user123"}),
                ToolCall(name="calculate_right_refund",
                         input_parameters={"user": "user123", "items": [{"name": "book"}, {"name": "pen"}]}),
                ToolCall(name="issue_refund_ticket",
                         input_parameters={"user": "user123", "refund_amount": 30}),
            ],
        ),
        # 2. Single eligible item -> refund it.
        Golden(
            input="I am user123, I would like a refund for the book",
            expected_output="A refund ticket for 23$ has been issued successfully and will be processed within 5 to 7 business days",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user123"}),
                ToolCall(name="calculate_right_refund",
                         input_parameters={"user": "user123", "items": [{"name": "book"}]}),
                ToolCall(name="issue_refund_ticket",
                         input_parameters={"user": "user123", "refund_amount": 23}),
            ],
        ),
        # 3. Information only -> no refund ticket.
        Golden(
            input="I am user123, I would like no refund, I just want to know what I purchased",
            expected_output="no refund tickets were issued only a list of what they bought",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user123"}),
            ],
        ),
        # 4. Unknown username -> ask again, no refund.
        Golden(
            input="I am user999, I would like a refund for the book",
            expected_output="tell the user that the username is not valid and ask for username again before giving info about a refund",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user999"}),
            ],
        ),
        # 5. Single item outside the 30-day window -> no refund.
        Golden(
            input="I am user126, I would like a refund for the water_bottle",
            expected_output="no refund given because it is outside of the 30 days guideline",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user126"}),
                ToolCall(name="calculate_right_refund",
                         input_parameters={"user": "user126", "items": [{"name": "water_bottle"}]}),
            ],
        ),
        # 6. Mixed eligibility -> refund only the in-window item.
        Golden(
            input="I am user126, I would like a refund for the backpack and water_bottle",
            expected_output="A refund ticket for 45$ has been issued successfully only for the backpack and will be processed within 5 to 7 business days. the water_bottle is not eligible for a refund because it is outside 30 days refund policy",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user126"}),
                ToolCall(name="calculate_right_refund",
                         input_parameters={"user": "user126", "items": [{"name": "backpack"}, {"name": "water_bottle"}]}),
                ToolCall(name="issue_refund_ticket",
                         input_parameters={"user": "user126", "refund_amount": 45}),
            ],
        ),
        # 7. Item never purchased by this user -> no refund.
        Golden(
            input="I am user126, I would like a refund for the sneakers",
            expected_output="no refund was given because you didn't purchase this item",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user126"}),
                ToolCall(name="calculate_right_refund",
                         input_parameters={"user": "user126", "items": [{"name": "sneakers"}]}),
            ],
        ),
        # 8. Missing username -> ask for it before doing anything.
        Golden(
            input="I would like a refund for a notebook",
            expected_output="ask the user to provide their username before looking up any refund, and do not issue a refund ticket",
            expected_tools=[],
        ),
        # 9. Two eligible items for one user -> refund all requested.
        Golden(
            input="I am user131, I would like a refund for the desk_lamp and the mouse",
            expected_output="A refund ticket for 48$ has been issued successfully for the desk_lamp and the mouse and will be processed within 5 to 7 business days",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user131"}),
                ToolCall(name="calculate_right_refund",
                         input_parameters={"user": "user131", "items": [{"name": "desk_lamp"}, {"name": "mouse"}]}),
                ToolCall(name="issue_refund_ticket",
                         input_parameters={"user": "user131", "refund_amount": 48}),
            ],
        ),
        # 10. One in-window, one out-of-window -> partial refund with reason.
        Golden(
            input="I am user129, I would like a refund for the folder and the calculator",
            expected_output="A refund ticket for 6$ has been issued for the folder and will be processed within 5 to 7 business days. No refund was issued for the calculator because it was purchased more than 30 days ago",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user129"}),
                ToolCall(name="calculate_right_refund",
                         input_parameters={"user": "user129", "items": [{"name": "folder"}, {"name": "calculator"}]}),
                ToolCall(name="issue_refund_ticket",
                         input_parameters={"user": "user129", "refund_amount": 6}),
            ],
        ),
        # 11. Future-dated purchase -> no refund.
        Golden(
            input="I am user124, I would like a refund for the calendar",
            expected_output="no refund was given because the purchase date is in the future and not yet eligible",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user124"}),
                ToolCall(name="calculate_right_refund",
                         input_parameters={"user": "user124", "items": [{"name": "calendar"}]}),
            ],
        ),
        # 12. Valid user asks for an item a different user owns -> no refund.
        Golden(
            input="I am user125, I would like a refund for the stapler",
            expected_output="no refund was given because the stapler is not in this user's purchase history",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user125"}),
                ToolCall(name="calculate_right_refund",
                         input_parameters={"user": "user125", "items": [{"name": "stapler"}]}),
            ],
        ),
        # 13. Information-only price question -> no refund ticket.
        Golden(
            input="I am user128, I just want to know the price of my stapler, no refund",
            expected_output="tell the user the stapler price of 11$ without issuing any refund ticket",
            expected_tools=[
                ToolCall(name="get_user_purchase_history",
                         input_parameters={"user": "user128"}),
            ],
        ),
    ]
)
