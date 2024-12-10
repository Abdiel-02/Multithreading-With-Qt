import math
from dataclasses import dataclass
from typing import cast

from PySide6.QtCore import QPointF, QRectF, QSize
from PySide6.QtGui import QImage, QVector3D, qRgb


@dataclass(frozen=True)
class Sphere:
    center: QVector3D
    r: float


@dataclass(frozen=True)
class Ray:
    start: QVector3D
    end: QVector3D

    @property
    def direction(self):
        return (self.end - self.start).normalized()


class RayCaster:
    def render(self, viewport: QSize, dpi: float):
        minDimension = min(viewport.width(), viewport.height())
        sccreenRectangle = QRectF(
            -0.5 * (viewport.width() / minDimension),
            -0.5 * (viewport.height() / minDimension),
            viewport.width() / minDimension,
            viewport.height() / minDimension,
        )

        scaledViewport = viewport * dpi
        image = QImage(scaledViewport, QImage.Format.Format_RGB32)
        image.setDevicePixelRatio(dpi)

        sphere = Sphere(QVector3D(0, 0, 10), 0.5)
        directionlLight = Ray(QVector3D(1, 1, 0), QVector3D(0, 0, 0)).direction

        screenDelta = QPointF(
            sccreenRectangle.width() / (scaledViewport.width() - 1),
            sccreenRectangle.height() / (scaledViewport.height() - 1),
        )

        for y in range(scaledViewport.height()):
            scanLine = cast(memoryview, image.scanLine(y)).cast("@I")
            for x in range(scaledViewport.width()):
                ray = Ray(
                    QVector3D(
                        sccreenRectangle.x() + x * screenDelta.x(),
                        sccreenRectangle.y() + y * screenDelta.y(),
                        0,
                    ),
                    QVector3D(
                        sccreenRectangle.x() + x * screenDelta.x(),
                        sccreenRectangle.y() + y * screenDelta.y(),
                        1,
                    ),
                )

                a = (
                    ray.direction.x() * ray.direction.x()
                    + ray.direction.y() * ray.direction.y()
                    + ray.direction.z() * ray.direction.z()
                )
                b = (
                    2 * ray.direction.x() * (ray.start.x() - sphere.center.x())
                    + 2 * ray.direction.y() * (ray.start.y() - sphere.center.y())
                    + 2 * ray.direction.z() * (ray.start.z() - sphere.center.z())
                )
                c = (
                    sphere.center.x() * sphere.center.x()
                    + sphere.center.y() * sphere.center.y()
                    + sphere.center.z() * sphere.center.z()
                    + ray.start.x() * ray.start.x()
                    + ray.start.y() * ray.start.y()
                    + ray.start.z() * ray.start.z()
                    + -2
                    * (
                        sphere.center.x() * ray.start.x()
                        + sphere.center.y() * ray.start.y()
                        + sphere.center.z() * ray.start.z()
                    )
                    + -(sphere.r * sphere.r)
                )

                delta = b * b - 4 * (a * c)

                if delta >= 0:
                    tAtCollision = (-b - math.sqrt(delta)) / (2 * a)
                    pointOfCollision = ray.start + (ray.direction * tAtCollision)
                    normalAtCollision = (pointOfCollision - sphere.center).normalized()
                    cosine = QVector3D.dotProduct(-directionlLight, normalAtCollision)

                    r = int(255 * 0.3 + 255 * 0.7 * max(0.0, -cosine))
                    scanLine[x] = qRgb(r, 0, 0)
                else:
                    scanLine[x] = qRgb(0, 0, 0)

        return image
