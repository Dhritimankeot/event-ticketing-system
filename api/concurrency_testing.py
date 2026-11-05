
import requests
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

URL = "http://127.0.0.1:8000/bookings"

EVENT_ID = 2
SEAT_ID = 4

barrier = Barrier(2)


def book_seat(user_id):

    payload = {
        "user_id": user_id,
        "event_id": EVENT_ID,
        "seat_ids": [SEAT_ID]
    }

    barrier.wait()

    response = requests.post(URL, json=payload)

    return {
        "user_id": user_id,
        "status_code": response.status_code,
        "response": response.json()
    }


with ThreadPoolExecutor(max_workers=2) as executor:

    results = list(
        executor.map(book_seat, [1, 2])
    )


for result in results:

    print(f"\nUser: {result['user_id']}")
    print(f"Status code: {result['status_code']}")
    print(f"Response: {result['response']}")
