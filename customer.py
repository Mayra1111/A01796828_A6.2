"""Module for Customer class with file persistence."""

import json
import os

CUSTOMERS_FILE = "data/customers.json"


def _load_customers():
    """Load customers from JSON file."""
    if not os.path.exists(CUSTOMERS_FILE):
        return {}
    try:
        with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print("Error: customers file has invalid format. Starting fresh.")
                return {}
            return data
    except json.JSONDecodeError as e:
        print(f"Error reading customers file: {e}. Starting fresh.")
        return {}
    except OSError as e:
        print(f"Error opening customers file: {e}. Starting fresh.")
        return {}


def _save_customers(customers):
    """Save customers dictionary to JSON file."""
    os.makedirs("data", exist_ok=True)
    try:
        with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
            json.dump(customers, f, indent=4)
    except OSError as e:
        print(f"Error saving customers file: {e}")


class Customer:
    """Represents a customer in the reservation system."""

    def __init__(self, customer_id, name, email, phone):
        """Initialize a Customer instance."""
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone

    def to_dict(self):
        """Convert customer to dictionary."""
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Customer from a dictionary."""
        return cls(
            data["customer_id"],
            data["name"],
            data["email"],
            data["phone"],
        )

    @staticmethod
    def create_customer(customer_id, name, email, phone):
        """Create and persist a new customer."""
        customers = _load_customers()
        if customer_id in customers:
            print(f"Error: Customer with ID '{customer_id}' already exists.")
            return None
        customer = Customer(customer_id, name, email, phone)
        customers[customer_id] = customer.to_dict()
        _save_customers(customers)
        print(f"Customer '{name}' created successfully.")
        return customer

    @staticmethod
    def delete_customer(customer_id):
        """Delete a customer by ID."""
        customers = _load_customers()
        if customer_id not in customers:
            print(f"Error: Customer with ID '{customer_id}' not found.")
            return False
        del customers[customer_id]
        _save_customers(customers)
        print(f"Customer '{customer_id}' deleted successfully.")
        return True

    @staticmethod
    def display_customer(customer_id):
        """Display customer information."""
        customers = _load_customers()
        if customer_id not in customers:
            print(f"Error: Customer with ID '{customer_id}' not found.")
            return None
        data = customers[customer_id]
        print(f"--- Customer Info ---")
        print(f"ID    : {data['customer_id']}")
        print(f"Name  : {data['name']}")
        print(f"Email : {data['email']}")
        print(f"Phone : {data['phone']}")
        return Customer.from_dict(data)

    @staticmethod
    def modify_customer(customer_id, name=None, email=None, phone=None):
        """Modify customer attributes."""
        customers = _load_customers()
        if customer_id not in customers:
            print(f"Error: Customer with ID '{customer_id}' not found.")
            return False
        if name:
            customers[customer_id]["name"] = name
        if email:
            customers[customer_id]["email"] = email
        if phone:
            customers[customer_id]["phone"] = phone
        _save_customers(customers)
        print(f"Customer '{customer_id}' modified successfully.")
        return True
