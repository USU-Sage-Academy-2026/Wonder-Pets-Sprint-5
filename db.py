import os
from datetime import timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
secret_key = os.getenv("SUPABASE_SECRET_KEY")

supabase = create_client(url, secret_key)

# Get events with optional filters
def get_events(event_type=None, event_date=None):
    query = supabase.table("event").select("*, location(*)")

    if event_type is not None:
        query = query.eq("event_type", event_type)

    if event_date is not None:
        next_day = event_date + timedelta(days=1)
        query = query.gte("start_time", event_date)
        query = query.lt("start_time", next_day)

    response = query.execute()
    events = response.data

    formatted_events = []

    for event in events:
        location_name = event["location"]["location_name"]
        spots_left = get_event_spots_left(event["event_id"])
        formatted_event = {
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
}
        formatted_events.append(formatted_event)

    return formatted_events

# Get remaining spots for an event
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

def get_event_by_id(event_id):
    response = supabase.table("event") \
        .select("*, location(*)") \
        .eq("event_id", event_id) \
        .execute()

    if not response.data:
        return None

    event = response.data[0]
    
    location_name = event["location"]["location_name"]
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

#Create a new customer account
def signup_customer(email, password, first_name, last_name, phone_number=None):

    # Step 1: Create the user in Supabase Authentication
    auth_user = supabase.auth.admin.create_user({
        "email": email,
        "password": password
    })

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

###Log in an existing customer###
def login_customer(email, password):

    # Step 1: Create a separate client for authentication
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    auth_client = create_client(url, anon_key)

    # Step 2: Check the customer's email and password
    auth_response = auth_client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    # Step 3: Get the customer's Auth ID
    auth_user_id = auth_response.user.id

    # Step 4: Find the matching account in our database
    response = supabase.table("account") \
        .select("account_id, first_name") \
        .eq("auth_user_id", auth_user_id) \
        .execute()

    if not response.data:
        raise Exception("No customer account found.")

    account = response.data[0]

    # Step 5: Return information for Brian's Flask route
    return {
        "account_id": account["account_id"],
        "first_name": account["first_name"],
        "role": "customer"
    }