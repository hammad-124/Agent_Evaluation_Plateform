from datetime import date, timedelta

# Purchase dates are stored relative to "today" so the 30-day refund policy
# always evaluates the same way no matter when the evaluation is run.
# days_ago <= 30  -> within the refund window (eligible)
# days_ago  > 30  -> outside the window (not eligible)
# days_ago  < 0   -> purchase date is in the future (not eligible)
_TODAY = date.today()


def _days_ago(days: int) -> str:
    return (_TODAY - timedelta(days=days)).isoformat()


users_data = {
    "user123": {
        "book": {"price": 23, "date": _days_ago(28)},
        "pen": {"price": 7, "date": _days_ago(30)},
    },
    "user124": {
        "notebook": {"price": 12, "date": _days_ago(27)},
        # future-dated purchase, used to test the "not in the future" rule
        "calendar": {"price": 10, "date": _days_ago(-5)},
    },
    "user125": {
        "pencil": {"price": 3, "date": _days_ago(19)},
        "ruler": {"price": 5, "date": _days_ago(39)},
    },
    "user126": {
        "backpack": {"price": 45, "date": _days_ago(28)},
        "water_bottle": {"price": 18, "date": _days_ago(100)},
        "lunch_box": {"price": 14, "date": _days_ago(23)},
    },
    "user127": {
        "eraser": {"price": 2, "date": _days_ago(23)},
    },
    "user128": {
        "stapler": {"price": 11, "date": _days_ago(23)},
        "highlighter": {"price": 4, "date": _days_ago(23)},
    },
    "user129": {
        "calculator": {"price": 29, "date": _days_ago(39)},
        "folder": {"price": 6, "date": _days_ago(8)},
        "usb_drive": {"price": 16, "date": _days_ago(98)},
    },
    "user130": {
        "headphones": {"price": 35, "date": _days_ago(23)},
    },
    "user131": {
        "desk_lamp": {"price": 28, "date": _days_ago(29)},
        "mouse": {"price": 20, "date": _days_ago(29)},
    },
    "user132": {
        "sketchbook": {"price": 17, "date": _days_ago(19)},
        "paintbrush": {"price": 9, "date": _days_ago(18)},
        "canvas": {"price": 25, "date": _days_ago(95)},
    },
}

# print(users_data["user123"])
