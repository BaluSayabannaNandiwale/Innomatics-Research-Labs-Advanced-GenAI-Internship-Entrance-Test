from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="Hotel Room Booking System")

# -----------------------------
# Sample Data
# -----------------------------

rooms = [
    {"id": 1, "room_type": "Single", "price": 1200, "available": True},
    {"id": 2, "room_type": "Double", "price": 2000, "available": True},
    {"id": 3, "room_type": "Suite", "price": 3500, "available": True},
    {"id": 4, "room_type": "Deluxe", "price": 2800, "available": True},
]

bookings = []

# -----------------------------
# Pydantic Models
# -----------------------------

class Room(BaseModel):
    room_type: str = Field(..., min_length=3)
    price: float = Field(..., gt=0)
    available: bool = True


class Booking(BaseModel):
    customer_name: str = Field(..., min_length=2)
    room_id: int
    days: int = Field(..., gt=0)


# -----------------------------
# Helper Functions
# -----------------------------

def find_room(room_id: int):
    for room in rooms:
        if room["id"] == room_id:
            return room
    return None


def find_booking(booking_id: int):
    for booking in bookings:
        if booking["id"] == booking_id:
            return booking
    return None


def calculate_total(price, days):
    return price * days


# -----------------------------
# DAY 1 – Basic GET APIs
# -----------------------------

@app.get("/")
def home():
    return {"message": "Welcome to Hotel Room Booking API"}


@app.get("/rooms")
def get_all_rooms():
    return rooms


@app.get("/rooms/{room_id}")
def get_room_by_id(room_id: int):
    room = find_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@app.get("/rooms/count")
def total_rooms():
    return {"total_rooms": len(rooms)}


@app.get("/rooms/available")
def available_rooms():
    return [room for room in rooms if room["available"]]


# -----------------------------
# DAY 2 – POST + Pydantic
# -----------------------------

@app.post("/rooms", status_code=status.HTTP_201_CREATED)
def add_room(room: Room):
    new_room = room.dict()
    new_room["id"] = len(rooms) + 1
    rooms.append(new_room)
    return {"message": "Room added successfully", "room": new_room}


@app.post("/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(booking: Booking):
    room = find_room(booking.room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if not room["available"]:
        raise HTTPException(status_code=400, detail="Room not available")

    total_price = calculate_total(room["price"], booking.days)

    new_booking = booking.dict()
    new_booking["id"] = len(bookings) + 1
    new_booking["total_price"] = total_price
    new_booking["status"] = "Booked"

    bookings.append(new_booking)

    room["available"] = False

    return {"message": "Room booked successfully", "booking": new_booking}


# -----------------------------
# DAY 3 – Query + Filtering
# -----------------------------

@app.get("/rooms/filter")
def filter_rooms(
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None)
):

    result = rooms

    if min_price is not None:
        result = [room for room in result if room["price"] >= min_price]

    if max_price is not None:
        result = [room for room in result if room["price"] <= max_price]

    return result


@app.get("/rooms/type")
def filter_by_type(room_type: str):
    return [room for room in rooms if room["room_type"].lower() == room_type.lower()]


@app.get("/bookings/summary")
def booking_summary():
    return {
        "total_bookings": len(bookings)
    }


# -----------------------------
# DAY 4 – CRUD
# -----------------------------

@app.put("/rooms/{room_id}")
def update_room(room_id: int, updated_room: Room):

    room = find_room(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.update(updated_room.dict())

    return {"message": "Room updated", "room": room}


@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):

    room = find_room(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    rooms.remove(room)

    return {"message": "Room deleted successfully"}


@app.put("/bookings/{booking_id}")
def update_booking(booking_id: int, booking: Booking):

    existing_booking = find_booking(booking_id)

    if not existing_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    existing_booking.update(booking.dict())

    return {"message": "Booking updated", "booking": existing_booking}


@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int):

    booking = find_booking(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    room = find_room(booking["room_id"])

    if room:
        room["available"] = True

    bookings.remove(booking)

    return {"message": "Booking cancelled"}


# -----------------------------
# DAY 5 – Multi Step Workflow
# -----------------------------

@app.post("/booking/create")
def workflow_booking(booking: Booking):

    room = find_room(booking.room_id)

    if not room or not room["available"]:
        raise HTTPException(status_code=400, detail="Room not available")

    new_booking = booking.dict()
    new_booking["id"] = len(bookings) + 1
    new_booking["status"] = "Booked"

    bookings.append(new_booking)
    room["available"] = False

    return {"message": "Booking created", "booking": new_booking}


@app.post("/booking/checkin/{booking_id}")
def checkin(booking_id: int):

    booking = find_booking(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking["status"] = "Checked-in"

    return {"message": "Customer checked in", "booking": booking}


@app.post("/booking/checkout/{booking_id}")
def checkout(booking_id: int):

    booking = find_booking(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    room = find_room(booking["room_id"])

    if room:
        room["available"] = True

    booking["status"] = "Checked-out"

    return {"message": "Customer checked out", "booking": booking}


# -----------------------------
# DAY 6 – Advanced APIs
# -----------------------------

@app.get("/rooms/search")
def search_rooms(keyword: str):

    return [
        room for room in rooms
        if keyword.lower() in room["room_type"].lower()
    ]


@app.get("/rooms/paginate")
def paginate_rooms(page: int = 1, limit: int = 2):

    start = (page - 1) * limit
    end = start + limit

    return rooms[start:end]


@app.get("/rooms/browse")
def browse_rooms(
    keyword: Optional[str] = None,
    sort: Optional[str] = None,
    page: int = 1,
    limit: int = 5
):

    result = rooms

    if keyword:
        result = [r for r in result if keyword.lower() in r["room_type"].lower()]

    if sort == "price":
        result = sorted(result, key=lambda x: x["price"])

    start = (page - 1) * limit
    end = start + limit

    return result[start:end]