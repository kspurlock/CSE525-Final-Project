import asyncio
import time
import socket
import requests
import logging

from shazamio import Shazam


# Basic logging to record ShazamIO operation
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - [%(filename)s:%(lineno)d - %(funcName)s()] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def perform_lookup(audio_bytes: bytes) -> bytes:
    """Performs recognition of song and extracts information from
    Shazam API response

    Args:
        audio_bytes (bytes): audio_bytes received from client

    Returns:
        bytes: concatenated byte string containing size, metadata, and image bytes
    """
    shazam = Shazam()

    response: dict = await shazam.recognize(audio_bytes)
    
    # Extraction

    image_url = ""
    song_name = ""
    artist_name = ""
    album_name = ""
    release_year = ""

    if len(response["matches"]) > 0:
        song_name = response["track"]["title"]
        artist_name = response["track"]["subtitle"]

        sections = response["track"]["sections"]
        for section in sections:
            if section["type"] == "SONG":
                for metapage in section["metapages"]:
                    # Find image
                    if metapage["caption"] == song_name:
                        image_url = metapage["image"]

                # Find album name and release year
                for metadata in section["metadata"]:
                    if metadata["title"] == "Album":
                        album_name = metadata["text"]
                    elif metadata["title"] == "Released":
                        release_year = metadata["text"]
                        
        # Formatting
        meta_bytes = "\n".join(
            [song_name, artist_name, album_name, release_year]
        ).encode()
        size_bytes = (len(meta_bytes)).to_bytes(2, byteorder="big")
        if image_url:
            image_bytes = requests.get(image_url).content  # Download image
        else:
            image_bytes = b""

        full_bytes = size_bytes + meta_bytes + image_bytes

    else:
        full_bytes = b"\x00\x00"  # Corresponds to length 0 size bytes

    return full_bytes


async def handle_connection(reader, writer):
    """Receives data from client, calls lookup procedure,
    and returns response to client
    """
    audio_bytes = await reader.read(-1)
    reader.feed_eof()

    response = await perform_lookup(audio_bytes)

    writer.write(response)
    await writer.drain()
    writer.write_eof()

    writer.close()
    await writer.wait_closed()


async def main():
    hostname = socket.getfqdn()
    address = socket.gethostbyname_ex(hostname)[2][1]

    server = await asyncio.start_server(handle_connection, address, 8000)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


asyncio.run(main())
