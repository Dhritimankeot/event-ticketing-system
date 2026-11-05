--users table--

CREATE TABLE users (
user_id BIGSERIAL PRIMARY KEY,
name VARCHAR(50) NOT NULL,
email_id VARCHAR(100) UNIQUE NOT NULL,
created_at TIMESTAMP NOT NULL DEFAULT NOW());

--venue--

 CREATE TABLE venue (
venue_id BIGSERIAL PRIMARY KEY,
venue_name VARCHAR(100) NOT NULL,
venue_city VARCHAR(50) NOT NULL);

--seats--

event_ticketing_system=# CREATE TABLE seats (
seat_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
venue_id INT NOT NULL references venue(venue_id),
seat_number VARCHAR(20) NOT NULL,
section VARCHAR(50),
UNIQUE (venue_id, seat_number));

--events--

CREATE TABLE events (
event_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
venue_id INT NOT NULL REFERENCES venue(venue_id),
event_name VARCHAR(150) NOT NULL,
event_date TIMESTAMP NOT NULL,
UNIQUE (event_id, venue_id));

--bookings--

 CREATE TABLE bookings (
booking_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 user_id INT NOT NULL REFERENCES users(user_id),
event_id INT NOT NULL REFERENCES events(event_id),
booking_time TIMESTAMP NOT NULL DEFAULT NOW(),
status VARCHAR(20) NOT NULL DEFAULT 'confirmed'
CHECK (status IN ('pending', 'confirmed', 'cancelled')));

--booking_seats--


event_ticketing_system=# CREATE TABLE booking_seats (
booking_id INT NOT NULL REFERENCES bookings(booking_id),
seat_id INT NOT NULL REFERENCES seats(seat_id),
 price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
PRIMARY KEY (booking_id, seat_id));