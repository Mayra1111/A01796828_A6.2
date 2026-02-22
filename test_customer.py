"""Unit tests for Customer class."""

import json
import os
import unittest
import shutil
from customer import Customer, _load_customers, _save_customers, CUSTOMERS_FILE


class TestCustomer(unittest.TestCase):
    """Test cases for Customer class."""

    def setUp(self):
        """Set up test environment with a fresh data directory."""
        os.makedirs("data", exist_ok=True)
        if os.path.exists(CUSTOMERS_FILE):
            os.remove(CUSTOMERS_FILE)

    def tearDown(self):
        """Clean up test data files."""
        if os.path.exists(CUSTOMERS_FILE):
            os.remove(CUSTOMERS_FILE)

    # --- to_dict / from_dict ---

    def test_to_dict(self):
        """Test Customer to_dict returns correct structure."""
        customer = Customer("C1", "Alice", "alice@mail.com", "1234567890")
        d = customer.to_dict()
        self.assertEqual(d["customer_id"], "C1")
        self.assertEqual(d["name"], "Alice")
        self.assertEqual(d["email"], "alice@mail.com")

    def test_from_dict(self):
        """Test Customer from_dict creates correct instance."""
        data = {
            "customer_id": "C2",
            "name": "Bob",
            "email": "bob@mail.com",
            "phone": "0987654321",
        }
        customer = Customer.from_dict(data)
        self.assertEqual(customer.customer_id, "C2")
        self.assertEqual(customer.name, "Bob")

    # --- create_customer ---

    def test_create_customer_success(self):
        """Test successful customer creation."""
        customer = Customer.create_customer(
            "C1", "Alice", "alice@mail.com", "123"
        )
        self.assertIsNotNone(customer)
        self.assertEqual(customer.name, "Alice")

    def test_create_customer_duplicate(self):
        """Test creating a customer with duplicate ID returns None."""
        Customer.create_customer("C1", "Alice", "alice@mail.com", "123")
        result = Customer.create_customer("C1", "Bob", "bob@mail.com", "456")
        self.assertIsNone(result)

    # --- delete_customer ---

    def test_delete_customer_success(self):
        """Test successful customer deletion."""
        Customer.create_customer("C1", "Alice", "alice@mail.com", "123")
        result = Customer.delete_customer("C1")
        self.assertTrue(result)
        customers = _load_customers()
        self.assertNotIn("C1", customers)

    def test_delete_customer_not_found(self):
        """Test deleting a non-existent customer returns False."""
        result = Customer.delete_customer("NONEXISTENT")
        self.assertFalse(result)

    # --- display_customer ---

    def test_display_customer_success(self):
        """Test display returns correct Customer object."""
        Customer.create_customer("C1", "Alice", "alice@mail.com", "123")
        customer = Customer.display_customer("C1")
        self.assertIsNotNone(customer)
        self.assertEqual(customer.name, "Alice")

    def test_display_customer_not_found(self):
        """Test displaying a non-existent customer returns None."""
        result = Customer.display_customer("NONEXISTENT")
        self.assertIsNone(result)

    # --- modify_customer ---

    def test_modify_customer_name(self):
        """Test modifying customer name."""
        Customer.create_customer("C1", "Alice", "alice@mail.com", "123")
        result = Customer.modify_customer("C1", name="Alicia")
        self.assertTrue(result)
        customers = _load_customers()
        self.assertEqual(customers["C1"]["name"], "Alicia")

    def test_modify_customer_email(self):
        """Test modifying customer email."""
        Customer.create_customer("C1", "Alice", "alice@mail.com", "123")
        Customer.modify_customer("C1", email="new@mail.com")
        customers = _load_customers()
        self.assertEqual(customers["C1"]["email"], "new@mail.com")

    def test_modify_customer_phone(self):
        """Test modifying customer phone."""
        Customer.create_customer("C1", "Alice", "alice@mail.com", "123")
        Customer.modify_customer("C1", phone="999")
        customers = _load_customers()
        self.assertEqual(customers["C1"]["phone"], "999")

    def test_modify_customer_not_found(self):
        """Test modifying a non-existent customer returns False."""
        result = Customer.modify_customer("NONEXISTENT", name="Ghost")
        self.assertFalse(result)

    # --- invalid file handling ---

    def test_load_customers_invalid_json(self):
        """Test loading corrupted JSON file returns empty dict."""
        os.makedirs("data", exist_ok=True)
        with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
            f.write("INVALID JSON }{")
        customers = _load_customers()
        self.assertEqual(customers, {})

    def test_load_customers_invalid_format(self):
        """Test loading a JSON file with wrong format returns empty dict."""
        os.makedirs("data", exist_ok=True)
        with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
            json.dump(["not", "a", "dict"], f)
        customers = _load_customers()
        self.assertEqual(customers, {})

    def test_save_customers_creates_directory(self):
        """Test save creates data directory if missing."""
        if os.path.exists("data"):
            shutil.rmtree("data")
        customers = {
            "C1": {"customer_id": "C1", "name": "Test",
                   "email": "t@t.com", "phone": "0"}
        }
        _save_customers(customers)
        self.assertTrue(os.path.exists(CUSTOMERS_FILE))


if __name__ == "__main__":
    unittest.main()
