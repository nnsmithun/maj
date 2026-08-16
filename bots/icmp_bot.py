#!/usr/bin/env python3

import argparse
import subprocess
import time


def icmp_traffic(target, rate, duration):

    end_time = time.time() + duration

    interval = 1.0 / rate

    sent = 0

    print("[ICMP] Starting ICMP traffic")
    print(f"[ICMP] Target: {target}")
    print(f"[ICMP] Rate: {rate} packets/sec")
    print(f"[ICMP] Duration: {duration}s")

    while time.time() < end_time:

        start = time.time()

        try:

            subprocess.run(
                [
                    "ping",
                    "-c",
                    "1",
                    "-W",
                    "1",
                    target
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            sent += 1

        except Exception as e:
            print(f"[ICMP] Error: {e}")

        elapsed = time.time() - start

        sleep_time = interval - elapsed

        if sleep_time > 0:
            time.sleep(sleep_time)

    print(f"[ICMP] Completed: {sent} packets")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--target",
        default="10.0.0.100"
    )

    parser.add_argument(
        "--rate",
        type=int,
        default=5
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=60
    )

    args = parser.parse_args()

    icmp_traffic(
        args.target,
        args.rate,
        args.duration
    )


if __name__ == "__main__":
    main()