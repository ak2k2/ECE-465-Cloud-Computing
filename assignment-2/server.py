import asyncio
import os
from asyncio import StreamReader, StreamWriter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SERVER_DIRECTORY = "server-files"


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
                writer.write(b"OK\n")
                writer.write(content)
                await writer.drain()
                writer.write(b"END\n")
                await writer.drain()
                logger.info(f"Sent file {filename} to {client_addr}")

        elif command == "UPLOAD":
            filename = args[0]
            filepath = os.path.join(SERVER_DIRECTORY, filename)
            try:
                # set a timeout for readuntil
                data = await asyncio.wait_for(reader.readuntil(b"END\n"), timeout=10.0)
                data = data[:-4]
                with open(filepath, "wb") as f:
                    f.write(data)
                writer.write(b"OK File saved\n")
                await writer.drain()
                logger.info(f"Received and saved file {filename} from {client_addr}")
            except asyncio.TimeoutError:
                writer.write(b"ERROR Timeout waiting for file data\n")
                await writer.drain()
                logger.error(f"Timeout error waiting for file data from {client_addr}")

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
