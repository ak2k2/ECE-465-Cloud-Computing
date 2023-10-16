# ray-server.py
import ray
import time


def main():
    # Initialize Ray with default options.
    # It will start the relevant servers and listen on all interfaces.
    ray.init(
        _redis_password="5241590000000000",
        dashboard_host="0.0.0.0",
    )

    print("Ray Server Started...")
    while True:
        print("♥")
        time.sleep(60)


if __name__ == "__main__":
    main()
