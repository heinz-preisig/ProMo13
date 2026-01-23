from PyQt5.QtCore import QEasingCurve
from PyQt5.QtCore import QParallelAnimationGroup
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class CircleProgressBar(QWidget):
    def __init__(self, num_steps=7, parent=None):
        super().__init__(parent)

        self.num_steps = num_steps
        self.minimum_diameter = 40

        self.circle_diameter = None
        self.circle_distance = None
        self.padding = None

        self.current_step = 0
        self.future_step = None
        self.animated_line = None

        self._animated_line_length = 0
        self.line_animation = QPropertyAnimation(
                self, b"animated_line_length", self)
        self.line_animation.setEasingCurve(QEasingCurve.InOutQuad)
        # self.line_animation.setDuration(300)

        self._leaving_radius = 0
        self.leaving_radius_animation = QPropertyAnimation(
                self, b"leaving_radius", self)
        self._leaving_bg_color = QColor("#000000")
        self.leaving_bg_animation = QPropertyAnimation(
                self, b"leaving_bg_color", self)
        self._leaving_font_color = QColor("#000000")
        self.leaving_font_animation = QPropertyAnimation(
                self, b"leaving_font_color", self)
        self.leaving_animation = QParallelAnimationGroup()
        self.leaving_animation.addAnimation(self.leaving_radius_animation)
        self.leaving_animation.addAnimation(self.leaving_bg_animation)
        self.leaving_animation.addAnimation(self.leaving_font_animation)
        # self.border_animation.setEasingCurve(QEasingCurve.InOutQuad)
        # self.leaving_animation.setDuration(300)

        self._arriving_radius = 0
        self.arriving_radius_animation = QPropertyAnimation(
                self, b"arriving_radius", self)
        self._arriving_bg_color = QColor("#000000")
        self.arriving_bg_animation = QPropertyAnimation(
                self, b"arriving_bg_color", self)
        self._arriving_font_color = QColor("#000000")
        self.arriving_font_animation = QPropertyAnimation(
                self, b"arriving_font_color", self)
        self.arriving_animation = QParallelAnimationGroup()
        self.arriving_animation.addAnimation(self.arriving_radius_animation)
        self.arriving_animation.addAnimation(self.arriving_bg_animation)
        self.arriving_animation.addAnimation(self.arriving_font_animation)

        # self.border_animation.setEasingCurve(QEasingCurve.InOutQuad)
        # self.arriving_animation.setDuration(300)

        self.full_animation = QParallelAnimationGroup()
        self.full_animation.addAnimation(self.leaving_animation)
        self.full_animation.addAnimation(self.line_animation)
        self.full_animation.addAnimation(self.arriving_animation)

        # self.full_animation = QSequentialAnimationGroup()
        # self.full_animation.addAnimation(self.first_animation)
        # self.full_animation.addAnimation(self.arriving_animation)

        self.full_animation.finished.connect(self.animation_finished)

        self.setMinimumSize(self.minimumSizeHint())

    def setup_animation(self):
        if self.current_step < self.future_step:
            self.line_animation.setStartValue(0)
            self.line_animation.setEndValue(
                    self.circle_distance - 2 * self.circle_diameter // 15)
            self.leaving_bg_animation.setStartValue(QColor("#333333"))
            self.leaving_bg_animation.setEndValue(QColor("#646464"))
            self.leaving_font_animation.setStartValue(QColor("#FFFFFF"))
            self.leaving_font_animation.setEndValue(QColor("#FFFFFF"))
            self.arriving_bg_animation.setStartValue(QColor("#B4B4B4"))
            self.arriving_bg_animation.setEndValue(QColor("#333333"))
            self.arriving_font_animation.setStartValue(QColor("#333333"))
            self.arriving_font_animation.setEndValue(QColor("#FFFFFF"))

        else:
            self.line_animation.setStartValue(
                    self.circle_distance - 2 * self.circle_diameter // 15)
            self.line_animation.setEndValue(0)
            self.leaving_bg_animation.setStartValue(QColor("#333333"))
            self.leaving_bg_animation.setEndValue(QColor("#B4B4B4"))
            self.leaving_font_animation.setStartValue(QColor("#FFFFFF"))
            self.leaving_font_animation.setEndValue(QColor("#333333"))
            self.arriving_bg_animation.setStartValue(QColor("#646464"))
            self.arriving_bg_animation.setEndValue(QColor("#333333"))
            self.arriving_font_animation.setStartValue(QColor("#FFFFFF"))
            self.arriving_font_animation.setEndValue(QColor("#FFFFFF"))

        self.leaving_radius_animation.setStartValue(0)
        self.leaving_radius_animation.setEndValue(self.circle_diameter // 2)

        self.arriving_radius_animation.setStartValue(self.circle_diameter // 2)
        self.arriving_radius_animation.setEndValue(0)

    def animation_finished(self):
        self.current_step = self.future_step

    def next(self):
        if self.current_step + 1 < self.num_steps:
            self.future_step = self.current_step + 1
            self.animated_line = self.current_step
            self.setup_animation()
            self.full_animation.start()

    def previous(self):
        if self.current_step - 1 >= 0:
            self.future_step = self.current_step - 1
            self.animated_line = self.current_step - 1
            self.setup_animation()
            self.full_animation.start()

    def minimumSizeHint(self) -> QSize:
        padding = self.minimum_diameter // 4
        circle_distance = self.minimum_diameter * 2 // 3

        minimum_width = (
                2 * padding
                + self.num_steps * self.minimum_diameter
                + (self.num_steps - 1) * circle_distance
        )

        minimum_height = 2 * padding + self.minimum_diameter

        return QSize(minimum_width, minimum_height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate the available diameter for circles
        d1 = 6 * self.width() // (10 * self.num_steps - 1)
        d2 = 2 * self.height() // (3)

        self.circle_diameter = min(d1, d2)
        if self.circle_diameter < self.minimum_diameter:
            self.circle_diameter = self.minimum_diameter

        self.padding = self.circle_diameter // 4
        self.circle_distance = self.circle_diameter * 2 // 3

        font_size = int(self.circle_diameter / 3)  # scaling factor
        font = QFont("Computer Modern", font_size)
        painter.setFont(font)

        border_pen = QPen(QColor("#333333"), self.circle_diameter // 15)

        current_step_brush = QBrush(QColor("#333333"))
        current_font_pen = QPen(QColor("#FFFFFF"), self.circle_diameter // 15)

        completed_step_brush = QBrush(QColor("#646464"))
        completed_font_pen = current_font_pen

        pending_step_brush = QBrush(QColor("#B4B4B4"))
        pending_font_pen = QPen(QColor("#333333"), self.circle_diameter // 15)

        thin_line_pen = border_pen
        thick_line_pen = QPen(QColor("#333333"), self.circle_diameter // 5)

        # Drawing the lines
        for i in range(self.num_steps - 1):
            if i == self.animated_line and self.full_animation.state() == QPropertyAnimation.Running:
                self.draw_line(i, painter, thin_line_pen)
                self.draw_line(i, painter, thick_line_pen, self._animated_line_length)
            elif i < self.current_step:
                self.draw_line(i, painter, thick_line_pen)
            else:
                self.draw_line(i, painter, thin_line_pen)

        # Drawing the shapes
        for i in range(self.num_steps):
            if i == self.current_step:
                if self.full_animation.state() == QPropertyAnimation.Running:
                    pen = QPen(self._leaving_font_color, self.circle_diameter // 15)
                    brush = QBrush(self._leaving_bg_color)
                    self.draw_shape(i, self._leaving_radius,
                                    painter, border_pen, pen, brush)
                else:
                    self.draw_shape(i, 0, painter, border_pen,
                                    current_font_pen, current_step_brush)
            elif i == self.future_step and self.arriving_animation.state() == QPropertyAnimation.Running:
                # print(self._arriving_radius)
                pen = QPen(self._arriving_font_color, self.circle_diameter // 15)
                brush = QBrush(self._arriving_bg_color)
                self.draw_shape(i, self._arriving_radius,
                                painter, border_pen, pen, brush)
            else:
                radius = self.circle_diameter // 2
                if i < self.current_step:
                    self.draw_shape(i, radius, painter, border_pen,
                                    completed_font_pen, completed_step_brush)
                else:
                    self.draw_shape(i, radius, painter, border_pen,
                                    pending_font_pen, pending_step_brush)

    def draw_shape(self, pos, border_radius, painter, b_pen, t_pen, brush):
        # Calculating coordinates
        x = self.padding + pos * (self.circle_distance + self.circle_diameter)
        y = (self.height() - self.circle_diameter) // 2

        rect = QRectF(x, y, self.circle_diameter, self.circle_diameter)

        # Drawing the shape
        painter.setPen(b_pen)
        painter.setBrush(brush)
        painter.drawRoundedRect(rect, border_radius, border_radius)

        # Drawing the text
        painter.setPen(t_pen)
        painter.drawText(rect, Qt.AlignCenter, str(pos + 1))

    def draw_line(self, pos, painter, pen, length=None):
        # Calculating coordinates
        border_thickness = self.circle_diameter // 15
        x1 = self.padding + (pos + 1) * self.circle_diameter + \
             pos * self.circle_distance + border_thickness

        if length is None:
            length = self.circle_distance - 2 * border_thickness

        x2 = x1 + int(length)

        y = self.height() // 2

        if length == 0.0:
            pen.setWidthF(0.0)

        # Drawing the line
        painter.setPen(pen)
        painter.drawLine(x1, y, x2, y)

    @pyqtProperty(float)
    def animated_line_length(self):
        return self._animated_line_length

    @animated_line_length.setter
    def animated_line_length(self, length):
        self._animated_line_length = length
        self.update()

    @pyqtProperty(float)
    def leaving_radius(self):
        return self._leaving_radius

    @leaving_radius.setter
    def leaving_radius(self, radius):
        self._leaving_radius = radius
        #  self.update()

    @pyqtProperty(QColor)
    def leaving_bg_color(self):
        return self._leaving_bg_color

    @leaving_bg_color.setter
    def leaving_bg_color(self, color):
        self._leaving_bg_color = color
        #  self.update()

    @pyqtProperty(QColor)
    def leaving_font_color(self):
        return self._leaving_font_color

    @leaving_font_color.setter
    def leaving_font_color(self, color):
        self._leaving_font_color = color
        #  self.update()

    @pyqtProperty(float)
    def arriving_radius(self):
        return self._arriving_radius

    @arriving_radius.setter
    def arriving_radius(self, radius):
        self._arriving_radius = radius
        #  self.update()

    @pyqtProperty(QColor)
    def arriving_bg_color(self):
        return self._arriving_bg_color

    @arriving_bg_color.setter
    def arriving_bg_color(self, color):
        self._arriving_bg_color = color
        #  self.update()

    @pyqtProperty(QColor)
    def arriving_font_color(self):
        return self._arriving_font_color

    @arriving_font_color.setter
    def arriving_font_color(self, color):
        self._arriving_font_color = color
        #  self.update()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    w = CircleProgressBar()
    w.resize(w.minimumSizeHint())

    button_layout = QHBoxLayout()
    pbutton_previous = QPushButton("Previous")
    pbutton_next = QPushButton("Next")
    button_layout.addWidget(pbutton_previous)
    button_layout.addWidget(pbutton_next)

    pbutton_next.clicked.connect(w.next)
    pbutton_previous.clicked.connect(w.previous)

    main_layout = QVBoxLayout()
    main_layout.addWidget(w)
    main_layout.addLayout(button_layout)

    a = QWidget()
    a.setLayout(main_layout)

    a.show()

    sys.exit(app.exec_())
