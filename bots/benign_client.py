#!/usr/bin/env python3

import argparse
import random
import time
import urllib.request


def make_request(url, timeout=5):
    try:
        start = time.time()

        with urllib.request.urlopen(url, timeout=timeout) as response:
            response.read(1024)
            status = response.status

        elapsed = time.time() - start

        print(
            f"[BENIGN] {url} "
            f"status={status} "
            f"time={elapsed:.3f}s"
        )

    except Exception as e:
        print(f"[BENIGN] request failed: {e}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--target",
        default="10.0.0.100",
        help="Victim server IP"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Victim server port"
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Duration in seconds"
    )

    parser.add_argument(
        "--min-delay",
        type=float,
        default=2.0,
        help="Minimum delay between requests"
    )

    parser.add_argument(
        "--max-delay",
        type=float,
        default=8.0,
        help="Maximum delay between requests"
    )

    args = parser.parse_args()

    base = f"http://{args.target}:{args.port}"

    pages = [
        "/",
        "/about",
        "/contact",
    ]

    end_time = time.time() + args.duration

    print("[BENIGN] Starting legitimate traffic")
    print(f"[BENIGN] Target: {base}")
    print(f"[BENIGN] Duration: {args.duration}s")

    while time.time() < end_time:

        page = random.choice(pages)
        url = base + page

        make_request(url)

        delay = random.uniform(
            args.min_delay,
            args.max_delay
        )

        time.sleep(delay)

    print("[BENIGN] Finished")


if __name__ == "__main__":
    main()