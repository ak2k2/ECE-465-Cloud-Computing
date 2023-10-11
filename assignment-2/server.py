import asyncio
import os
from asyncio import StreamReader, StreamWriter
import logging
import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_DIRECTORY = "server-files"
CHUNK_SIZE = 8192  # 8KB


async def send_in_chunks(writer, data):
    for i in range(0, len(data), CHUNK_SIZE):
        writer.write(data[i : i + CHUNK_SIZE])
        await writer.drain()


async def read_exactly(reader, num_bytes):
    received_data = bytearray()
    while len(received_data) < num_bytes:
        chunk = await reader.read(min(num_bytes - len(received_data), CHUNK_SIZE))
        if not chunk:
            break
        received_data.extend(chunk)
    return bytes(received_data)


async def handle_client(reader: StreamReader, writer: StreamWriter):
    client_addr = writer.get_extra_info("peername")
    logger.info(f"Connected to client: {client_addr}")

    while True:
        data = await reader.readline()
        if not data:
            break

        command, *args = data.decode().split()

        if command == "DOWNLOAD":
            filename = args[0]
            filepath = os.path.join(SERVER_DIRECTORY, filename)
            if not os.path.exists(filepath):
                writer.write(b"ERROR File not found\n")
                await writer.drain()
                logger.warning(f"File not found: {filename} requested by {client_addr}")
            else:
                with open(filepath, "rb") as f:
                    content = f.read()
                writer.write(f"{len(content)}\n".encode())
                await send_in_chunks(writer, content)
                logger.info(f"Sent file {filename} to {client_addr}")

        elif command == "UPLOAD":
            filename = args[0]
            filepath = os.path.join(SERVER_DIRECTORY, filename)
            data_size = int(await reader.readline())
            data = await read_exactly(reader, data_size)
            with open(filepath, "wb") as f:
                f.write(data)
            writer.write(b"OK File saved\n")
            await writer.drain()
            logger.info(f"Received and saved file {filename} from {client_addr}")

        elif command == "PROCESS":
            filename = args[0]
            filepath = os.path.join(SERVER_DIRECTORY, filename)
            if not os.path.exists(filepath):
                writer.write(b"ERROR File not found\n")
                await writer.drain()
                logger.warning(f"File not found: {filename} requested by {client_addr}")
            else:
                # Read the image using OpenCV
                img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

                # Apply histogram equalization
                equ = cv2.equalizeHist(img)

                # Convert the equalized image to bytes
                _, img_encoded = cv2.imencode(".png", equ)
                img_bytes = img_encoded.tobytes()

                writer.write(f"{len(img_bytes)}\n".encode())
                await send_in_chunks(writer, img_bytes)
                logger.info(f"Sent processed file {filename} to {client_addr}")

        elif command == "HEQ":
            filename = args[0]
            data_size = int(await reader.readline())
            data = await read_exactly(reader, data_size)

            # Use a temporary path to save the uploaded image for processing
            temp_filepath = os.path.join(SERVER_DIRECTORY, f"temp_{filename}")
            with open(temp_filepath, "wb") as f:
                f.write(data)

            # Read the image using OpenCV
            img = cv2.imread(temp_filepath, cv2.IMREAD_GRAYSCALE)

            # Apply histogram equalization
            equ = cv2.equalizeHist(img)

            # Convert the equalized image to bytes
            _, img_encoded = cv2.imencode(".png", equ)
            img_bytes = img_encoded.tobytes()

            writer.write(f"{len(img_bytes)}\n".encode())
            await send_in_chunks(writer, img_bytes)
            logger.info(
                f"Received, processed, and sent file {filename} from/to {client_addr}"
            )

            # Remove the temp file after processing
            os.remove(temp_filepath)

        elif command == "EXIT":
            writer.write(b"OK Bye\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            logger.info(f"Client {client_addr} closed connection")


async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8888)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
