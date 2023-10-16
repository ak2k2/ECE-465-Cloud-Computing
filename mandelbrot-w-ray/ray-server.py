# ray-server.py
import ray
import time


def main():
    # Initialize Ray with default options.
    # It will start the relevant servers and listen on all interfaces.
    ray.init(_redis_password="5241590000000000")

    # Print the Ray dashboard URL, which is useful for monitoring the Ray cluster.
    print(f"Dashboard URL: {ray.get_dashboard_url()}")

    print("Ray Server Started...")
    while True:
        print("♥")
        time.sleep(60)


if __name__ == "__main__":
    main()
