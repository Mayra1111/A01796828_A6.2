"""Unit tests for Reservation class."""

import json
import os
import unittest
import shutil
from hotel import Hotel, HOTELS_FILE
from customer import Customer, CUSTOMERS_FILE
from reservation import (
    Reservation,
    _load_reservations,
    _save_reservations,
    RESERVATIONS_FILE,
)


class TestReservation(unittest.TestCase):
    """Test cases for Reservation class."""

    def setUp(self):
        """Set up test environment with sample hotel and customer."""
        os.makedirs("data", exist_ok=True)
        for f in [HOTELS_FILE, CUSTOMERS_FILE, RESERVATIONS_FILE]:
            if os.path.exists(f):
                os.remove(f)
        Hotel.create_hotel("H1", "Grand", "NYC", 5)
        Customer.create_customer("C1", "Alice", "alice@mail.com", "123")

    def tearDown(self):
        """Clean up test data files."""
        for f in [HOTELS_FILE, CUSTOMERS_FILE, RESERVATIONS_FILE]:
            if os.path.exists(f):
                os.remove(f)

    # --- to_dict / from_dict ---

    def test_to_dict(self):
        """Test Reservation to_dict returns correct structure."""
        res = Reservation("R1", "C1", "H1", "2025-01-01", "2025-01-05")
        d = res.to_dict()
        self.assertEqual(d["reservation_id"], "R1")
        self.assertEqual(d["customer_id"], "C1")
        self.assertEqual(d["hotel_id"], "H1")

    def test_from_dict(self):
        """Test Reservation from_dict creates correct instance."""
        data = {
            "reservation_id": "R2",
            "customer_id": "C1",
            "hotel_id": "H1",
            "check_in": "2025-02-01",
            "check_out": "2025-02-05",
        }
        res = Reservation.from_dict(data)
        self.assertEqual(res.reservation_id, "R2")
        self.assertEqual(res.check_in, "2025-02-01")

    # --- create_reservation ---

    def test_create_reservation_success(self):
        """Test successful reservation creation."""
        res = Reservation.create_reservation("C1", "H1", "2025-01-01", "2025-01-05")
        self.assertIsNotNone(res)
        self.assertEqual(res.customer_id, "C1")
        self.assertEqual(res.hotel_id, "H1")

    def test_create_reservation_decreases_available_rooms(self):
        """Test that creating a reservation decreases hotel available rooms."""
        Reservation.create_reservation("C1", "H1", "2025-01-01", "2025-01-05")
        from hotel import _load_hotels
        hotels = _load_hotels()
        self.assertEqual(hotels["H1"]["available_rooms"], 4)

    def test_create_reservation_customer_not_found(self):
        """Test creating reservation with invalid customer returns None."""
        result = Reservation.create_reservation(
            "INVALID_C", "H1", "2025-01-01", "2025-01-05"
        )
        self.assertIsNone(result)

    def test_create_reservation_hotel_not_found(self):
        """Test creating reservation with invalid hotel returns None."""
        result = Reservation.create_reservation(
            "C1", "INVALID_H", "2025-01-01", "2025-01-05"
        )
        self.assertIsNone(result)

    def test_create_reservation_no_rooms(self):
        """Test creating reservation when hotel has no rooms returns None."""
        Hotel.create_hotel("H_FULL", "Tiny", "NYC", 1)
        Reservation.create_reservation("C1", "H_FULL", "2025-01-01", "2025-01-02")
        result = Reservation.create_reservation(
            "C1", "H_FULL", "2025-01-03", "2025-01-04"
        )
        self.assertIsNone(result)

    # --- cancel_reservation ---

    def test_cancel_reservation_success(self):
        """Test successful reservation cancellation."""
        res = Reservation.create_reservation("C1", "H1", "2025-01-01", "2025-01-05")
        result = Reservation.cancel_reservation(res.reservation_id)
        self.assertTrue(result)
        reservations = _load_reservations()
        self.assertNotIn(res.reservation_id, reservations)

    def test_cancel_reservation_restores_room(self):
        """Test that cancelling a reservation restores available rooms."""
        res = Reservation.create_reservation("C1", "H1", "2025-01-01", "2025-01-05")
        Reservation.cancel_reservation(res.reservation_id)
        from hotel import _load_hotels
        hotels = _load_hotels()
        self.assertEqual(hotels["H1"]["available_rooms"], 5)

    def test_cancel_reservation_not_found(self):
        """Test cancelling a non-existent reservation returns False."""
        result = Reservation.cancel_reservation("NONEXISTENT")
        self.assertFalse(result)

    # --- display_reservation ---

    def test_display_reservation_success(self):
        """Test display returns correct Reservation object."""
        res = Reservation.create_reservation("C1", "H1", "2025-01-01", "2025-01-05")
        displayed = Reservation.display_reservation(res.reservation_id)
        self.assertIsNotNone(displayed)
        self.assertEqual(displayed.customer_id, "C1")

    def test_display_reservation_not_found(self):
        """Test displaying a non-existent reservation returns None."""
        result = Reservation.display_reservation("NONEXISTENT")
        self.assertIsNone(result)

    # --- invalid file handling ---

    def test_load_reservations_invalid_json(self):
        """Test loading corrupted JSON file returns empty dict."""
        os.makedirs("data", exist_ok=True)
        with open(RESERVATIONS_FILE, "w", encoding="utf-8") as f:
            f.write("BAD JSON {{{")
        reservations = _load_reservations()
        self.assertEqual(reservations, {})

    def test_load_reservations_invalid_format(self):
        """Test loading JSON with wrong format returns empty dict."""
        os.makedirs("data", exist_ok=True)
        with open(RESERVATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(["not", "a", "dict"], f)
        reservations = _load_reservations()
        self.assertEqual(reservations, {})

    def test_save_reservations_creates_directory(self):
        """Test save creates data directory if missing."""
        if os.path.exists("data"):
            shutil.rmtree("data")
        os.makedirs("data", exist_ok=True)
        # Recreate required files after rmtree
        Hotel.create_hotel("H1", "Grand", "NYC", 5)
        Customer.create_customer("C1", "Alice", "alice@mail.com", "123")
        data = {"R1": {"reservation_id": "R1", "customer_id": "C1",
                       "hotel_id": "H1", "check_in": "2025-01-01",
                       "check_out": "2025-01-05"}}
        _save_reservations(data)
        self.assertTrue(os.path.exists(RESERVATIONS_FILE))


if __name__ == "__main__":
    unittest.main()
