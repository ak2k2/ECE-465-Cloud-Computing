import asyncio
import concurrent.futures


CHUNK_SIZE = 1024 * 4  # This can be adjusted based on your needs.


def write_chunk(writer, chunk):
    writer.write(chunk)


async def send_in_chunks(writer, data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = []
        for i in range(0, len(data), CHUNK_SIZE):
            chunk = data[i : i + CHUNK_SIZE]
            task = await asyncio.to_thread(executor.submit, write_chunk, writer, chunk)
            tasks.append(task)

        # Wait for all threads to complete
        for task in tasks:
            task.result()  # This raises any exceptions encountered.

        # After all the writes, drain the writer once to ensure all data has been sent.
        await writer.drain()


async def read_exactly(reader, num_bytes):
    received_data = bytearray()
    while len(received_data) < num_bytes:
        chunk = await reader.read(min(num_bytes - len(received_data), CHUNK_SIZE))
        if not chunk:
            break
        received_data.extend(chunk)
    return bytes(received_data)


async def send_request(command: str, filename: str):
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)

    if command == "DOWNLOAD":
        writer.write(f"DOWNLOAD {filename}\n".encode())
        data_size = int(await reader.readline())
        content = await read_exactly(reader, data_size)
        if content == b"ERROR File not found":
            print("File not found on the server.")
        else:
            with open(f"client-files/{filename}", "wb") as f:
                f.write(content)
            print("File downloaded successfully.")

    elif command == "UPLOAD":
        with open(f"client-files/{filename}", "rb") as f:
            content = f.read()
        writer.write(f"UPLOAD {filename}\n".encode())
        writer.write(f"{len(content)}\n".encode())
        await send_in_chunks(writer, content)
        response = await reader.readline()
        print(response.decode().strip())

    elif command == "PROCESS":
        writer.write(f"PROCESS {filename}\n".encode())
        data_size = int(await reader.readline())
        content = await read_exactly(reader, data_size)
        if content == b"ERROR File not found":
            print("File not found on the server.")
        else:
            with open(f"client-files/processed_{filename}", "wb") as f:
                f.write(content)
            print("Processed image downloaded successfully.")

    elif command == "HEQ":
        with open(f"client-files/{filename}", "rb") as f:
            content = f.read()
        writer.write(f"HEQ {filename}\n".encode())
        writer.write(f"{len(content)}\n".encode())
        await send_in_chunks(writer, content)
        data_size = int(await reader.readline())
        content = await read_exactly(reader, data_size)
        with open(f"client-files/processed_{filename}", "wb") as f:
            f.write(content)
        print("Processed image downloaded successfully.")

    elif command == "EXIT":
        writer.write(b"EXIT\n")
        response = await reader.readline()
        print(response.decode().strip())

    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    command = input("Enter command (DOWNLOAD/UPLOAD/PROCESS/HEQ/EXIT): ")
    filename = ""
    if command in ["DOWNLOAD", "UPLOAD", "HEQ"]:
        filename = input("Enter filename: ")

    asyncio.run(send_request(command, filename))
