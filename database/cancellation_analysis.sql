SELECT
    COUNT(*) AS total_bookings,
    COUNT(*) FILTER (
        WHERE status = 'cancelled'
    ) AS cancelled_bookings,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE status = 'cancelled'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS cancellation_percentage
FROM bookings;