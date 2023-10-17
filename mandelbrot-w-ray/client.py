import socket
import json
from concurrent.futures import ThreadPoolExecutor


def receive_video(s):
    with open("clients-stuff/received_video.mp4", "wb") as f:
        while True:
            video_data = s.recv(1024)
            if not video_data:
                break
            f.write(video_data)


def send_request(request_json):
    HOST = "127.0.0.1"
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(request_json.encode("utf-8"))

        # Now, receive the video file back from the server
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(receive_video, s)
            return future.result()


if __name__ == "__main__":
    request_json = """
    {   
        "point": "-1.338238635,-0.057237059",
        "num_frames": 50,
        "frame_width": 1000,
        "frame_height": 1000,
        "maxiter": 1000,
        "fps": 20,
        "start_delta": 2.5,
        "end_delta": 0.0001
    }
    """
    send_request(request_json.strip())
    print("Video received!")
