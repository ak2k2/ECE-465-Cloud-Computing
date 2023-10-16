# ray-server.py
import ray


def main():
    # Initialize Ray
    ray.init(address="auto")

    # The script should continue running to keep the Ray cluster alive
    print(f"Server ready: {ray.get_runtime_context().get()}")

    # Keep the script alive
    import time

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
