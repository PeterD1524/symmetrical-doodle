import asyncio
import dataclasses

import av
import cv2


@dataclasses.dataclass
class CV2Screen:
    frame_sink: asyncio.Queue[
        av.VideoFrame
    ] = dataclasses.field(default_factory=asyncio.Queue, init=False)

    winname: str
    title: str = ''

    async def run(self):
        cv2.namedWindow(self.winname, cv2.WINDOW_GUI_NORMAL)

        while True:
            frame = await self.frame_sink.get()
            frame = frame.to_ndarray(format='bgr24')
            cv2.resizeWindow(
                self.winname, frame.shape[1] // 3, frame.shape[0] // 3
            )
            cv2.imshow(self.winname, frame)
            key = cv2.pollKey()
            if key == 27 or key == 113:
                cv2.destroyWindow(self.winname)
                raise RuntimeError
