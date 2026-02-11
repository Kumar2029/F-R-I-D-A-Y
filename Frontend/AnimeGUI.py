import sys
import os
import random
import math
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QGraphicsDropShadowEffect, QFrame, QSizePolicy,
                             QHBoxLayout, QPushButton)
from PyQt5.QtCore import Qt, QTimer, QPoint, QRectF, pyqtSlot, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont, QPixmap, QPolygonF, QMovie, QImage

# Ensure path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from Frontend.FridayWorker import FridayWorker
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), "Frontend"))
    from FridayWorker import FridayWorker

# --- CONFIG ---
THEME_COLOR = QColor(255, 105, 180) # Hot Pink
BG_COLOR = QColor(255, 255, 255, 220) # White semi-transparent
TEXT_COLOR = QColor(60, 60, 60)

class AnimeCharacterWidget(QWidget):
    """
    Displays the character avatar using OpenCV for robust video playback.
    Fills the entire screen/parent widget.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setFixedSize(400, 500) # Removed for Full Screen
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.is_speaking = False
        self.is_listening = False
        self.files_dir = os.path.join(os.path.dirname(__file__), "Graphics")
        
        # Paths
        self.idle_gif = os.path.join(self.files_dir, "Idle.gif")
        self.talk_gif = os.path.join(self.files_dir, "Talk.gif")
        self.idle_mp4 = os.path.join(self.files_dir, "Idle.mp4")
        self.talk_mp4 = os.path.join(self.files_dir, "Talk.mp4")
        self.avatar_png = os.path.join(self.files_dir, "Avatar.png")

        # Media Logic
        self.mode = "PROCEDURAL"
        self.movie = None
        self.cap = None # OpenCV Capture
        
        # Timer for frame updates (30 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        self.check_resources()

        # Fallback Anim
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.blink)
        self.is_blinking = False
        self.talk_timer = QTimer(self)
        self.talk_timer.timeout.connect(self.animate_mouth)
        self.mouth_open = 0
        
        if self.mode == "PROCEDURAL":
            self.blink_timer.start(3000)

        # DEBUG: Show mode
        print(f"[AnimeGUI] Initialized in mode: {self.mode}")

    def check_resources(self):
        # 1. GIF Priority
        if os.path.exists(self.idle_gif) and os.path.exists(self.talk_gif):
            self.mode = "GIF"
            self.movie = QMovie(self.idle_gif)
            self.movie.setCacheMode(QMovie.CacheAll)
            self.movie.frameChanged.connect(self.repaint)
            self.movie.start()
            return

        # 2. MP4 (OpenCV)
        if os.path.exists(self.idle_mp4) and os.path.exists(self.talk_mp4):
            try:
                import cv2
                self.mode = "VIDEO_CV2"
                self.load_video(self.idle_mp4)
                self.timer.start(33) # ~30 FPS
                return
            except ImportError:
                print("OpenCV not found, falling back.")

        # 3. Image
        if os.path.exists(self.avatar_png):
            self.mode = "IMAGE"
            return
            
        self.mode = "PROCEDURAL"

    def load_video(self, path):
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(path)

    def update_frame(self):
        if self.mode == "VIDEO_CV2" and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                # Loop
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
            
            if ret:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Expand to fill (Zoom effect)
                self.current_frame = qt_img.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.update()

    def set_speaking(self, speaking):
        if self.is_speaking == speaking:
            return
        self.is_speaking = speaking
        
        if self.mode == "GIF":
            target = self.talk_gif if speaking else self.idle_gif
            if self.movie.fileName() != target:
                self.movie.stop()
                self.movie.setFileName(target)
                self.movie.start()
        
        elif self.mode == "VIDEO_CV2":
            target = self.talk_mp4 if speaking else self.idle_mp4
            self.load_video(target)

        elif self.mode == "PROCEDURAL":
            if speaking:
                self.talk_timer.start(100)
            else:
                self.talk_timer.stop()
                self.mouth_open = 0
                self.update()
        
        self.update()

    def set_listening(self, listening):
        self.is_listening = listening
        self.update()

    # --- PROCEDURAL ANIMATION ---
    def blink(self):
        self.is_blinking = True
        QTimer.singleShot(150, lambda: setattr(self, 'is_blinking', False))
        self.update()
        
    def animate_mouth(self):
        self.mouth_open = random.randint(5, 20)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Full Rect
        target_rect = self.rect()

        if self.mode == "GIF":
            if self.movie and self.movie.currentPixmap():
                frame = self.movie.currentPixmap()
                # Scale to Fill
                scaled = frame.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                # Center Crop logic
                x = (self.width() - scaled.width()) // 2
                y = (self.height() - scaled.height()) // 2
                painter.drawPixmap(x, y, scaled)
            return

        if self.mode == "VIDEO_CV2":
            if hasattr(self, 'current_frame') and self.current_frame:
                # Already scaled in update_frame but rect might change
                # Re-do centering
                img = self.current_frame
                x = (self.width() - img.width()) // 2
                y = (self.height() - img.height()) // 2
                painter.drawImage(x, y, img)
            return

        if self.mode == "IMAGE":
            pixmap = QPixmap(self.avatar_png)
            scaled = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            return

        # --- PROCEDURAL DRAWING (Fallback) ---
        # Fill BG
        painter.fillRect(self.rect(), QColor(255, 240, 245))
        
        # Head
        painter.setBrush(QBrush(QColor(255, 255, 255))) 
        painter.setPen(QPen(THEME_COLOR, 4))
        
        # Draw Big Face
        w, h = self.width(), self.height()
        rect = QRectF(w//2 - 150, h//2 - 200, 300, 350)
        painter.drawRoundedRect(rect, 40, 40)

        # Eyes
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.setPen(Qt.NoPen)
        
        eye_y = int(h//2 - 50)
        
        if self.is_blinking:
            # Closed Eyes
            pen = QPen(QColor(60, 60, 60), 6)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(int(w//2 - 80), eye_y, int(w//2 - 40), eye_y)
            painter.drawLine(int(w//2 + 40), eye_y, int(w//2 + 80), eye_y)
        else:
            # Open Eyes
            painter.drawEllipse(int(w//2 - 90), eye_y - 30, 60, 80)
            painter.drawEllipse(int(w//2 + 30), eye_y - 30, 60, 80)
            
            # Highlights
            painter.setBrush(QBrush(Qt.white))
            painter.drawEllipse(int(w//2 - 80), eye_y - 20, 25, 25)
            painter.drawEllipse(int(w//2 + 40), eye_y - 20, 25, 25)

        # Cheeks (Blush)
        painter.setBrush(QBrush(QColor(255, 100, 100, 100)))
        painter.drawEllipse(int(w//2 - 120), eye_y + 60, 50, 30)
        painter.drawEllipse(int(w//2 + 70), eye_y + 60, 50, 30)

        # Mouth
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 80, 80)))
        mouth_y = int(h//2 + 70)
        if self.is_speaking:
            # Moving Mouth
            w_mouth = 30
            h_mouth = self.mouth_open * 2
            painter.drawEllipse(int(w//2 - w_mouth/2), int(mouth_y - h_mouth/2), w_mouth, h_mouth)
        else:
            # Smile
            pen = QPen(QColor(60, 60, 60), 4)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(int(w//2 - 30), mouth_y, 60, 30, 180*16, 180*16)


class DialogueBox(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            border: 2px solid rgba(255, 255, 255, 100);
            border-radius: 15px;
        """)
        self.layout = QVBoxLayout(self)
        
        self.name_label = QLabel("SYSTEM")
        self.name_label.setStyleSheet("color: #FF69B4; font-weight: bold; font-family: 'Segoe UI'; font-size: 16px; text-transform: uppercase;")
        self.layout.addWidget(self.name_label)
        
        self.text_label = QLabel("...")
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("color: white; font-family: 'Segoe UI'; font-size: 20px; border: none; background: transparent; font-weight: 500;")
        self.layout.addWidget(self.text_label)
        self.layout.addStretch()

        # Typewriter logic
        self.full_text = ""
        self.curr_idx = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step_text)

    def set_text(self, name, text):
        self.name_label.setText(name)
        self.full_text = text
        self.curr_idx = 0
        self.text_label.setText("")
        self.timer.start(30)

    def step_text(self):
        if self.curr_idx < len(self.full_text):
            self.text_label.setText(self.full_text[:self.curr_idx+1])
            self.curr_idx += 1
        else:
            self.timer.stop()


class AnimeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Full Screen Flags
        self.setWindowFlags(Qt.FramelessWindowHint) # Removed WindowStaysOnTopHint
        
        # 1. Main Video Background Widget
        self.char_widget = AnimeCharacterWidget()
        self.setCentralWidget(self.char_widget)
        
        # 2. Overlay Layout
        # We set a layout on the char_widget to position children on top of it
        self.overlay_layout = QVBoxLayout(self.char_widget)
        self.overlay_layout.setContentsMargins(40, 40, 40, 40)
        
        # Top Bar (Close Button)
        self.top_bar = QHBoxLayout()
        self.top_bar.addStretch()
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(50, 50)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton { 
                color: white; 
                background: rgba(0,0,0,100); 
                border-radius: 25px; 
                font-weight: bold;
                font-size: 20px;
                border: 2px solid white;
            }
            QPushButton:hover { background: #FF69B4; border-color: #FF69B4; }
        """)
        self.close_btn.clicked.connect(self.close_app)
        self.top_bar.addWidget(self.close_btn)
        
        self.overlay_layout.addLayout(self.top_bar)
        
        # Spacer to push dialogue down
        self.overlay_layout.addStretch()
        
        # Dialogue Box (Bottom)
        self.dialogue = DialogueBox()
        self.dialogue.setFixedHeight(200) # Bigger for full screen
        self.overlay_layout.addWidget(self.dialogue)

        # Worker
        self.worker = FridayWorker()
        self.worker.signal_user_input.connect(self.on_user_input)
        self.worker.signal_assistant_output.connect(self.on_assistant_output)
        self.worker.signal_status_change.connect(self.on_status_change)
        self.worker.start()
        
        # Launch Full Screen
        self.showFullScreen()

    @pyqtSlot(str)
    def on_user_input(self, text):
        self.dialogue.set_text("YOU", text)
        self.char_widget.set_speaking(False)

    @pyqtSlot(str)
    def on_assistant_output(self, text):
        self.dialogue.set_text("JARVIS", text)
        self.char_widget.set_speaking(True)
        duration = len(text) * 50 + 1000
        QTimer.singleShot(duration, lambda: self.char_widget.set_speaking(False))

    @pyqtSlot(str)
    def on_status_change(self, status):
        if "LISTENING" in status.upper():
            self.char_widget.set_listening(True)
            self.dialogue.set_text("SYSTEM", "Listening...")
        else:
            self.char_widget.set_listening(False)

    def close_app(self):
        self.worker.stop()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AnimeWindow()
    # win.show() # Covered by init
    sys.exit(app.exec_())
