import asyncio
from asyncio import StreamReader, StreamWriter


async def send_request(command: str, filename: str):
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)

    if command == "DOWNLOAD":
        writer.write(f"DOWNLOAD {filename}\n".encode())
        response = await reader.readline()
        if response == b"ERROR File not found\n":
            print("File not found on the server.")
        else:
            data = await reader.readuntil(EOF)
            content = data[: -1 * len(EOF)]
            with open(f"client-files/{filename}", "wb") as f:
                f.write(content)
            print("File downloaded successfully.")

    elif command == "UPLOAD":
        with open(f"client-files/{filename}", "rb") as f:
            content = f.read()
        writer.write(f"UPLOAD {filename}\n".encode())
        # multithread here
        writer.write(content)
        writer.write(EOF)
        response = await reader.readline()
        print(response.decode().strip())

    elif command == "PROCESS":
        writer.write(f"PROCESS {filename}\n".encode())
        response = await reader.readline()
        if response == b"ERROR File not found\n":
            print("File not found on the server.")
        else:
            data = await reader.readuntil(b"END\n")
            content = data[:-4]
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
    command = input("Enter command (DOWNLOAD/UPLOAD/PROCESS/EXIT): ")
    filename = ""
    if command in ["DOWNLOAD", "UPLOAD"]:
        filename = input("Enter filename: ")

    asyncio.run(send_request(command, filename))
