import json
import random
import os
import string
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Create a directory for the seed data if it doesn't exist
if not os.path.exists("seed_data"):
    os.makedirs("seed_data")

# Sample data for generating random users
first_names = [
    "John", "Jane", "Michael", "Emily", "David", "Sarah", "James", "Emma", "Robert", "Olivia",
    "William", "Sophia", "Daniel", "Isabella", "Matthew", "Ava", "Joseph", "Mia", "Andrew", "Charlotte",
    "Thomas", "Amelia", "Joshua", "Harper", "Christopher", "Evelyn", "Anthony", "Abigail", "Kevin", "Elizabeth",
    "Brian", "Sofia", "George", "Avery", "Edward", "Ella", "Steven", "Scarlett", "Timothy", "Grace",
    "Jason", "Victoria", "Jeffrey", "Riley", "Ryan", "Aria", "Jacob", "Lily", "Gary", "Aubrey",
    "Nicholas", "Zoey", "Eric", "Penelope", "Jonathan", "Chloe", "Stephen", "Layla", "Larry", "Rebecca",
    "Justin", "Natalie", "Scott", "Hannah", "Brandon", "Zoe", "Benjamin", "Hazel", "Samuel", "Violet",
    "Gregory", "Aurora", "Alexander", "Savannah", "Patrick", "Audrey", "Frank", "Brooklyn", "Raymond", "Bella",
    "Jack", "Claire", "Dennis", "Skylar", "Jerry", "Lucy", "Tyler", "Paisley", "Aaron", "Everly",
    "Jose", "Anna", "Adam", "Caroline", "Nathan", "Nova", "Henry", "Genesis", "Douglas", "Emilia"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Phillips", "Evans", "Turner", "Torres", "Parker", "Collins", "Edwards", "Stewart", "Sanchez", "Morris",
    "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson",
    "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks",
    "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins",
    "Perry", "Powell", "Long", "Patterson", "Hughes", "Foster", "Butler", "Simmons", "Bryant", "Russell"
]

domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com"]


def generate_password():
    """Generate a random password with letters, numbers, and special chars."""
    length = random.randint(8, 12)
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return "".join(random.choice(chars) for _ in range(length))


# Generate users and their passwords
users = []
passwords = []

for i in range(100):  # Generate 100 users
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    username = (
        f"{first_name.lower()}" f"{last_name.lower()}" f"{random.randint(1, 999)}"
    )
    email = f"{username}@{random.choice(domains)}"

    # Generate password and its hash
    password = generate_password()
    password_hash = generate_password_hash(password)

    # Generate random dates within the last year
    created_at = datetime.utcnow() - timedelta(days=random.randint(0, 365))
    updated_at = created_at + timedelta(days=random.randint(0, 30))
    last_login = updated_at + timedelta(days=random.randint(0, 15))

    user = {
        "username": username,
        "email": email,
        "new_email": None,
        "email_confirmed": random.choice([True, False]),
        "password_hash": password_hash,
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat(),
        "last_login": last_login.isoformat() if random.random() > 0.2 else None,
    }
    users.append(user)

    # Store password separately
    password_entry = {"username": username, "email": email, "password": password}
    passwords.append(password_entry)

# Write users to JSON file
with open("seed_data/users.json", "w") as f:
    json.dump(users, f, indent=2)

# Write passwords to separate JSON file
with open("seed_data/user_passwords.json", "w") as f:
    json.dump(passwords, f, indent=2)

print("Generated users.json and user_passwords.json files in the seed_data directory.")
