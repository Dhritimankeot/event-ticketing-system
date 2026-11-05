INSERT INTO users (name, email_id)
VALUES ( 'Lipi Bora', 'lipi@gmail.com'), ('Dhritiman Keot','dk@gmail.com'), ('Rahul Sharma', 'rs@hotmail.com');

INSERT INTO venue (venue_name, venue_city) VALUES
('Judges Hall', 'Nagaon'), ('Sankardev kalakhetra', 'Guwahati');

INSERT INTO seats (venue_id, seat_number, section) VALUES
(1, 'A1', 'Gold'),(1, 'A2', 'Gold'),(1, 'A3', 'Gold'),(1, 'B1', 'Silver'),(1, 'B2', 'Silver'),(2, 'A1', 'Gold'),(2, 'A2', 'Gold');

INSERT INTO events (venue_id, event_name, event_date) VALUES
 (1, 'Music Night', '2026-12-10 18:00:00'),(1, 'Tech Conference', '2026-12-15 09:00:00'),(2, 'Comedy Show', '2026-12-20 19:00:00');

INSERT INTO bookings (user_id, event_id, status) VALUES
 (1, 1, 'confirmed'),(2, 1, 'confirmed'),(3, 2, 'cancelled');

INSERT INTO booking_seats (booking_id, seat_id, price) VALUES
 (1, 1, 1200.00),(1, 2, 1200.00),(2, 3, 1200.00),(3, 4, 800.00);