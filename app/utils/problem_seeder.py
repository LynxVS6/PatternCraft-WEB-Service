import json
import random
import os
from app import create_app
from app.models import User

# Create Flask app context
app = create_app()
app.app_context().push()

# Get user ID range from database
min_user_id = User.query.order_by(User.id).first().id
max_user_id = User.query.order_by(User.id.desc()).first().id

# Create a directory for the seed data if it doesn't exist
if not os.path.exists("seed_data"):
    os.makedirs("seed_data")

# Sample data for generating random problems
difficulties = ["Easy", "Medium", "Hard"]
languages = ["Python", "JavaScript", "Java", "C++", "Ruby"]
statuses = ["Checked", "Beta"]

# Problem descriptions
descriptions = [
    """
    # Factory Method Pattern Challenge

    ## Problem Description
    Implement a Factory Method pattern to create different types of UI components
    based on the operating system (Windows, Mac, Linux).

    ## Requirements
    - Create an abstract factory interface
    - Implement concrete factories for each OS
    - Handle component creation through factory methods
    - Ensure proper encapsulation of object creation

    ## Example
    ```python
    # Abstract Factory
    class UIFactory:
        def create_button(self): pass
        def create_textbox(self): pass

    # Concrete Factory
    class WindowsUIFactory(UIFactory):
        def create_button(self):
            return WindowsButton()
    ```

    ## Constraints
    - Support at least 3 different OS types
    - Each OS should have unique component implementations
    - Maintain single responsibility principle

    ## Hints
    1. Consider using abstract base classes
    2. Think about component variations
    3. Consider using inheritance for factory classes
    """,

    """
    # Observer Pattern Challenge

    ## Problem Description
    Implement an event notification system using the Observer pattern where
    multiple subscribers can receive updates from a publisher.

    ## Requirements
    - Create a subject (publisher) interface
    - Implement observer (subscriber) interface
    - Handle subscription and unsubscription
    - Support multiple notification types

    ## Example
    ```python
    class Subject:
        def attach(self, observer): pass
        def detach(self, observer): pass
        def notify(self): pass

    class Observer:
        def update(self, data): pass
    ```

    ## Constraints
    - Support at least 5 different observer types
    - Handle concurrent notifications
    - Implement proper memory management

    ## Hints
    1. Consider using weak references
    2. Think about notification queuing
    3. Consider using event types
    """,

    """
    # SOLID Principles Challenge

    ## Problem Description
    Refactor a monolithic class into smaller, more focused classes following
    SOLID principles.

    ## Requirements
    - Apply Single Responsibility Principle
    - Implement Open/Closed Principle
    - Follow Liskov Substitution Principle
    - Use Interface Segregation
    - Apply Dependency Inversion

    ## Example
    ```python
    # Before
    class UserManager:
        def create_user(self): pass
        def send_email(self): pass
        def generate_report(self): pass

    # After
    class UserCreator:
        def create_user(self): pass

    class EmailSender:
        def send_email(self): pass
    ```

    ## Constraints
    - Each class should have one reason to change
    - New functionality should not modify existing code
    - Dependencies should be injected

    ## Hints
    1. Consider class responsibilities
    2. Think about interface design
    3. Consider dependency injection
    """,

    """
    # Decorator Pattern Challenge

    ## Problem Description
    Implement a text processing system using the Decorator pattern to add
    formatting capabilities dynamically.

    ## Requirements
    - Create a base text component
    - Implement decorator classes for different formatting
    - Support multiple decorator combinations
    - Handle decorator ordering

    ## Example
    ```python
    class TextComponent:
        def render(self): pass

    class BoldDecorator(TextComponent):
        def __init__(self, component):
            self.component = component
    ```

    ## Constraints
    - Support at least 4 different formatting options
    - Allow decorator chaining
    - Maintain proper encapsulation

    ## Hints
    1. Consider component composition
    2. Think about decorator order
    3. Consider using inheritance
    """,

    """
    # Strategy Pattern Challenge

    ## Problem Description
    Implement a payment processing system using the Strategy pattern to
    support different payment methods.

    ## Requirements
    - Create a payment strategy interface
    - Implement concrete strategies for each payment method
    - Support dynamic strategy switching
    - Handle payment validation

    ## Example
    ```python
    class PaymentStrategy:
        def process_payment(self, amount): pass

    class CreditCardStrategy(PaymentStrategy):
        def process_payment(self, amount):
            # Process credit card payment
            pass
    ```

    ## Constraints
    - Support at least 3 payment methods
    - Handle payment failures
    - Implement proper validation

    ## Hints
    1. Consider strategy selection
    2. Think about error handling
    3. Consider using factory with strategy
    """
]

# Problem types
problem_types = ["Behavioral", "Structural", "Creational", "Solid"]

# Available tags
available_tags = [
    "Factory Method",
    "Abstract Factory",
    "Builder",
    "Prototype",
    "Singleton",
    "Adapter",
    "Bridge",
    "Composite",
    "Decorator",
    "Facade",
    "Flyweight",
    "Proxy",
    "Chain of Responsibility",
    "Command",
    "Interpreter",
    "Iterator",
    "Mediator",
    "Memento",
    "Observer",
    "State",
    "Strategy",
    "Template Method",
    "Visitor",
    "SRP",
    "OCP",
    "LSP",
    "ISP",
    "DIP",
]

# Generate problems
problems = []
for i in range(300):
    problem_type = random.choice(problem_types)
    description = random.choice(descriptions)
    tag_number = random.randint(1, 6)
    problem = {
        "name": f"Problem {i+1}: {problem_type} Challenge",
        "description": description,
        "tags_json": random.sample(available_tags, tag_number),
        "difficulty": random.choice(difficulties),
        "language": random.choice(languages),
        "status": random.choice(statuses),
        "author_id": random.randint(min_user_id, max_user_id),
    }
    problems.append(problem)

# Write to a single JSON file
filename = "seed_data/problems.json"
with open(filename, "w") as f:
    json.dump(problems, f, indent=2)

print("Generated problems.json file in the seed_data directory.")
