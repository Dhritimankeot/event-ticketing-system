SELECT
    e.event_name,
    SUM(bs.price) AS total_revenue
FROM events e
INNER JOIN bookings b
    ON e.event_id = b.event_id
INNER JOIN booking_seats bs
    ON b.booking_id = bs.booking_id
WHERE b.status = 'confirmed'
GROUP BY e.event_id, e.event_name
ORDER BY total_revenue DESC;