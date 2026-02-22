"""Module for Reservation class with file persistence."""

import json
import os
import uuid
from hotel import Hotel

RESERVATIONS_FILE = "data/reservations.json"


def _load_reservations():
    """Load reservations from JSON file."""
    if not os.path.exists(RESERVATIONS_FILE):
        return {}
    try:
        with open(RESERVATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print(
                    "Error: reservations file "
                    "has invalid format. Starting fresh."
                )
                return {}
            return data
    except json.JSONDecodeError as e:
        print(f"Error reading reservations file: {e}. Starting fresh.")
        return {}
    except OSError as e:
        print(f"Error opening reservations file: {e}. Starting fresh.")
        return {}


def _save_reservations(reservations):
    """Save reservations dictionary to JSON file."""
    os.makedirs("data", exist_ok=True)
    try:
        with open(RESERVATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(reservations, f, indent=4)
    except OSError as e:
        print(f"Error saving reservations file: {e}")


def _load_customers():
    """Load customers from JSON file for validation."""
    customers_file = "data/customers.json"
    if not os.path.exists(customers_file):
        return {}
    try:
        with open(customers_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading customers file: {e}.")
        return {}


def _load_hotels():
    """Load hotels from JSON file for validation."""
    hotels_file = "data/hotels.json"
    if not os.path.exists(hotels_file):
        return {}
    try:
        with open(hotels_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading hotels file: {e}.")
        return {}


class Reservation:
    """Represents a reservation linking a customer and a hotel."""

    def __init__(self, reservation_id, customer_id, hotel_id,
                 check_in, check_out):
        """Initialize a Reservation instance."""
        self.reservation_id = reservation_id
        self.customer_id = customer_id
        self.hotel_id = hotel_id
        self.check_in = check_in
        self.check_out = check_out

    def to_dict(self):
        """Convert reservation to dictionary."""
        return {
            "reservation_id": self.reservation_id,
            "customer_id": self.customer_id,
            "hotel_id": self.hotel_id,
            "check_in": self.check_in,
            "check_out": self.check_out,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Reservation from a dictionary."""
        return cls(
            data["reservation_id"],
            data["customer_id"],
            data["hotel_id"],
            data["check_in"],
            data["check_out"],
        )

    @staticmethod
    def create_reservation(customer_id, hotel_id, check_in, check_out):
        """Create and persist a new reservation."""
        customers = _load_customers()
        if customer_id not in customers:
            print(f"Error: Customer '{customer_id}' not found.")
            return None

        hotels = _load_hotels()
        if hotel_id not in hotels:
            print(f"Error: Hotel '{hotel_id}' not found.")
            return None

        if not Hotel.reserve_room(hotel_id):
            return None

        reservation_id = str(uuid.uuid4())[:8]
        reservation = Reservation(
            reservation_id, customer_id, hotel_id, check_in, check_out
        )
        reservations = _load_reservations()
        reservations[reservation_id] = reservation.to_dict()
        _save_reservations(reservations)
        print(
            f"Reservation '{reservation_id}' created: "
            f"Customer '{customer_id}' at Hotel '{hotel_id}'."
        )
        return reservation

    @staticmethod
    def cancel_reservation(reservation_id):
        """Cancel an existing reservation."""
        reservations = _load_reservations()
        if reservation_id not in reservations:
            print(f"Error: Reservation '{reservation_id}' not found.")
            return False

        hotel_id = reservations[reservation_id]["hotel_id"]
        Hotel.cancel_room(hotel_id)

        del reservations[reservation_id]
        _save_reservations(reservations)
        print(f"Reservation '{reservation_id}' cancelled successfully.")
        return True

    @staticmethod
    def display_reservation(reservation_id):
        """Display reservation information."""
        reservations = _load_reservations()
        if reservation_id not in reservations:
            print(f"Error: Reservation '{reservation_id}' not found.")
            return None
        data = reservations[reservation_id]
        print("--- Reservation Info ---")
        print(f"Reservation ID : {data['reservation_id']}")
        print(f"Customer ID    : {data['customer_id']}")
        print(f"Hotel ID       : {data['hotel_id']}")
        print(f"Check-in       : {data['check_in']}")
        print(f"Check-out      : {data['check_out']}")
        return Reservation.from_dict(data)
