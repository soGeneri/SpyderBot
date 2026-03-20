# -*- coding: utf-8 -*-
"""Custom Qt widgets: JoystickWidget, CrosshairWidget, ColorPreviewWidget."""
import math
from PyQt6.QtCore import pyqtSignal, QPointF, QSize, Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtWidgets import QWidget


class JoystickWidget(QWidget):
    """Virtual joystick with mouse drag + programmatic set_knob for WASD."""
    moved   = pyqtSignal(float, float)   # dx, dy  normalized -1.0 .. 1.0
    released = pyqtSignal()

    RADIUS = 100
    KNOB_R = 15

    def __init__(self, parent=None):
        super().__init__(parent)
        self._knob_pos = QPointF(0.0, 0.0)
        self._dragging = False
        self.setMouseTracking(False)

    def sizeHint(self):
        return QSize(230, 230)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self.rect().width() / 2
        cy = self.rect().height() / 2
        R  = self.RADIUS
        KR = self.KNOB_R

        # Outer circle
        qp.setPen(QPen(QColor('#555'), 2))
        qp.setBrush(QBrush(QColor('#2a2a2a')))
        qp.drawEllipse(int(cx - R), int(cy - R), int(R * 2), int(R * 2))

        # Crosshair lines through knob
        kx = cx + self._knob_pos.x()
        ky = cy + self._knob_pos.y()
        qp.setPen(QPen(QColor('#008aff'), 1, Qt.PenStyle.DashLine))
        qp.drawLine(int(cx - R), int(ky), int(cx + R), int(ky))
        qp.drawLine(int(kx), int(cy - R), int(kx), int(cy + R))

        # Knob
        qp.setPen(Qt.PenStyle.NoPen)
        qp.setBrush(QBrush(QColor('#008aff')))
        qp.drawEllipse(int(kx - KR), int(ky - KR), int(KR * 2), int(KR * 2))

    # ------------------------------------------------------------------ mouse
    def mousePressEvent(self, event):
        self._dragging = True
        self._update_from_pos(event.position())

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._update_from_pos(event.position())

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._knob_pos = QPointF(0.0, 0.0)
        self.update()
        self.released.emit()

    # ---------------------------------------------------------------- helpers
    def _clamp(self, dx, dy):
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > self.RADIUS:
            s = self.RADIUS / dist
            dx, dy = dx * s, dy * s
        return dx, dy

    def _update_from_pos(self, pos):
        cx = self.rect().width() / 2
        cy = self.rect().height() / 2
        dx, dy = self._clamp(pos.x() - cx, pos.y() - cy)
        self._knob_pos = QPointF(dx, dy)
        self.update()
        self.moved.emit(dx / self.RADIUS, dy / self.RADIUS)

    def set_knob(self, dx: float, dy: float):
        """Set knob to normalized position and emit moved signal (for WASD)."""
        self._knob_pos = QPointF(dx * self.RADIUS, dy * self.RADIUS)
        self.update()
        self.moved.emit(dx, dy)


class CrosshairWidget(QWidget):
    """Clickable crosshair pad that emits real-unit coordinates."""
    changed = pyqtSignal(float, float)

    def __init__(self, x_range=(-15, 15), y_range=(-15, 15), parent=None):
        super().__init__(parent)
        self._x_range = x_range
        self._y_range = y_range
        self._cursor  = QPointF(0.0, 0.0)  # normalized -1 .. 1

    def sizeHint(self):
        return QSize(220, 220)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.rect().width(), self.rect().height()

        # Background / border
        qp.setPen(QPen(QColor('#555'), 1))
        qp.setBrush(QBrush(QColor('#2a2a2a')))
        qp.drawRect(0, 0, w - 1, h - 1)

        # Crosshair at cursor position
        px = (self._cursor.x() + 1.0) / 2.0 * w
        py = (1.0 - (self._cursor.y() + 1.0) / 2.0) * h
        qp.setPen(QPen(QColor('#008aff'), 1))
        qp.drawLine(0, int(py), w, int(py))
        qp.drawLine(int(px), 0, int(px), h)

        # Coordinate label
        xr = self._x_range[1] - self._x_range[0]
        yr = self._y_range[1] - self._y_range[0]
        x_val = round(self._cursor.x() * xr / 2.0)
        y_val = round(self._cursor.y() * yr / 2.0)
        qp.setPen(QPen(QColor('#e0e0e0')))
        qp.setFont(QFont('Segoe UI', 8))
        qp.drawText(4, h - 4, f'({x_val},{y_val})')

    def mousePressEvent(self, event):
        self._update_from_pos(event.position())

    def mouseMoveEvent(self, event):
        self._update_from_pos(event.position())

    def mouseReleaseEvent(self, event):
        pass

    def _update_from_pos(self, pos):
        w, h = self.rect().width(), self.rect().height()
        nx = max(-1.0, min(1.0, pos.x() / w * 2.0 - 1.0))
        ny = max(-1.0, min(1.0, 1.0 - pos.y() / h * 2.0))
        self._cursor = QPointF(nx, ny)
        self.update()
        xr = self._x_range[1] - self._x_range[0]
        yr = self._y_range[1] - self._y_range[0]
        self.changed.emit(nx * xr / 2.0, ny * yr / 2.0)

    def reset(self):
        self._cursor = QPointF(0.0, 0.0)
        self.update()
        self.changed.emit(0.0, 0.0)


class ColorPreviewWidget(QWidget):
    """Solid-color swatch widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor(0, 0, 0)

    def setColor(self, r, g, b):
        self._color = QColor(int(r), int(g), int(b))
        self.update()

    def sizeHint(self):
        return QSize(80, 30)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(self.rect(), self._color)


# ----------------------------------------------------------------- standalone test
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget as W

    app = QApplication(sys.argv)
    win = W()
    lay = QHBoxLayout(win)
    j = JoystickWidget()
    c = CrosshairWidget()
    p = ColorPreviewWidget()
    p.setColor(255, 0, 128)
    j.moved.connect(lambda dx, dy: print(f'joy {dx:.2f},{dy:.2f}'))
    c.changed.connect(lambda x, y: print(f'cross {x:.1f},{y:.1f}'))
    lay.addWidget(j)
    lay.addWidget(c)
    lay.addWidget(p)
    win.show()
    sys.exit(app.exec())
