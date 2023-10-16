# ray-server.py
import ray
import time


def main():
    # Initialize Ray
    ray.init(
        address="0.0.0.0:6379",
        _redis_password="5241590000000000",
        _node_ip_address="0.0.0.0",
    )

    print("Ray Server Started...")
    while True:
        print("♥")
        time.sleep(60)


if __name__ == "__main__":
    main()
