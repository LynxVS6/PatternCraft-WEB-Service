import json
import random
import os
from app import create_app
from app.models import User, Problem

# Create Flask app context
app = create_app()
app.app_context().push()

# Get user ID range from database
min_user_id = User.query.order_by(User.id).first().id
max_user_id = User.query.order_by(User.id.desc()).first().id

# Get problem ID range from database
min_problem_id = Problem.query.order_by(Problem.id).first().id
max_problem_id = Problem.query.order_by(Problem.id.desc()).first().id

# Create a directory for the seed data if it doesn't exist
if not os.path.exists("seed_data"):
    os.makedirs("seed_data")

# Sample solution templates
solution_templates = [
    """
    class Solution:
        def solve(self, data):
            # TODO: Implement your solution here
            pass
    """,
    """
    class Solution:
        def __init__(self):
            self.result = None
        
        def process(self, input_data):
            # TODO: Add your implementation
            return self.result
    """,
    """
    class Solution:
        @staticmethod
        def solve(input_data):
            # TODO: Write your code here
            return None
    """,
    """
    class Solution:
        def __init__(self):
            self.cache = {}

        def solve(self, data):
            # TODO: Implement caching logic
            return self.cache.get(data)
    """,
    """
    class Solution:
        def __init__(self):
            self.observers = []

        def solve(self, data):
            # TODO: Implement observer pattern
            for observer in self.observers:
                observer.update(data)
    """,
]

# Generate submissions
submissions = []
for i in range(600):  # Generate 600 submissions
    submission = {
        "server_problem_id": random.randint(min_problem_id, max_problem_id),
        "solution": random.choice(solution_templates),
        "user_id": random.randint(min_user_id, max_user_id),
        "is_seeded": True,
    }
    submissions.append(submission)

# Write to a single JSON file
filename = "seed_data/submissions.json"
with open(filename, "w") as f:
    json.dump(submissions, f, indent=2)

print("Generated submissions.json file in the seed_data directory.")
