import asyncio
import dataclasses
from collections.abc import Callable
from typing import Optional

import av
import numpy
import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets


@dataclasses.dataclass
class FrameReceiver:
    signal_instance: PySide6.QtCore.SignalInstance
    frame_sink: asyncio.Queue[av.VideoFrame] = dataclasses.field(
        default_factory=asyncio.Queue, init=False
    )

    async def run(self):
        while True:
            frame = await self.frame_sink.get()
            image = frame.to_ndarray(format="rgb24")
            self.signal_instance.emit(image)


class Thread(PySide6.QtCore.QThread):
    image_received = PySide6.QtCore.Signal(numpy.ndarray)

    def __init__(self, target: Callable[[], None]):
        super().__init__()
        self.target = target

    def run(self):
        self.target()


class PySideScreen(PySide6.QtWidgets.QWidget):

    def __init__(
        self,
        thread: Thread,
        size: Optional[tuple[int, int]] = None,
        window_title: Optional[str] = None,
    ):

        super().__init__()

        self.pixmap = PySide6.QtGui.QPixmap()
        self.label = PySide6.QtWidgets.QLabel()

        self.frame_receiver = FrameReceiver(thread.image_received)

        self.label.setPixmap(self.pixmap)
        self.label.setScaledContents(True)

        layout = PySide6.QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)

        thread.image_received.connect(self.update_image)

        self.device_screen_size = size

        if window_title is not None:
            self.setWindowTitle(window_title)

    @PySide6.QtCore.Slot(numpy.ndarray)  # type: ignore https://bugreports.qt.io/browse/PYSIDE-2942
    def update_image(
        self, image: numpy.ndarray[tuple[int, int, int], numpy.dtype[numpy.uint8]]
    ):
        height, width = image.shape[:2]

        self.pixmap.convertFromImage(
            PySide6.QtGui.QImage(
                image.data, width, height, PySide6.QtGui.QImage.Format.Format_RGB888
            )
        )
        self.label.setPixmap(self.pixmap)

        rect = self.screen().availableGeometry()
        if width > rect.width():
            width_factor = rect.width() / width
        else:
            width_factor = 1
        if height > rect.height():
            height_factor = rect.height() / height
        else:
            height_factor = 1
        factor = min(width_factor, height_factor) * 0.8
        width = round(width * factor)
        height = round(height * factor)
        self.setFixedSize(width, height)


@dataclasses.dataclass
class App:
    thread: Thread
    size: dataclasses.InitVar[Optional[tuple[int, int]]] = None
    window_title: dataclasses.InitVar[Optional[str]] = None
    screen: PySideScreen = dataclasses.field(init=False)
    app: PySide6.QtWidgets.QApplication = dataclasses.field(
        default_factory=PySide6.QtWidgets.QApplication
    )

    def __post_init__(self, size, window_title):
        self.screen = PySideScreen(self.thread, size, window_title)

    def show(self):
        self.screen.show()

    def exec(self):
        return self.app.exec()

    def run(self):
        self.show()
        return self.exec()
