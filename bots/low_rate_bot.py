#!/usr/bin/env python3

import argparse
import socket
import time


def low_rate(target, port, interval, duration):

    end_time = time.time() + duration

    sent = 0

    print("[LOW_RATE] Starting")
    print(f"[LOW_RATE] Target: {target}:{port}")
    print(f"[LOW_RATE] Interval: {interval}s")
    print(f"[LOW_RATE] Duration: {duration}s")

    while time.time() < end_time:

        try:

            sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            sock.settimeout(1)

            sock.connect_ex(
                (target, port)
            )

            sock.close()

            sent += 1

        except Exception:
            pass

        time.sleep(interval)

    print(
        f"[LOW_RATE] Completed: {sent} attempts"
    )


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
        "--interval",
        type=float,
        default=2.0
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=300
    )

    args = parser.parse_args()

    low_rate(
        args.target,
        args.port,
        args.interval,
        args.duration
    )


if __name__ == "__main__":
    main()