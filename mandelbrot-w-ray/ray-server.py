# ray-server.py
import ray
import time


def main():
    # Initialize Ray
    ray.init(
        address="auto",
        _node_ip_address="192.168.1.11",
        _redis_password="5241590000000000",
    )

    print("Ray Server started at 192.168.1.11:6379")
    while True:
        print("♥ ♥ ♥ ♥")
        time.sleep(60)


if __name__ == "__main__":
    main()
