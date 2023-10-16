import logging
import time

import ray

# Setup basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def start_ray():
    try:
        # Specify the address of the existing cluster here
        ray.init("ray://192.168.1.11:6379")
        logging.info("Connected to the existing Ray cluster.")
    except ConnectionError:
        logging.warning(
            "No existing Ray cluster found or connection failed. Trying to start a new cluster."
        )
        try:
            # Try to start a new Ray cluster
            ray.init(address="0.0.0.0:6379")
            logging.info("New Ray cluster started successfully.")
        except Exception as e:
            logging.error("Could not start Ray server: {}".format(e))


def main():
    start_ray()

    print("Ray Server Started...")
    while True:
        print("♥")
        time.sleep(60)


if __name__ == "__main__":
    main()
