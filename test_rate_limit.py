#!/usr/bin/env python3

import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter


TARGET = "http://10.0.0.100:3000/"
TOTAL_REQUESTS = 40


def send_request(number):
    try:
        request = urllib.request.Request(
            TARGET,
            method="GET"
        )

        with urllib.request.urlopen(
            request,
            timeout=5
        ) as response:
            return number, response.status

    except urllib.error.HTTPError as e:
        return number, e.code

    except Exception as e:
        return number, f"ERROR: {e}"


def main():

    print(f"Sending {TOTAL_REQUESTS} requests concurrently...")
    print(f"Target: {TARGET}")
    print()

    results = []

    with ThreadPoolExecutor(
        max_workers=TOTAL_REQUESTS
    ) as executor:

        futures = [
            executor.submit(send_request, i)
            for i in range(1, TOTAL_REQUESTS + 1)
        ]

        for future in as_completed(futures):
            results.append(future.result())

    results.sort()

    counts = Counter(
        status for _, status in results
    )

    for number, status in results:
        print(
            f"Request {number:02d}: HTTP {status}"
        )

    print()
    print("========== SUMMARY ==========")

    for status, count in sorted(
        counts.items(),
        key=lambda x: str(x[0])
    ):
        print(f"HTTP {status}: {count}")

    print("==============================")


if __name__ == "__main__":
    main()