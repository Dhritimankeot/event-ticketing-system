WITH event_revenue AS (
    SELECT
        e.event_id,
        e.event_name,
        SUM(bs.price) AS revenue
    FROM events e
    INNER JOIN bookings b
        ON e.event_id = b.event_id
    INNER JOIN booking_seats bs
        ON b.booking_id = bs.booking_id
    WHERE b.status = 'confirmed'
    GROUP BY e.event_id, e.event_name
)
SELECT *
FROM event_revenue
ORDER BY revenue DESC
LIMIT 1;