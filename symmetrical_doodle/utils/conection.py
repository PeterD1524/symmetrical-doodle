import asyncio


async def close_connection(
    connection: tuple[asyncio.StreamReader, asyncio.StreamWriter]
):
    await close_writer(connection[1])


async def close_writer(writer: asyncio.StreamWriter):
    writer.write_eof()
    writer.close()
    await writer.wait_closed()
