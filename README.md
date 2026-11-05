# Event Ticketing System | PostgreSQL & FastAPI

A project exploring how an event ticketing system can manage events, seats, bookings, and cancellations using PostgreSQL and FastAPI.

I started this project to strengthen my SQL skills and understand how database concepts work in an actual application. What began as a database design exercise gradually developed into a working API with booking operations and mechanisms to prevent duplicate seat reservations.

## Project Overview

The system manages users, venues, events, seats, and bookings.

The main objective was to build a database-backed application where users can retrieve event and seat information, create bookings, and cancel existing reservations while maintaining data consistency.

Some of the key functionalities implemented include:

- Event and seat retrieval.
- Seat booking and cancellation.
- Booking status management.
- Revenue-related SQL queries.
- Database constraints for maintaining data integrity.
- Transaction management.
- Prevention of duplicate seat reservations.
- REST API integration using FastAPI.

## Technology Stack

| Technology | Purpose |
|---|---|
| PostgreSQL | Relational database management |
| Python | Application development |
| FastAPI | REST API development |
| SQLAlchemy | Database connectivity |
| Pydantic | Request data validation |
| python-dotenv | Environment variable management |
| pgAdmin 4 | Database administration and SQL execution |

## 1. Database Design

The database consists of seven tables designed to manage the different aspects of an event ticketing system.

| Table | Description |
|---|---|
| `users` | Stores user information |
| `venues` | Stores venue details |
| `seats` | Stores individual seats associated with venues |
| `events` | Stores event information and venue associations |
| `bookings` | Maintains booking records and their status |
| `booking_seats` | Associates bookings with the seats reserved |
| `active_reservations` | Tracks active seat reservations and helps prevent duplicate bookings |

Primary keys, foreign keys, unique constraints, and check constraints are used to maintain relational integrity.

### Entity Relationship Diagram

The following diagram represents the database structure and relationships between the seven tables.

![Database ER Diagram](docs/ER_event_ticketing.pgerd.png)

## 2. SQL Concepts Implemented

A major part of this project involved practising SQL through practical database operations and analytical queries.

The concepts covered include:

**Basic SQL**
- SELECT, WHERE, ORDER BY
- GROUP BY and HAVING
- Aggregate functions
- CASE statements

**Intermediate and Advanced SQL**
- INNER JOIN and LEFT JOIN
- Subqueries and correlated subqueries
- Common Table Expressions (CTEs)
- Window functions and ranking
- UNION and UNION ALL
- Conditional aggregation

**Database Management**
- INSERT, UPDATE and DELETE
- Primary and foreign keys
- UNIQUE and CHECK constraints
- Transactions
- COMMIT and ROLLBACK
- SAVEPOINT

I also worked on queries involving booking analysis, event revenue, cancellations, and seat availability.

## 3. FastAPI Integration

After developing the database and practising SQL operations, I integrated PostgreSQL with FastAPI to expose the booking functionality through REST endpoints.

### Available API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Home endpoint |
| GET | `/events` | Retrieve available events |
| GET | `/events/{event_id}/seats` | Retrieve seat availability |
| POST | `/bookings` | Create a booking |
| GET | `/bookings/{booking_id}` | Retrieve booking details |
| PATCH | `/bookings/{booking_id}/cancel` | Cancel a booking |
| GET | `/analytics/events/revenue` | Retrive Event Revenue With Rank |

### API Documentation

FastAPI automatically generates interactive API documentation through Swagger UI.

![Swagger UI](docs/Images/swagger_ui.png)

The documentation can be accessed locally at:

`http://127.0.0.1:8000/docs`

## 4. Transaction Management and Double-Booking Prevention

One of the important problems I explored during this project was concurrent seat booking.

Consider two users attempting to reserve the same seat at nearly the same time. Both requests may initially find the seat available.

Without appropriate database-level protection, this can lead to duplicate reservations.

To handle this, I implemented:

- Transactional booking operations.
- Database-level constraints to prevent duplicate active reservations.
- Foreign key relationships to maintain consistency.
- Booking and cancellation operations that update reservation records.

The `active_reservations` table plays an important role in tracking currently reserved seats.

This helped me understand why checking seat availability in application code alone is not sufficient when multiple requests can arrive simultaneously.

### Booking and API Testing

**Successful Booking**

![Successful Booking](docs/Images/booking_created_response.png)

**Duplicate Booking Prevention**

![Duplicate Booking](docs/Images/booking_conflict.png)

**Concurrent Booking Test**

![Concurrent Booking threadpoolexecuter](docs/Images/concurrent_transaction_test_threadppolexecutor.png)

![Concurrent Booking psql_two_sessions](docs/Images/concurrency_testing_psql.png)

## 5. Running the Project Locally

### Prerequisites

- Python
- PostgreSQL
- pgAdmin 4 (optional, for database administration)

### Step 1: Clone the repository

```bash
git clone https://github.com/Dhritimankeot/event-ticketing-system.git

cd event-ticketing-system
```

### Step 2: Create a virtual environment

```powershell
python -m venv .ticketingenv
```

Activate it on Windows:

```powershell
.ticketingenv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create the database

Create a PostgreSQL database named:

```sql
CREATE DATABASE event_ticketing_system;
```

Execute the SQL scripts provided in the `database/` directory to create the tables and insert the sample data.

### Step 5: Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/event_ticketing_system
```

Replace the username and password with your local PostgreSQL credentials.

### Step 6: Run the application

```bash
uvicorn api.main:app --reload
```

Open the Swagger documentation:

`http://127.0.0.1:8000/docs`

## 6. Key Learnings

Building this project helped me understand how SQL and database concepts translate into real application workflows.

Some of the key things I learned:

- Designing relational databases with appropriate keys and constraints.
- Writing complex SQL queries using joins, CTEs, and window functions.
- Using transactions to ensure consistency across multiple database operations.
- Understanding race conditions and concurrent database requests.
- Connecting PostgreSQL with Python applications using SQLAlchemy.
- Building REST APIs and validating requests using FastAPI and Pydantic.

## 7. Future Improvements

There are still several areas I would like to explore and improve:

- Implementing adjacent-seat allocation to minimize separation between people booking together.
- Adding automated API testing using Pytest.
- Improving query performance through indexing and query-plan analysis.
- Containerizing the application using Docker.
- Improving API error handling and documentation.

---

**Project Status:** Work in Progress

