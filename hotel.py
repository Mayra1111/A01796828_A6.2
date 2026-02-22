"""Module for Hotel class with file persistence."""

import json
import os

HOTELS_FILE = "data/hotels.json"


def _load_hotels():
    """Load hotels from JSON file."""
    if not os.path.exists(HOTELS_FILE):
        return {}
    try:
        with open(HOTELS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print("Error: hotels file has invalid format. Starting fresh.")
                return {}
            return data
    except json.JSONDecodeError as e:
        print(f"Error reading hotels file: {e}. Starting fresh.")
        return {}
    except OSError as e:
        print(f"Error opening hotels file: {e}. Starting fresh.")
        return {}


def _save_hotels(hotels):
    """Save hotels dictionary to JSON file."""
    os.makedirs("data", exist_ok=True)
    try:
        with open(HOTELS_FILE, "w", encoding="utf-8") as f:
            json.dump(hotels, f, indent=4)
    except OSError as e:
        print(f"Error saving hotels file: {e}")


class Hotel:
    """Represents a hotel with rooms and reservations."""

    def __init__(self, hotel_id, name, location, total_rooms):
        """Initialize a Hotel instance."""
        self.hotel_id = hotel_id
        self.name = name
        self.location = location
        self.total_rooms = total_rooms
        self.available_rooms = total_rooms

    def to_dict(self):
        """Convert hotel to dictionary."""
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "location": self.location,
            "total_rooms": self.total_rooms,
            "available_rooms": self.available_rooms,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Hotel from a dictionary."""
        hotel = cls(
            data["hotel_id"],
            data["name"],
            data["location"],
            data["total_rooms"],
        )
        hotel.available_rooms = data.get(
            "available_rooms", data["total_rooms"]
        )
        return hotel

    @staticmethod
    def create_hotel(hotel_id, name, location, total_rooms):
        """Create and persist a new hotel."""
        hotels = _load_hotels()
        if hotel_id in hotels:
            print(f"Error: Hotel with ID '{hotel_id}' already exists.")
            return None
        hotel = Hotel(hotel_id, name, location, total_rooms)
        hotels[hotel_id] = hotel.to_dict()
        _save_hotels(hotels)
        print(f"Hotel '{name}' created successfully.")
        return hotel

    @staticmethod
    def delete_hotel(hotel_id):
        """Delete a hotel by ID."""
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"Error: Hotel with ID '{hotel_id}' not found.")
            return False
        del hotels[hotel_id]
        _save_hotels(hotels)
        print(f"Hotel '{hotel_id}' deleted successfully.")
        return True

    @staticmethod
    def display_hotel(hotel_id):
        """Display hotel information."""
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"Error: Hotel with ID '{hotel_id}' not found.")
            return None
        data = hotels[hotel_id]
        print("--- Hotel Info ---")
        print(f"ID       : {data['hotel_id']}")
        print(f"Name     : {data['name']}")
        print(f"Location : {data['location']}")
        avail = data['available_rooms']
        total = data['total_rooms']
        print(f"Rooms    : {avail}/{total} available")
        return Hotel.from_dict(data)

    @staticmethod
    def modify_hotel(hotel_id, name=None, location=None, total_rooms=None):
        """Modify hotel attributes."""
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"Error: Hotel with ID '{hotel_id}' not found.")
            return False
        if name:
            hotels[hotel_id]["name"] = name
        if location:
            hotels[hotel_id]["location"] = location
        if total_rooms is not None:
            diff = total_rooms - hotels[hotel_id]["total_rooms"]
            hotels[hotel_id]["total_rooms"] = total_rooms
            hotels[hotel_id]["available_rooms"] = max(
                0, hotels[hotel_id]["available_rooms"] + diff
            )
        _save_hotels(hotels)
        print(f"Hotel '{hotel_id}' modified successfully.")
        return True

    @staticmethod
    def reserve_room(hotel_id):
        """Reserve a room in the hotel (decrease available rooms)."""
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"Error: Hotel with ID '{hotel_id}' not found.")
            return False
        if hotels[hotel_id]["available_rooms"] <= 0:
            print(f"Error: No available rooms in hotel '{hotel_id}'.")
            return False
        hotels[hotel_id]["available_rooms"] -= 1
        _save_hotels(hotels)
        return True

    @staticmethod
    def cancel_room(hotel_id):
        """Cancel a room reservation (increase available rooms)."""
        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"Error: Hotel with ID '{hotel_id}' not found.")
            return False
        avail = hotels[hotel_id]["available_rooms"]
        total = hotels[hotel_id]["total_rooms"]
        if avail >= total:
            print(
                f"Error: All rooms already available in hotel '{hotel_id}'."
            )
            return False
        hotels[hotel_id]["available_rooms"] += 1
        _save_hotels(hotels)
        return True
