"""
VLC Media Player (PySide6 + VLC)

A simple media player built with **Python, PySide6, and VLC** that allows users to play, pause, stop, and adjust volume for audio and video files.

Features
- Play, pause, and stop media files
- Adjust volume using a slider
- Seek through media playback with a position slider
- Supports popular formats like **MP3, MP4, AVI, MKV, etc.** using VLC

"""
import os
import sys
# print(sys.path)
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication, QSlider, QPushButton, QFileDialog, QHBoxLayout, QFrame
from PySide6.QtGui import QAction, QPalette, QColor
from PySide6.QtCore import Qt, QTimer
import vlc

class MediaPlayer(QMainWindow):

    def __init__(self, master=None):
        super().__init__(master)
        self.setWindowTitle("Media Player")

        # Create vlc instance to load media
        self.instance = vlc.Instance()

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.create_gui()
        self.is_paused = False

    def create_gui(self):
        # Create widget container and set as main center widget
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.videoframe = QFrame()

        # Set video frame background color to black
        self.palette = self.videoframe.palette()
        self.palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        # Create slider for media playback control (skip forward, rewind)
        self.positionslider = QSlider(Qt.Orientation.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)

        # Create horizontal layout box for play and pause if video is playing
        self.hbuttonbox = QHBoxLayout()
        self.playbutton = QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.play_pause)

        # Add second stop button to existing horizontal layout box 
        self.stopbutton = QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.stop)

        # .addStretch() adds padding to push volume slider to the right, away from play/stop buttons
        self.hbuttonbox.addStretch(1)
        # Create and add volume slider to layout
        self.volumeslider = QSlider(Qt.Orientation.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.set_volume) # Connect to se_volume() function

        # Create layout for the whole window
        self.vboxlayout = QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe) # Video playback window
        self.vboxlayout.addWidget(self.positionslider) # Playback control slider
        self.vboxlayout.addLayout(self.hbuttonbox) # Finally add play/stop buttons and volume slider

        # Set layout to the central widget (.widget)
        self.widget.setLayout(self.vboxlayout)

        menu_bar = self.menuBar()

        # File browse menu
        file_menu = menu_bar.addMenu("File")

        # Add functionality to file menu
        open_action = QAction("Load Video", self)
        close_action = QAction("Close App", self)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)

        open_action.triggered.connect(self.open_file)
        close_action.triggered.connect(sys.exit)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)

        self.volumeslider.setValue(50)
        self.mediaplayer.audio_set_volume(50)

    # Action functions
    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.is_paused = True
            self.timer.stop()
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.is_paused = False

    def stop(self):
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def open_file(self):
        dialog_txt = "Choose Media File"
        filename, _ = QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
        if not filename:
            return

        self.media = self.instance.media_new(filename)
        self.mediaplayer.set_media(self.media)

        self.media.parse()

        self.setWindowTitle(self.media.get_meta(vlc.Meta.Title))

        self.mediaplayer.set_hwnd(int(self.videoframe.winId()))

        self.play_pause()

    def set_volume(self, volume):
        self.mediaplayer.audio_set_volume(volume)

    def set_position(self, position):
        pos = position / 1000.0
        self.mediaplayer.set_position(pos)

    def update_ui(self):
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.positionslider.setValue(media_pos)

        if not self.mediaplayer.is_playing():
            self.timer.stop()
            if not self.is_paused:
                self.stop()

def main():
    app = QApplication(sys.argv)
    player = MediaPlayer()
    player.show() # Makes the player visible and interactive to user 
    player.resize(640, 480) # Set player window size
    sys.exit(app.exec())

if __name__ == "__main__":
    main()