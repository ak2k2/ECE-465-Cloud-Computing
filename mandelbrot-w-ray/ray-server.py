# ray-server.py
import ray


def main():
    # Initialize Ray
    ray.init()

    # The script should continue running to keep the Ray cluster alive
    print(f"Server ready at {ray.get_runtime_context().get()}")
    # Keep the script alive
    import time

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
