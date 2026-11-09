import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from db import (
    get_registration_by_code,
    get_registration_by_qr_token
)

# Replace these with a real booking's values from Supabase
confirmation_code = "KYX0GF"
qr_token = "035ce82945ab4f109516fccb6e663d5d"

print("Testing registration lookup by confirmation code...")

try:
    registration = get_registration_by_code(confirmation_code)
    print(registration)

    if registration:
        print("Success! Registration found by confirmation code.")
    else:
        print("Registration not found.")

except Exception as error:
    print("Confirmation code lookup failed:")
    print(error)


print("\nTesting registration lookup by QR token...")

try:
    registration = get_registration_by_qr_token(qr_token)
    print(registration)

    if registration:
        print("Success! Registration found by QR token.")
    else:
        print("Registration not found.")

except Exception as error:
    print("QR token lookup failed:")
    print(error)