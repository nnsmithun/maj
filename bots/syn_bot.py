#!/usr/bin/env python3

import argparse
import ipaddress
import random
import time

from scapy.all import IP, TCP, send


LAB_NETWORK = ipaddress.ip_network("10.0.0.0/24")
MAX_RATE = 100


def validate_target(target):
    ip = ipaddress.ip_address(target)

    if ip not in LAB_NETWORK:
        raise ValueError(
            f"Target {target} is outside the Mininet lab network "
            f"{LAB_NETWORK}"
        )


def syn_traffic(target, port, rate, duration):

    validate_target(target)

    rate = min(rate, MAX_RATE)
    interval = 1.0 / rate

    end_time = time.time() + duration
    sent = 0

    print("[SYN] Starting controlled SYN traffic")
    print(f"[SYN] Target     : {target}:{port}")
    print(f"[SYN] Rate       : {rate} SYN packets/sec")
    print(f"[SYN] Duration   : {duration} seconds")
    print("[SYN] Network    : 10.0.0.0/24")

    while time.time() < end_time:

        start = time.time()

        # Random source port makes each SYN a separate flow attempt.
        source_port = random.randint(1024, 65535)

        packet = (
            IP(dst=target) /
            TCP(
                sport=source_port,
                dport=port,
                flags="S"
            )
        )

        try:
            # send() transmits the packet without waiting for a reply.
            send(
                packet,
                verbose=False
            )

            sent += 1

        except Exception as e:
            print(f"[SYN] Error: {e}")
            break

        elapsed = time.time() - start
        sleep_time = interval - elapsed

        if sleep_time > 0:
            time.sleep(sleep_time)

    print(f"[SYN] Finished")
    print(f"[SYN] SYN packets sent: {sent}")


def main():

    parser = argparse.ArgumentParser(
        description="Controlled SYN traffic generator for Mininet"
    )

    parser.add_argument(
        "--target",
        default="10.0.0.100",
        help="Victim IP inside the Mininet lab"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Destination TCP port"
    )

    parser.add_argument(
        "--rate",
        type=int,
        default=10,
        help="SYN packets per second (maximum 100)"
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Duration in seconds"
    )

    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")

    if args.rate <= 0:
        parser.error("Rate must be greater than 0")

    if args.duration <= 0:
        parser.error("Duration must be greater than 0")

    try:
        syn_traffic(
            args.target,
            args.port,
            args.rate,
            args.duration
        )

    except ValueError as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()