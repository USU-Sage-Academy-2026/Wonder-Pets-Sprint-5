import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from db import (
    get_events,
    get_event_by_id,
    get_event_attendance,
    get_customers_by_source,
    get_loyalty_tenure,
    get_event_selections,
    get_event_discounts
)

print("Starting final database tests...")

tests = [
    ("Get all events", lambda: get_events()),
    ("Get event by ID", lambda: get_event_by_id(3)),
    ("Get event attendance", lambda: get_event_attendance(3)),
    ("Get customers by source", lambda: get_customers_by_source()),
    ("Get loyalty tenure", lambda: get_loyalty_tenure()),
    ("Get event selections", lambda: get_event_selections(3)),
    ("Get event discounts", lambda: get_event_discounts(3))
]

for name, function in tests:
    print(f"\nTesting: {name}")

    try:
        result = function()
        print("SUCCESS")
        print(result)

    except Exception as error:
        print("FAILED")
        print(error)

print("\nFinal database tests completed.")