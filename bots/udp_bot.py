#!/usr/bin/env python3

import argparse
import socket
import time


MAX_RATE = 200


def udp_traffic(target, port, rate, packet_size, duration):

    rate = min(rate, MAX_RATE)

    interval = 1.0 / rate

    payload = b"A" * packet_size

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    end_time = time.time() + duration

    sent = 0

    print("[UDP] Starting UDP traffic")
    print(f"[UDP] Target: {target}:{port}")
    print(f"[UDP] Rate: {rate} packets/sec")
    print(f"[UDP] Packet size: {packet_size} bytes")
    print(f"[UDP] Duration: {duration}s")

    while time.time() < end_time:

        start = time.time()

        try:
            sock.sendto(
                payload,
                (target, port)
            )

            sent += 1

        except Exception as e:
            print(f"[UDP] Error: {e}")

        elapsed = time.time() - start

        sleep_time = interval - elapsed

        if sleep_time > 0:
            time.sleep(sleep_time)

    sock.close()

    print(f"[UDP] Completed: {sent} packets")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--target",
        default="10.0.0.100"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=9999
    )

    parser.add_argument(
        "--rate",
        type=int,
        default=50
    )

    parser.add_argument(
        "--size",
        type=int,
        default=512
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=60
    )

    args = parser.parse_args()

    udp_traffic(
        args.target,
        args.port,
        args.rate,
        args.size,
        args.duration
    )


if __name__ == "__main__":
    main()