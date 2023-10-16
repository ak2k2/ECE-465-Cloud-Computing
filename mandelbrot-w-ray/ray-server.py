# ray-server.py
import ray
import time


def main():
    # Initialize Ray. No parameters means it starts in local mode but listens on all interfaces.
    ray.init(address="auto", _redis_password="5241590000000000")

    print(f"Dashboard URL: {ray.get_dashboard_url()}")

    print("Ray Server Started...")
    while True:
        print("♥")
        time.sleep(60)


if __name__ == "__main__":
    main()
