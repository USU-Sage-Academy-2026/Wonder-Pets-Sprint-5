import sys
from pathlib import Path

# Allow Python to find db.py in the main project folder
sys.path.append(str(Path(__file__).resolve().parent.parent))

from db import cancel_registration


print("Testing cancellation of a nonexistent registration...")

try:
    result = cancel_registration(999999)

    if result is None:
        print("Success! Nonexistent registration was handled correctly.")
    else:
        print("Error: Unexpected registration was found.")
        print(result)

except Exception as error:
    print("Test failed:")
    print(error)