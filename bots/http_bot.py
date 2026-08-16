#!/usr/bin/env python3

import argparse
import random
import time
import urllib.request


MAX_RATE = 50


def http_flood(target, port, rate, duration):

    rate = min(rate, MAX_RATE)

    interval = 1.0 / rate

    base = f"http://{target}:{port}"

    pages = [
        "/",
        "/about",
        "/contact"
    ]

    end_time = time.time() + duration

    requests = 0

    print("[HTTP] Starting HTTP traffic")
    print(f"[HTTP] Target: {base}")
    print(f"[HTTP] Rate: {rate} requests/sec")
    print(f"[HTTP] Duration: {duration}s")

    while time.time() < end_time:

        start = time.time()

        page = random.choice(pages)

        url = base + page

        try:

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "MAJOR-Research-Bot"
                }
            )

            with urllib.request.urlopen(
                request,
                timeout=2
            ) as response:

                response.read(512)

            requests += 1

        except Exception:
            pass

        elapsed = time.time() - start

        sleep_time = interval - elapsed

        if sleep_time > 0:
            time.sleep(sleep_time)

    print(f"[HTTP] Completed: {requests} requests")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--target",
        default="10.0.0.100"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=3000
    )

    parser.add_argument(
        "--rate",
        type=int,
        default=10
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=60
    )

    args = parser.parse_args()

    http_flood(
        args.target,
        args.port,
        args.rate,
        args.duration
    )


if __name__ == "__main__":
    main()