
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from sqlalchemy import text, bindparam
from sqlalchemy.exc import IntegrityError

from database import engine


app = FastAPI(title="Event Ticketing API")


SECTION_PRICES = {
    "gold": 1200,
    "silver": 800,
}


# PYDANTIC REQUEST MODEL

class BookingRequest(BaseModel):

    user_id: int = Field(gt=0)

    event_id: int = Field(gt=0)

    seat_ids: list[int] = Field(min_length=1)


@app.get("/")
def home():

    return {
        "message": "Event Ticketing API is running"
    }


# GET ALL EVENTS

@app.get("/events")
def get_events():

    query = text("""
        SELECT
            event_id,
            event_name,
            venue_id,
            event_date
        FROM events
        ORDER BY event_date;
    """)

    with engine.connect() as connection:

        result = connection.execute(query)

        events = [
            dict(row._mapping)
            for row in result
        ]

    return events


# GET SEATS FOR AN EVENT

@app.get("/events/{event_id}/seats")
def get_event_seats(event_id: int):

    query = text("""
        WITH event_venue AS (

            SELECT event_id, venue_id
            FROM events
            WHERE event_id = :event_id

        ),

        seat_status AS (

            SELECT
                s.seat_id,
                s.seat_number,
                s.section,

                CASE
                    WHEN ar.seat_id IS NULL
                    THEN 'available'
                    ELSE 'booked'
                END AS status

            FROM event_venue ev

            JOIN seats s
                ON s.venue_id = ev.venue_id

            LEFT JOIN active_reservations ar
                ON ar.event_id = ev.event_id
                AND ar.seat_id = s.seat_id

        )

        SELECT *
        FROM seat_status
        ORDER BY seat_number;
    """)

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {"event_id": event_id}
        )

        seats = [
            dict(row._mapping)
            for row in result
        ]

        if not seats:

            event = connection.execute(
                text("""
                    SELECT event_id
                    FROM events
                    WHERE event_id = :event_id
                """),
                {"event_id": event_id}
            ).first()

            if event is None:
                raise HTTPException(
                    status_code=404,
                    detail="Event not found"
                )

    return seats

# CREATE BOOKINGS


@app.post("/bookings", status_code=201)
def create_booking(request: BookingRequest):

    if len(request.seat_ids) != len(set(request.seat_ids)):

        raise HTTPException(
            status_code=400,
            detail="Duplicate seat IDs are not allowed"
        )

    if any(seat_id <= 0 for seat_id in request.seat_ids):

        raise HTTPException(
            status_code=400,
            detail="Seat IDs must be positive"
        )

    try:

        with engine.begin() as connection:

            # Check if user exists

            user = connection.execute(
                text("""
                    SELECT user_id
                    FROM users
                    WHERE user_id = :user_id
                """),
                {"user_id": request.user_id}
            ).first()

            if user is None:

                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )


# Retrieve event and venue

            event = connection.execute(
                text("""
                    SELECT event_id, venue_id
                    FROM events
                    WHERE event_id = :event_id
                """),
                {"event_id": request.event_id}
            ).mappings().first()

            if event is None:

                raise HTTPException(
                    status_code=404,
                    detail="Event not found"
                )

            venue_id = event["venue_id"]

            seat_query = text("""
                SELECT
                    seat_id,
                    seat_number,
                    section

                FROM seats

                WHERE venue_id = :venue_id
                AND seat_id IN :seat_ids

                ORDER BY seat_id;
            """).bindparams(
                bindparam("seat_ids", expanding=True)
            )

            selected_seats = connection.execute(
                seat_query,
                {
                    "venue_id": venue_id,
                    "seat_ids": request.seat_ids
                }
            ).mappings().all()

            if len(selected_seats) != len(request.seat_ids):

                raise HTTPException(
                    status_code=400,
                    detail="One or more seats do not belong to this event's venue"
                )

            availability_query = text("""
                SELECT seat_id

                FROM active_reservations

                WHERE event_id = :event_id
                AND seat_id IN :seat_ids;
            """).bindparams(
                bindparam("seat_ids", expanding=True)
            )

            occupied_seats = connection.execute(
                availability_query,
                {
                    "event_id": request.event_id,
                    "seat_ids": request.seat_ids
                }
            ).scalars().all()

            if occupied_seats:

                raise HTTPException(
                    status_code=409,
                    detail={
                        "message": "Some selected seats are already booked",
                        "occupied_seat_ids": occupied_seats
                    }
                )

            booking_seat_records = []

            total_amount = 0

            for seat in selected_seats:

                section = seat["section"].strip().lower()

                if section not in SECTION_PRICES:

                    raise HTTPException(
                        status_code=400,
                        detail=f"No pricing configured for section: {
                            seat['section']}"
                    )

                price = SECTION_PRICES[section]

                total_amount += price

                booking_seat_records.append({

                    "seat_id": seat["seat_id"],
                    "price": price

                })

            booking_result = connection.execute(
                text("""
                    INSERT INTO bookings
                    (user_id, event_id, status)

                    VALUES
                    (:user_id, :event_id, 'confirmed')

                    RETURNING booking_id;
                """),
                {
                    "user_id": request.user_id,
                    "event_id": request.event_id
                }
            )

            booking_id = booking_result.scalar_one()

            booking_seat_query = text("""
                INSERT INTO booking_seats
                (booking_id, seat_id, price)

                VALUES
                (:booking_id, :seat_id, :price);
            """)

            booking_seat_data = [

                {
                    "booking_id": booking_id,
                    "seat_id": record["seat_id"],
                    "price": record["price"]
                }

                for record in booking_seat_records

            ]

            connection.execute(
                booking_seat_query,
                booking_seat_data
            )

            reservation_query = text("""
                INSERT INTO active_reservations
                (event_id, seat_id, booking_id, venue_id)

                VALUES
                (:event_id, :seat_id, :booking_id, :venue_id);
            """)

            reservation_data = [

                {
                    "event_id": request.event_id,
                    "seat_id": record["seat_id"],
                    "booking_id": booking_id,
                    "venue_id": venue_id
                }

                for record in booking_seat_records

            ]

            connection.execute(
                reservation_query,
                reservation_data
            )

        return {

            "message": "Booking created successfully",

            "booking_id": booking_id,

            "user_id": request.user_id,

            "event_id": request.event_id,

            "seats": booking_seat_records,

            "total_amount": total_amount,

            "status": "confirmed"

        }

    except IntegrityError:

        raise HTTPException(
            status_code=409,
            detail="Booking could not be completed because of a database constraint conflict"
        )

# GET BOOKING DETAILS


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: int):

    query = text("""
        WITH booking_summary AS (

            SELECT
                booking_id,
                COUNT(seat_id) AS total_seats,
                SUM(price) AS total_amount

            FROM booking_seats

            WHERE booking_id = :booking_id

            GROUP BY booking_id

        )

        SELECT
            b.booking_id,
            b.user_id,
            b.event_id,
            b.booking_time,
            b.status,

            COALESCE(bs.total_seats, 0) AS total_seats,
            COALESCE(bs.total_amount, 0) AS total_amount

        FROM bookings b

        LEFT JOIN booking_summary bs
            ON b.booking_id = bs.booking_id

        WHERE b.booking_id = :booking_id;
    """)

    seat_query = text("""
        SELECT
            bs.seat_id,
            s.seat_number,
            s.section,
            bs.price

        FROM booking_seats bs

        JOIN seats s
            ON bs.seat_id = s.seat_id

        WHERE bs.booking_id = :booking_id

        ORDER BY bs.seat_id;
    """)

    with engine.connect() as connection:

        booking = connection.execute(
            query,
            {"booking_id": booking_id}
        ).mappings().first()

        if booking is None:

            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        result = connection.execute(
            seat_query,
            {"booking_id": booking_id}
        )

        seats = [
            dict(row._mapping)
            for row in result
        ]

    return {
        "booking": dict(booking),
        "seats": seats
    }

# CANCEL BOOKINGS


@app.patch("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int):

    with engine.begin() as connection:

        # Lock booking row while cancellation is processed

        booking = connection.execute(
            text("""
                SELECT booking_id, status

                FROM bookings

                WHERE booking_id = :booking_id

                FOR UPDATE;
            """),
            {"booking_id": booking_id}
        ).mappings().first()

        if booking is None:

            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        if booking["status"] == "cancelled":

            return {
                "message": "Booking is already cancelled",
                "booking_id": booking_id
            }

        # Update booking status

        connection.execute(
            text("""
                UPDATE bookings

                SET status = 'cancelled'

                WHERE booking_id = :booking_id;
            """),
            {"booking_id": booking_id}
        )

        # Release reserved seats

        connection.execute(
            text("""
                DELETE FROM active_reservations

                WHERE booking_id = :booking_id;
            """),
            {"booking_id": booking_id}
        )

    return {

        "message": "Booking cancelled successfully",

        "booking_id": booking_id,

        "status": "cancelled"

    }


@app.get("/analytics/events/revenue")
def get_event_revenue():

    query = text("""
        WITH event_revenue AS (

            SELECT
                e.event_id,
                e.event_name,

                COALESCE(
                    SUM(bs.price) FILTER (
                        WHERE b.status = 'confirmed'
                    ),
                    0
                ) AS total_revenue,

                COUNT(DISTINCT b.booking_id) FILTER (
                    WHERE b.status = 'confirmed'
                ) AS total_bookings

            FROM events e

            LEFT JOIN bookings b
                ON e.event_id = b.event_id

            LEFT JOIN booking_seats bs
                ON b.booking_id = bs.booking_id

            GROUP BY
                e.event_id,
                e.event_name

        ),

        ranked_events AS (

            SELECT
                event_id,
                event_name,
                total_revenue,
                total_bookings,

                RANK() OVER (
                    ORDER BY total_revenue DESC
                ) AS revenue_rank

            FROM event_revenue

        )

        SELECT *
        FROM ranked_events
        ORDER BY revenue_rank, event_id;
    """)

    with engine.connect() as connection:

        result = connection.execute(query)

        events = [
            dict(row._mapping)
            for row in result
        ]

    return events
