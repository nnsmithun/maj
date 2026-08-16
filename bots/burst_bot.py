#!/usr/bin/env python3

import argparse
import socket
import time


def burst(
    target,
    port,
    burst_rate,
    burst_duration,
    idle_duration,
    total_duration
):

    end_time = time.time() + total_duration

    print("[BURST] Starting")
    print(f"[BURST] Target: {target}:{port}")
    print(f"[BURST] Burst rate: {burst_rate}")
    print(f"[BURST] Burst duration: {burst_duration}s")
    print(f"[BURST] Idle duration: {idle_duration}s")

    while time.time() < end_time:

        # -------------------------
        # BURST
        # -------------------------

        print("[BURST] >>> burst")

        burst_end = min(
            time.time() + burst_duration,
            end_time
        )

        interval = 1.0 / burst_rate

        while time.time() < burst_end:

            start = time.time()

            try:

                sock = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )

                sock.settimeout(0.2)

                sock.connect_ex(
                    (target, port)
                )

                sock.close()

            except Exception:
                pass

            elapsed = time.time() - start

            sleep_time = interval - elapsed

            if sleep_time > 0:
                time.sleep(sleep_time)

        # -------------------------
        # IDLE
        # -------------------------

        print("[BURST] <<< idle")

        remaining = end_time - time.time()

        if remaining <= 0:
            break

        time.sleep(
            min(idle_duration, remaining)
        )

    print("[BURST] Finished")


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
        "--burst-rate",
        type=int,
        default=30
    )

    parser.add_argument(
        "--burst-duration",
        type=float,
        default=3
    )

    parser.add_argument(
        "--idle-duration",
        type=float,
        default=10
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=60
    )

    args = parser.parse_args()

    burst(
        args.target,
        args.port,
        args.burst_rate,
        args.burst_duration,
        args.idle_duration,
        args.duration
    )


if __name__ == "__main__":
    main()