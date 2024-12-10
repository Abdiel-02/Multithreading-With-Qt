from typing import Optional

from PySide6.QtCore import QEvent, QObject, QSize, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QMainWindow, QSizePolicy, QWidget

from raycaster import RayCaster
from ui_mainwindow import Ui_MainWindow


class RenderingThread(QThread):
    def __init__(
        self, viewportSize: QSize, dpi: float, parent: Optional[QObject] = None
    ) -> None:
        super().__init__(parent)

        self.dpi = dpi
        self.viewportSize = viewportSize

    result = Signal(QImage)

    def run(self) -> None:
        caster = RayCaster()
        result = caster.render(self.viewportSize, self.dpi)
        self.result.emit(result)


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def event(self, event: QEvent) -> bool:
        match event.type():
            case QEvent.Type.Resize:
                self.ui.viewport.setSizePolicy(
                    QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
                )
                self.ui.viewport.resize(self.geometry().size())
                self.renderImage()

        return super().event(event)

    def renderImage(self):
        thread = RenderingThread(self.ui.viewport.size(), self.devicePixelRatio(), self)
        thread.result.connect(self.threadResult)
        thread.finished.connect(thread.deleteLater)
        thread.start()

    @Slot()
    def threadResult(self, image: QImage):
        if image.size() != self.ui.viewport.size() * self.devicePixelRatio():
            return
        self.ui.viewport.setPixmap(QPixmap.fromImage(image))
