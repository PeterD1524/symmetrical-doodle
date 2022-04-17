# symmetrical-doodle

## Run scrcpy

```python
python -m symmetrical_doodle.scrcpy --server /path/to/scrcpy-server
```

## Example

```python
import asyncio

import symmetrical_doodle.decoders
import symmetrical_doodle.demuxers
import symmetrical_doodle.servers


async def main():
    # create a server with default settings
    server = symmetrical_doodle.servers.create_default_server(
        '/path/to/scrcpy-server'
    )
    # run and connect to the server
    server_process = await server.run()

    # create a demuxer to receive and process video packets
    demuxer = symmetrical_doodle.demuxers.Demuxer(server.video_connection)

    # create a decoder to decode packets into frames
    decoder = symmetrical_doodle.decoders.Decoder()
    # the demuxer will push packets into decoder's packet sink
    demuxer.sinks.append(decoder.packet_sink)

    frame_sink = asyncio.Queue()
    # the decoder will push frames into the frame sink
    decoder.sinks.append(frame_sink)

    # schedule the decoder and demuxer to run
    decoder_task = asyncio.create_task(decoder.run())
    demuxer_task = asyncio.create_task(demuxer.run())

    while True:
        frame = await frame_sink.get()
        # do something with the av frame
        image = frame.to_ndarray(format='bgr24')
        print(image.shape)


if __name__ == '__main__':
    asyncio.run(main())

```

