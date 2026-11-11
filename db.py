import os
import secrets
import string
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
secret_key = os.getenv("SUPABASE_SECRET_KEY")

supabase = create_client(url, secret_key)

# Get events with optional filters#################################################

def get_events(event_type=None, event_date=None):
    query = supabase.table("event").select("*, location(*)")

    if event_type is not None:
        query = query.eq("event_type", event_type)

    if event_date is not None:
        # Accept a date string from Flask or a Python date object.
        if isinstance(event_date, str):
            event_date = datetime.strptime(
                event_date, "%Y-%m-%d"
            ).date()
        elif isinstance(event_date, datetime):
            event_date = event_date.date()

        next_day = event_date + timedelta(days=1)

        query = query.gte("start_time", event_date.isoformat())
        query = query.lt("start_time", next_day.isoformat())

    response = query.execute()

    formatted_events = []

    for event in response.data:
        location = event.get("location") or {}
        location_name = location.get("location_name")

        spots_left = get_event_spots_left(event["event_id"])

        formatted_events.append({
            "event_id": event["event_id"],
            "event_name": event["event_name"],
            "event_type": event["event_type"],
            "start_time": event["start_time"],
            "end_time": event["end_time"],
            "price": event["price"],
            "spots_left": spots_left,
            "age_rule": event["age_rule"],
            "min_age": event["min_age"],
            "max_age": event["max_age"],
            "location_name": location_name
        })

    return formatted_events

# Get remaining spots for an event###################################################

def get_event_spots_left(event_id):
    response = supabase.table("v_event_attendance") \
        .select("event_id, guest_capacity, booked_people") \
        .eq("event_id", event_id) \
        .execute()

    if not response.data:
        return None

    event = response.data[0]

    spots_left = event["guest_capacity"] - event["booked_people"]

    return spots_left

######################################################################################

def get_event_by_id(event_id):
    response = supabase.table("event") \
        .select("*, location(*)") \
        .eq("event_id", event_id) \
        .execute()

    if not response.data:
        return None

    event = response.data[0]

    location = event.get("location") or {}
    location_name = location.get("location_name")

    spots_left = get_event_spots_left(event_id)

    return {
        "event_id": event["event_id"],
        "event_name": event["event_name"],
        "event_type": event["event_type"],
        "start_time": event["start_time"],
        "end_time": event["end_time"],
        "price": event["price"],
        "spots_left": spots_left,
        "age_rule": event["age_rule"],
        "min_age": event["min_age"],
        "max_age": event["max_age"],
        "location_name": location_name,
        "description": event["description"],
        "max_party_size": event["max_party_size"]
    }

#Create a new customer account######################################################

def signup_customer(email, password, first_name, last_name, phone_number=None):

    # Step 1: Create the user in Supabase Authentication
    # create_user returns a UserResponse; the actual user is on .user
    # email_confirm=True so the customer can log in right away
    # (admin-created users get no confirmation email).
    auth_user = supabase.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True
    }).user

    try:
        ###Step 2: Save customer information and Auth ID###
        response = supabase.table("account").insert({
            "auth_user_id": auth_user.id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number
        }).execute()

        ###Step 3: Make sure the account was created###
        if not response.data:
            raise Exception("Account creation failed.")

        account = response.data[0]

        ###Step 4: Return information for Brian's Flask route###
        return {
            "account_id": account["account_id"],
            "first_name": account["first_name"]
        }

    except Exception:
        ##Step 5: Delete Auth user if database creation fails###
        supabase.auth.admin.delete_user(auth_user.id)
        raise

#####Log in an existing customer######################################################


def login_customer(email, password):
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    if not anon_key:
        raise Exception("Missing SUPABASE_ANON_KEY in .env file.")

    auth_client = create_client(url, anon_key)

    auth_response = auth_client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    auth_user_id = auth_response.user.id

    response = supabase.table("account") \
        .select("account_id, first_name") \
        .eq("auth_user_id", auth_user_id) \
        .execute()

    if not response.data:
        raise Exception("No account found for this user.")

    account = response.data[0]

    user = get_current_user(auth_response.session.access_token)

    if not user:
        raise Exception("Could not identify user role.")

    return {
        "account_id": account["account_id"],
        "first_name": account["first_name"],
        "role": user["role"],
        "access_token": auth_response.session.access_token,
        "refresh_token": auth_response.session.refresh_token
    }

##################################################################################

def create_registration(
    event_id,
    attendees,
    account_id=None,
    guest_first_name=None,
    guest_last_name=None,
    guest_email=None,
    guest_phone=None,
    how_heard=None,
    discount_code=None
):
    # Make sure at least one person is attending
    if not attendees:
        raise ValueError("At least one attendee is required.")

    # Guest bookings must include a name and email or phone
    if account_id is None:
        if not guest_first_name:
            raise ValueError("Guest first name is required.")

        if not guest_email and not guest_phone:
            raise ValueError("Guest email or phone is required.")

    # Check that the event exists
    event_response = supabase.table("event") \
        .select("event_id, host_id, price, guest_capacity, max_party_size, status") \
        .eq("event_id", event_id) \
        .execute()

    if not event_response.data:
        raise ValueError("Event not found.")

    event = event_response.data[0]

    # Make sure the event is open for registration
    if event["status"] != "open":
        raise ValueError("This event is not currently open for registration.")

    # Check maximum party size
    max_party_size = event["max_party_size"]

    if max_party_size is not None and len(attendees) > max_party_size:
        raise ValueError("Too many attendees for this event.")

    # Check remaining event capacity
    spots_left = get_event_spots_left(event_id)

    if spots_left is not None and len(attendees) > spots_left:
        raise ValueError("Not enough spots remaining.")

    # Calculate original price
    price_per_person = Decimal(str(event["price"]))
    subtotal = price_per_person * len(attendees)

    # Start with no discount
    discount_id = None
    discount_total = Decimal("0")

    # Apply a discount if a code was provided
    if discount_code:
        discount = get_event_discount_by_code(
            event_id,
            discount_code
        )

        if discount is None:
            raise ValueError("Invalid or inactive discount code.")

        discount_id = discount["discount_id"]

        # Check how many times this discount has been used
        if discount["max_uses"] is not None:
            usage_response = supabase.table("registration") \
                .select("registration_id", count="exact") \
                .eq("discount_id", discount_id) \
                .neq("status", "canceled") \
                .execute()

            if usage_response.count >= discount["max_uses"]:
                raise ValueError("This discount has reached its usage limit.")

        # Calculate percentage or fixed discount
        discount_amount = Decimal(str(discount["discount_amount"]))
        discount_type = discount["discount_type"].lower()

        if discount_type in ("percentage", "percent"):
            discount_total = subtotal * discount_amount / Decimal("100")

        elif discount_type in ("fixed", "fixed_amount"):
            discount_total = discount_amount

        else:
            raise ValueError("Unsupported discount type.")

        # Discount cannot exceed the original price
        discount_total = min(discount_total, subtotal)

    # Calculate final price
    final_price = subtotal - discount_total

    # Generate a random six-character booking code
    characters = string.ascii_uppercase + string.digits

    confirmation_code = "".join(
        secrets.choice(characters) for _ in range(6)
    )

    # Create the main registration record
    registration_response = supabase.table("registration").insert({
        "event_id": event_id,
        "account_id": account_id,
        "discount_id": discount_id,
        "guest_first_name": guest_first_name,
        "guest_last_name": guest_last_name,
        "guest_email": guest_email,
        "guest_phone": guest_phone,
        "how_heard": how_heard,
        "subtotal": float(subtotal),
        "discount_total": float(discount_total),
        "final_price": float(final_price),
        "confirmation_code": confirmation_code
    }).execute()

    if not registration_response.data:
        raise Exception("Registration creation failed.")

    registration = registration_response.data[0]
    registration_id = registration["registration_id"]

    try:
        # Prepare attendee records
        attendee_records = []

        for attendee in attendees:
            attendee_records.append({
                "registration_id": registration_id,
                "first_name": attendee["first_name"],
                "birth_date": attendee.get("birth_date"),
                "is_account_holder": attendee.get(
                    "is_account_holder", False
                )
            })

        # Insert all attendees
        attendee_response = supabase.table(
            "registration_attendee"
        ).insert(attendee_records).execute()

        if not attendee_response.data:
            raise Exception("Attendee creation failed.")

    except Exception:
        # Delete registration if attendee creation fails
        supabase.table("registration") \
            .delete() \
            .eq("registration_id", registration_id) \
            .execute()

        raise

    # Return completed booking information
    return {
        "registration_id": registration_id,
        "confirmation_code": confirmation_code,
        "qr_token": registration["qr_token"],
        "subtotal": float(subtotal),
        "discount_total": float(discount_total),
        "final_price": float(final_price),
        "attendees": attendee_response.data
    }

#####################################################################################

def get_registration_by_code(confirmation_code):
    # Make sure a confirmation code was provided
    if not confirmation_code:
        raise ValueError("Confirmation code is required.")

    # Search for the registration
    response = supabase.table("registration") \
        .select("*, registration_attendee(*)") \
        .eq("confirmation_code", confirmation_code.strip().upper()) \
        .execute()

    # Check whether a booking was found
    if not response.data:
        return None

    # Return the booking and its attendees
    return response.data[0]

######################################################################################

def get_registration_by_qr_token(qr_token):
    if not qr_token:
        raise ValueError("QR token is required.")

    response = supabase.table("registration") \
        .select("*, registration_attendee(*)") \
        .eq("qr_token", qr_token.strip()) \
        .execute()

    if not response.data:
        return None

    return response.data[0]

######################################################################################

def cancel_registration(registration_id):
    # Find the registration
    response = supabase.table("registration") \
        .select("*") \
        .eq("registration_id", registration_id) \
        .execute()

    # Make sure the registration exists
    if not response.data:
        return None

    registration = response.data[0]

    # Make sure it is currently booked
    if registration["status"] == "canceled":
        raise ValueError("This registration is already canceled.")

    if registration["status"] != "booked":
        raise ValueError("Only booked registrations can be canceled.")

    # Cancel only if it is still booked
    cancel_response = supabase.table("registration") \
        .update({
            "status": "canceled",
            "canceled_at": datetime.now(timezone.utc).isoformat()
        }) \
        .eq("registration_id", registration_id) \
        .eq("status", "booked") \
        .execute()

    if not cancel_response.data:
        raise ValueError(
            "Registration could not be canceled. It may have already changed."
        )

    return cancel_response.data[0]

######################################################################################

def check_in_attendee(
    attendee_id,
    host_id,
    account_id=None,
    checked_in_by=None,
    method="manual"
):
    response = supabase.table("registration_attendee") \
        .select("*, registration(event_id, status)") \
        .eq("attendee_id", attendee_id) \
        .execute()

    if not response.data:
        raise ValueError("Attendee not found.")

    attendee = response.data[0]
    registration = attendee["registration"]

    if registration["status"] != "booked":
        raise ValueError("This registration is not active.")

    event_response = supabase.table("event") \
        .select("host_id") \
        .eq("event_id", registration["event_id"]) \
        .execute()

    if not event_response.data:
        raise ValueError("Event not found.")

    if event_response.data[0]["host_id"] != host_id:
        raise ValueError("This host is not authorized to check in this attendee.")

    if attendee["attendance_status"] == "checked_in":
        raise ValueError("This attendee has already checked in.")

    if attendee["attendance_status"] != "expected":
        raise ValueError("This attendee is not eligible for check-in.")

    checkin_response = supabase.table("checkin").insert({
        "host_id": host_id,
        "attendee_id": attendee_id,
        "account_id": account_id,
        "method": method,
        "checked_in_by": checked_in_by
    }).execute()

    if not checkin_response.data:
        raise Exception("Check-in failed.")

    update_response = supabase.table("registration_attendee") \
        .update({"attendance_status": "checked_in"}) \
        .eq("attendee_id", attendee_id) \
        .execute()

    if not update_response.data:
        raise Exception("Attendee status update failed.")

    return checkin_response.data[0]

#####################################################################################

def check_in_by_qr_token(
    qr_token,
    host_id,
    account_id=None,
    checked_in_by=None
):
    registration = get_registration_by_qr_token(qr_token)

    if not registration:
        raise ValueError("Invalid QR code.")

    attendees = registration.get("registration_attendee", [])
    results = []

    for attendee in attendees:
        if attendee["attendance_status"] == "expected":
            result = check_in_attendee(
                attendee_id=attendee["attendee_id"],
                host_id=host_id,
                account_id=account_id,
                checked_in_by=checked_in_by,
                method="qr"
            )
            results.append(result)

    if not results:
        raise ValueError("All attendees have already checked in.")

    return results

####################################################################################

def get_event_attendance(event_id):
    # Get attendance information from the database view
    response = supabase.table("v_event_attendance") \
        .select("*") \
        .eq("event_id", event_id) \
        .execute()

    # Check whether the event was found
    if not response.data:
        return None

    # Return the attendance report
    return response.data[0]

######################################################################################

def mark_no_shows(event_id):
    # Run the Supabase database function
    response = supabase.rpc(
        "mark_no_shows",
        {"p_event_id": event_id}
    ).execute()

    return response.data

#####################################################################################

def logout_user(access_token, refresh_token):
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    auth_client = create_client(url, anon_key)

    auth_client.auth.set_session(access_token, refresh_token)
    auth_client.auth.sign_out()

    return {"ok": True}

######################################################################################


def update_customer_profile(access_token, first_name=None, last_name=None, phone_number=None):
    # Verify the customer's login token.
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    if not anon_key:
        raise Exception("Missing SUPABASE_ANON_KEY in .env file.")

    auth_client = create_client(url, anon_key)

    auth_response = auth_client.auth.get_user(access_token)
    auth_user_id = auth_response.user.id

    # Find the account belonging to this user.
    account_response = supabase.table("account") \
        .select("account_id") \
        .eq("auth_user_id", auth_user_id) \
        .execute()

    if not account_response.data:
        raise Exception("Customer account not found.")

    account_id = account_response.data[0]["account_id"]

    # Build the list of fields to update.
    updates = {}

    if first_name is not None:
        if not first_name.strip():
            raise ValueError("First name cannot be empty.")
        updates["first_name"] = first_name.strip()

    if last_name is not None:
        if not last_name.strip():
            raise ValueError("Last name cannot be empty.")
        updates["last_name"] = last_name.strip()

    if phone_number is not None:
        updates["phone_number"] = phone_number.strip() or None

    if not updates:
        raise ValueError("You must provide at least one field to update.")

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Save the changes.
    response = supabase.table("account") \
        .update(updates) \
        .eq("account_id", account_id) \
        .execute()

    if not response.data:
        raise Exception("Customer profile update failed.")

    account = response.data[0]

    return {
        "account_id": account["account_id"],
        "first_name": account["first_name"],
        "last_name": account["last_name"],
        "phone_number": account["phone_number"]
    }

######################################################################################

def get_current_user(access_token):
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    if not anon_key:
        raise Exception("Missing SUPABASE_ANON_KEY in .env file.")

    auth_client = create_client(url, anon_key)

    auth_response = auth_client.auth.get_user(access_token)
    auth_user_id = auth_response.user.id

    response = supabase.table("account") \
        .select("account_id, first_name") \
        .eq("auth_user_id", auth_user_id) \
        .execute()

    if not response.data:
        return None

    account = response.data[0]
    account_id = account["account_id"]

    # Check whether this account owns a host.
    owner_response = supabase.table("host") \
        .select("host_id") \
        .eq("owner_account_id", account_id) \
        .execute()

    if owner_response.data:
        role = "owner"

    else:
        # Check whether this account is staff for a host.
        staff_response = supabase.table("host_staff") \
            .select("staff_role") \
            .eq("account_id", account_id) \
            .execute()

        if staff_response.data:
            staff_roles = [
                str(item["staff_role"]).lower()
                for item in staff_response.data
                if item.get("staff_role")
            ]

            if "manager" in staff_roles:
                role = "manager"
            else:
                role = "staff"
        else:
            role = "customer"

    return {
        "logged_in": True,
        "account_id": account_id,
        "first_name": account["first_name"],
        "role": role
    }

# GET CUSTOMERS BY SOURCE REPORT######################################################

def get_customers_by_source():
    response = supabase.table("v_customers_by_source") \
        .select("*") \
        .execute()

    return response.data

######################################################################################

def get_loyalty_tenure():
    response = supabase.table("v_loyalty_tenure") \
        .select("*") \
        .execute()

    return response.data

# GET AVAILABLE SELECTIONS FOR AN EVENT###############################################

def get_event_selections(event_id):
    # Find which host owns the event.
    event_response = supabase.table("event") \
        .select("host_id") \
        .eq("event_id", event_id) \
        .execute()

    if not event_response.data:
        return None

    host_id = event_response.data[0]["host_id"]

    # Find active selections belonging to that host.
    response = supabase.table("selection") \
        .select("*") \
        .eq("host_id", host_id) \
        .eq("active", True) \
        .execute()

    return response.data


# GET ACTIVE DISCOUNTS FOR AN EVENT###################################################

def get_event_discounts(event_id):
    event_response = supabase.table("event") \
        .select("host_id") \
        .eq("event_id", event_id) \
        .execute()

    if not event_response.data:
        return None

    host_id = event_response.data[0]["host_id"]
    today = datetime.now(timezone.utc).date().isoformat()

    response = supabase.table("discount") \
        .select("*") \
        .eq("host_id", host_id) \
        .eq("active", True) \
        .execute()

    # Only include discounts within their date range.##################################
    discounts = []

    for discount in response.data:
        starts_on = discount["starts_on"]
        ends_on = discount["ends_on"]

        if starts_on and starts_on > today:
            continue

        if ends_on and ends_on < today:
            continue

        discounts.append(discount)

    return discounts


# GET ONE DISCOUNT BY CODE FOR AN EVENT###############################################

def get_event_discount_by_code(event_id, discount_code):
    if not discount_code:
        raise ValueError("Discount code is required.")

    discounts = get_event_discounts(event_id)

    if discounts is None:
        return None

    for discount in discounts:
        if discount["discount_code"].upper() == discount_code.strip().upper():
            return discount

    return None