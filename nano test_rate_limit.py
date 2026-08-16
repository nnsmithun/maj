#!/usr/bin/env python3

import sys
import time
import urllib.request
import urllib.error


TARGET = "http://10.0.0.100:3000/"
REQUESTS = 40


def main():

    print(f"Sending {REQUESTS} HTTP requests...")
    print()

    for i in range(1, REQUESTS + 1):

        try:
            request = urllib.request.Request(
                TARGET,
                method="GET"
            )

            start = time.time()

            with urllib.request.urlopen(
                request,
                timeout=5
            ) as response:

                status = response.status

            elapsed = time.time() - start

            print(
                f"Request {i:02d}: "
                f"HTTP {status} "
                f"({elapsed:.3f}s)"
            )

        except urllib.error.HTTPError as e:

            elapsed = time.time() - start

            print(
                f"Request {i:02d}: "
                f"HTTP {e.code} "
                f"({elapsed:.3f}s)"
            )

        except Exception as e:

            print(
                f"Request {i:02d}: "
                f"ERROR: {e}"
            )

    print()
    print("Test complete.")


if __name__ == "__main__":
    main()