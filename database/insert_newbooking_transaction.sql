BEGIN;

-- Insert a new booking and retrieve its generated booking_id
WITH new_booking AS (
    INSERT INTO bookings(user_id, event_id, status)
    VALUES (3, 3, 'pending')
    RETURNING booking_id
)

-- Insert two seats using the generated booking_id
INSERT INTO booking_seats(booking_id, seat_id, price)
SELECT booking_id, seat_id, 500
FROM new_booking
CROSS JOIN (VALUES (6), (7)) AS seats(seat_id);

SELECT * FROM bookings;

SELECT * FROM booking_seats;

UPDATE bookings
SET status = 'confirmed'
WHERE booking_id = 6;

COMMIT;