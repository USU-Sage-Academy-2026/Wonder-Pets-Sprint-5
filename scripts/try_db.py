import sys
from pathlib import Path
from getpass import getpass

# This lets Python find db.py in the main project folder.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from db import (
    check_in_by_qr_token,
    login_customer,
    get_current_user,
    logout_user,
    update_customer_profile,
    mark_no_shows,
    get_customers_by_source,
    get_loyalty_tenure,
    get_event_selections,
    get_event_discounts,
    get_event_discount_by_code,
    create_registration,
    check_in_attendee,
    get_registration_by_qr_token,
    cancel_registration
)


# TEST CUSTOMER LOGIN
print("Testing customer login...")

# Check that the database URL loaded
print(url is not None)


# TEST CUSTOMER LOGIN
print("\nTesting customer login...")

email = input("Enter your test account email: ")
password = getpass("Enter your password: ")

login = login_customer(email, password)

print("\nLogin successful!")

print({
    "account_id": login["account_id"],
    "first_name": login["first_name"],
    "role": login["role"]
})


# TEST CUSTOMER PROFILE UPDATE
print("\nTesting customer profile update...")

updated_profile = update_customer_profile(
    login["access_token"],
    first_name=login["first_name"]
)

print(updated_profile)


# TEST GET CURRENT USER
print("\nTesting current user...")

user = get_current_user(login["access_token"])

print(user)


# TEST LOGOUT
print("\nTesting logout...")

logout = logout_user(
    login["access_token"],
    login["refresh_token"]
)

print(logout)

print("\nAll authentication tests completed!")


# TEST MARK NO-SHOWS
print("\nTesting mark no-shows...")

result = mark_no_shows(3)

print("No-show function executed!")
print("Attendees marked as no-show:", result)


# TEST CUSTOMERS BY SOURCE REPORT
print("\nTesting customers by source report...")

source_report = get_customers_by_source()

print(source_report)


# TEST LOYALTY TENURE REPORT
print("\nTesting loyalty tenure report...")

loyalty_report = get_loyalty_tenure()

print(loyalty_report)


# TEST EVENT SELECTIONS
print("\nTesting event selections...")

selections = get_event_selections(3)

print(selections)


# TEST EVENT DISCOUNTS
print("\nTesting event discounts...")

discounts = get_event_discounts(3)

print(discounts)


# TEST DISCOUNT CODE LOOKUP
print("\nTesting discount code lookup...")

discount = get_event_discount_by_code(3, "TESTCODE")
print(discount)