"""Unit tests for Hotel class."""

import json
import os
import unittest
import shutil
from hotel import Hotel, _load_hotels, _save_hotels, HOTELS_FILE


class TestHotel(unittest.TestCase):
    """Test cases for Hotel class."""

    def setUp(self):
        """Set up test environment with a fresh data directory."""
        os.makedirs("data", exist_ok=True)
        if os.path.exists(HOTELS_FILE):
            os.remove(HOTELS_FILE)

    def tearDown(self):
        """Clean up test data files."""
        if os.path.exists(HOTELS_FILE):
            os.remove(HOTELS_FILE)

    # --- to_dict / from_dict ---

    def test_to_dict(self):
        """Test Hotel to_dict returns correct structure."""
        hotel = Hotel("H1", "Grand", "NYC", 10)
        d = hotel.to_dict()
        self.assertEqual(d["hotel_id"], "H1")
        self.assertEqual(d["name"], "Grand")
        self.assertEqual(d["total_rooms"], 10)

    def test_from_dict(self):
        """Test Hotel from_dict creates correct instance."""
        data = {
            "hotel_id": "H2",
            "name": "Plaza",
            "location": "LA",
            "total_rooms": 5,
            "available_rooms": 3,
        }
        hotel = Hotel.from_dict(data)
        self.assertEqual(hotel.hotel_id, "H2")
        self.assertEqual(hotel.available_rooms, 3)

    def test_from_dict_missing_available_rooms(self):
        """Test from_dict defaults available_rooms to total_rooms."""
        data = {
            "hotel_id": "H3",
            "name": "Inn",
            "location": "TX",
            "total_rooms": 8,
        }
        hotel = Hotel.from_dict(data)
        self.assertEqual(hotel.available_rooms, 8)

    # --- create_hotel ---

    def test_create_hotel_success(self):
        """Test successful hotel creation."""
        hotel = Hotel.create_hotel("H1", "Grand", "NYC", 10)
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.name, "Grand")

    def test_create_hotel_duplicate(self):
        """Test creating a hotel with duplicate ID returns None."""
        Hotel.create_hotel("H1", "Grand", "NYC", 10)
        result = Hotel.create_hotel("H1", "Another", "LA", 5)
        self.assertIsNone(result)

    # --- delete_hotel ---

    def test_delete_hotel_success(self):
        """Test successful hotel deletion."""
        Hotel.create_hotel("H1", "Grand", "NYC", 10)
        result = Hotel.delete_hotel("H1")
        self.assertTrue(result)
        hotels = _load_hotels()
        self.assertNotIn("H1", hotels)

    def test_delete_hotel_not_found(self):
        """Test deleting a non-existent hotel returns False."""
        result = Hotel.delete_hotel("NONEXISTENT")
        self.assertFalse(result)

    # --- display_hotel ---

    def test_display_hotel_success(self):
        """Test display returns correct Hotel object."""
        Hotel.create_hotel("H1", "Grand", "NYC", 10)
        hotel = Hotel.display_hotel("H1")
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.name, "Grand")

    def test_display_hotel_not_found(self):
        """Test displaying a non-existent hotel returns None."""
        result = Hotel.display_hotel("NONEXISTENT")
        self.assertIsNone(result)

    # --- modify_hotel ---

    def test_modify_hotel_name(self):
        """Test modifying hotel name."""
        Hotel.create_hotel("H1", "Grand", "NYC", 10)
        result = Hotel.modify_hotel("H1", name="New Grand")
        self.assertTrue(result)
        hotels = _load_hotels()
        self.assertEqual(hotels["H1"]["name"], "New Grand")

    def test_modify_hotel_total_rooms(self):
        """Test modifying total rooms adjusts available rooms."""
        Hotel.create_hotel("H1", "Grand", "NYC", 10)
        Hotel.modify_hotel("H1", total_rooms=15)
        hotels = _load_hotels()
        self.assertEqual(hotels["H1"]["total_rooms"], 15)
        self.assertEqual(hotels["H1"]["available_rooms"], 15)

    def test_modify_hotel_not_found(self):
        """Test modifying a non-existent hotel returns False."""
        result = Hotel.modify_hotel("NONEXISTENT", name="Ghost")
        self.assertFalse(result)

    # --- reserve_room ---

    def test_reserve_room_success(self):
        """Test successful room reservation decreases available rooms."""
        Hotel.create_hotel("H1", "Grand", "NYC", 5)
        result = Hotel.reserve_room("H1")
        self.assertTrue(result)
        hotels = _load_hotels()
        self.assertEqual(hotels["H1"]["available_rooms"], 4)

    def test_reserve_room_no_availability(self):
        """Test reserving when no rooms are available returns False."""
        Hotel.create_hotel("H1", "Tiny", "NYC", 1)
        Hotel.reserve_room("H1")
        result = Hotel.reserve_room("H1")
        self.assertFalse(result)

    def test_reserve_room_hotel_not_found(self):
        """Test reserving a room in non-existent hotel returns False."""
        result = Hotel.reserve_room("NONEXISTENT")
        self.assertFalse(result)

    # --- cancel_room ---

    def test_cancel_room_success(self):
        """Test cancelling a room increases available rooms."""
        Hotel.create_hotel("H1", "Grand", "NYC", 5)
        Hotel.reserve_room("H1")
        result = Hotel.cancel_room("H1")
        self.assertTrue(result)
        hotels = _load_hotels()
        self.assertEqual(hotels["H1"]["available_rooms"], 5)

    def test_cancel_room_all_available(self):
        """Test cancelling when all rooms available returns False."""
        Hotel.create_hotel("H1", "Grand", "NYC", 5)
        result = Hotel.cancel_room("H1")
        self.assertFalse(result)

    def test_cancel_room_hotel_not_found(self):
        """Test cancelling a room in non-existent hotel returns False."""
        result = Hotel.cancel_room("NONEXISTENT")
        self.assertFalse(result)

    # --- invalid file handling ---

    def test_load_hotels_invalid_json(self):
        """Test loading corrupted JSON file returns empty dict."""
        os.makedirs("data", exist_ok=True)
        with open(HOTELS_FILE, "w", encoding="utf-8") as f:
            f.write("NOT VALID JSON {{")
        hotels = _load_hotels()
        self.assertEqual(hotels, {})

    def test_load_hotels_invalid_format(self):
        """Test loading a JSON file with wrong format returns empty dict."""
        os.makedirs("data", exist_ok=True)
        with open(HOTELS_FILE, "w", encoding="utf-8") as f:
            json.dump(["list", "not", "dict"], f)
        hotels = _load_hotels()
        self.assertEqual(hotels, {})

    def test_save_hotels_creates_directory(self):
        """Test save creates data directory if missing."""
        if os.path.exists("data"):
            shutil.rmtree("data")
        hotels = {
            "H1": {"hotel_id": "H1", "name": "Test", "location": "X",
                   "total_rooms": 1, "available_rooms": 1}
        }
        _save_hotels(hotels)
        self.assertTrue(os.path.exists(HOTELS_FILE))


if __name__ == "__main__":
    unittest.main()
