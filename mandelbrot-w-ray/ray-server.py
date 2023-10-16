import logging
import time

import ray

# Setup basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    # Initialize Ray
    try:
        # Try to start the Ray server
        ray.init(address="0.0.0.0:6379")
        logging.info("Ray server started successfully.")
    except Exception as e:
        logging.error("Could not start Ray server: {}".format(e))

    print("Ray Server Started...")
    while True:
        print("♥")
        time.sleep(60)


if __name__ == "__main__":
    main()
