import sys
import os
import math
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QGraphicsDropShadowEffect, QFrame, QSizePolicy,
                             QHBoxLayout, QPushButton)
from PyQt5.QtCore import Qt, QTimer, QPoint, QRectF, pyqtSlot, QSize
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont, QLinearGradient, QRadialGradient

# Ensure path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from Frontend.FridayWorker import FridayWorker
except ImportError:
    # Fallback if running from root
    sys.path.append(os.path.join(os.getcwd(), "Frontend"))
    from FridayWorker import FridayWorker

# --- CONFIG ---
THEME_COLOR = QColor(0, 255, 255) # Cyan
ACCENT_COLOR = QColor(0, 150, 255) # Blue
BG_COLOR = QColor(10, 10, 15, 240) # Dark Blue/Black semi-transparent

class ArcReactorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.angle_1 = 0
        self.angle_2 = 0
        self.angle_3 = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30) # ~30 FPS

    def animate(self):
        self.angle_1 = (self.angle_1 + 2) % 360
        self.angle_2 = (self.angle_2 - 3) % 360
        self.angle_3 = (self.angle_3 + 1) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPoint(self.width() // 2, self.height() // 2)
        
        # Glow Effect
        glow = QRadialGradient(center, 150)
        glow.setColorAt(0, QColor(0, 255, 255, 40))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), glow)

        pen = QPen(THEME_COLOR)
        pen.setWidth(2)
        painter.setPen(pen)

        # Core Circle
        painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
        painter.drawEllipse(center, 20, 20)
        painter.setBrush(Qt.NoBrush)

        # Inner Ring
        rect1 = QRectF(center.x() - 50, center.y() - 50, 100, 100)
        painter.drawArc(rect1, int(self.angle_1 * 16), 120 * 16)
        painter.drawArc(rect1, int((self.angle_1 + 180) * 16), 120 * 16)

        # Middle Ring
        rect2 = QRectF(center.x() - 80, center.y() - 80, 160, 160)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawArc(rect2, int(self.angle_2 * 16), 270 * 16)

        # Outer Ring (Ticks)
        rect3 = QRectF(center.x() - 110, center.y() - 110, 220, 220)
        pen.setWidth(2)
        painter.setPen(pen)
        # Draw rotating dashes
        painter.save()
        painter.translate(center)
        painter.rotate(self.angle_3)
        for i in range(0, 360, 30):
            painter.drawLine(0, -110, 0, -120)
            painter.rotate(30)
        painter.restore()

class AudioWaveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.bars = [10] * 30
        self.active = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def set_active(self, active: bool):
        self.active = active
        if not active:
            self.bars = [10] * 30
            self.update()

    def animate(self):
        if self.active:
            # Simulate wave
            self.bars = [random.randint(10, 50) for _ in range(30)]
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(THEME_COLOR))
        painter.setPen(Qt.NoPen)
        
        w = self.width()
        bar_w = w / 30
        
        center_y = self.height() // 2
        
        for i, h in enumerate(self.bars):
            x = i * bar_w
            painter.drawRoundedRect(QRectF(x, center_y - h/2, bar_w - 2, h), 2, 2)

class TypewriterLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.full_text = text
        self.current_idx = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.type_char)
        self.setWordWrap(True)
        self.setStyleSheet("color: white; font-family: 'Consolas'; font-size: 14px;")

    def set_text_animated(self, text):
        self.full_text = text
        self.current_idx = 0
        self.setText("")
        self.timer.start(30) # Speed

    def type_char(self):
        if self.current_idx < len(self.full_text):
            self.setText(self.full_text[:self.current_idx+1] + "█")
            self.current_idx += 1
        else:
            self.setText(self.full_text)
            self.timer.stop()

class CinematicWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Screen Geometry
        desktop = QApplication.desktop()
        self.screen_rect = desktop.screenGeometry()
        self.check_geometry()
        
        # Layouts
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Background Frame (Glass)
        self.bg_frame = QFrame()
        self.bg_frame.setStyleSheet(f"""
            background-color: rgba(10, 10, 15, 200);
            border: 1px solid rgba(0, 255, 255, 100);
            border-radius: 20px;
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(THEME_COLOR)
        self.bg_frame.setGraphicsEffect(shadow)
        
        # We need to manually stack widgets or put layout IN the frame.
        # Let's put layout in frame
        self.frame_layout = QVBoxLayout(self.bg_frame)
        self.main_layout.addWidget(self.bg_frame)

        # 1. Top Bar (Close)
        self.top_bar = QHBoxLayout()
        self.title_label = QLabel("JARVIS SYSTEMS") # Changed from FRIDAY to JARVIS for flavor
        self.title_label.setStyleSheet("color: rgba(0,255,255,150); font-weight: bold;")
        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
            QPushButton { color: white; background: transparent; border: none; font-weight: bold; }
            QPushButton:hover { color: red; }
        """)
        self.close_btn.clicked.connect(self.close)
        
        self.top_bar.addWidget(self.title_label)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.close_btn)
        self.frame_layout.addLayout(self.top_bar)

        # 2. Arc Reactor (Center)
        self.reactor = ArcReactorWidget()
        self.reactor_layout = QHBoxLayout()
        self.reactor_layout.addStretch()
        self.reactor_layout.addWidget(self.reactor)
        self.reactor_layout.addStretch()
        self.frame_layout.addLayout(self.reactor_layout)

        # 3. Status Label
        self.status_label = QLabel("SYSTEMS ONLINE")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: cyan; 
            font-size: 18px; 
            font-weight: bold; 
            letter-spacing: 5px;
        """)
        self.frame_layout.addWidget(self.status_label)

        # 4. Audio Visualizer (Hidden until listening)
        self.wave = AudioWaveWidget()
        self.frame_layout.addWidget(self.wave)

        # 5. Output Text (Typewriter)
        self.output_text = TypewriterLabel("Waiting for input...")
        self.output_text.setAlignment(Qt.AlignCenter)
        self.output_text.setFixedWidth(500) # Wrap width
        # Center the label
        text_layout = QHBoxLayout()
        text_layout.addStretch()
        text_layout.addWidget(self.output_text)
        text_layout.addStretch()
        self.frame_layout.addLayout(text_layout)

        self.frame_layout.addStretch()

        # Initialize Worker
        self.worker = FridayWorker()
        self.worker.signal_user_input.connect(self.on_user_input)
        self.worker.signal_assistant_output.connect(self.on_assistant_output)
        self.worker.signal_status_change.connect(self.on_status_change)
        self.worker.start()

        # Drag Logic
        self.old_pos = None

    def check_geometry(self):
        # Size: 600x600 center screen
        w, h = 600, 700
        x = (self.screen_rect.width() - w) // 2
        y = (self.screen_rect.height() - h) // 2
        self.setGeometry(x, y, w, h)

    # --- SLOTS ---
    @pyqtSlot(str)
    def on_user_input(self, text):
        self.status_label.setText(f"USER: {text[:20]}...")
        self.wave.set_active(True) # Simulating processing
        QTimer.singleShot(1000, lambda: self.wave.set_active(False))

    @pyqtSlot(str)
    def on_assistant_output(self, text):
        self.output_text.set_text_animated(text)
        self.status_label.setText("RESPONSE COMPLETE")

    @pyqtSlot(str)
    def on_status_change(self, status):
        # Clean status text
        status = status.upper().replace("...", "")
        self.status_label.setText(status)
        
        if "LISTENING" in status:
            self.wave.set_active(True)
            self.status_label.setStyleSheet("color: #00FF00; font-size: 18px; letter-spacing: 5px; font-weight: bold;") # Green
        else:
            self.wave.set_active(False)
            self.status_label.setStyleSheet("color: cyan; font-size: 18px; letter-spacing: 5px; font-weight: bold;")

    # --- DRAG LOGIC ---
    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def closeEvent(self, event):
        self.worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CinematicWindow()
    window.show()
    sys.exit(app.exec_())
