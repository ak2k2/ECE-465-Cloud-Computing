# ray-server.py
import logging
import subprocess
import time

import ray

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

subprocess.run(["ray", "stop"])

# specify your desired port
port = "6379"

# Start the Ray head node with the subprocess module
subprocess.run(
    [
        "ray",
        "start",
        "--head",
        "--node-ip-address=0.0.0.0",
        f"--port={port}",
        "--verbose",
    ]
)


def main():
    ray.init(address=f"ray://0.0.0.0:{port}")

    logger.info("Ray Server Started...")
    while True:
        logger.info("♥")
        time.sleep(60)


if __name__ == "__main__":
    main()
