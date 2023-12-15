import sys
import time
import vlc
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QSlider, QLabel
# Reference sources:
# vlc tutorial: https://www.geeksforgeeks.org/python-vlc-mediaplayer-getting-media/
# vlc doc: https://www.olivieraubert.net/vlc/python-ctypes/doc/
# PyQt tutorial: https://coderslegacy.com/python/pyqt5-tutorial/

class VideoPlayer(QWidget):
    def __init__(self, video_path, start_frame):
        super().__init__()

        self.setWindowTitle(video_path.split("/")[-1] + " frame: " + str(start_frame))
        self.resetButton = QPushButton('Reset')
        self.playButton = QPushButton('Play')
        self.pauseButton = QPushButton('Pause')
        self.slider = QSlider(Qt.Horizontal)
        self.timer = QTimer(self)
        self.timeLabel = QLabel('00:00:00/00:00:00')

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.videoFrame = QFrame(self)
        self.set_video_frame_handle()
        self.media = self.instance.media_new(video_path)
        self.player.set_media(self.media)

        self.start_time = 0
        self.player.play()
        time.sleep(0.1)
        self.player.pause()
        self.duration = self.player.get_length()
        self.slider.setRange(0, self.player.get_length())
        frame_rate = self.player.get_fps()
        if frame_rate > 0:
            self.start_time = (start_frame / frame_rate) * 1000
            self.player.set_time(int(self.start_time))

        self.setFocusPolicy(Qt.StrongFocus)
        self.init_ui()
        self.player.play()

    def init_ui(self):
        self.resetButton.clicked.connect(self.reset_video)
        self.playButton.clicked.connect(self.play_video)
        self.pauseButton.clicked.connect(self.pause_video)
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        # Please do NOT change the slider too frequently, or it could
        # overload the buffer.
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_slider)
        self.timer.start()

        hbox = QHBoxLayout()
        hbox.addWidget(self.resetButton)
        hbox.addWidget(self.playButton)
        hbox.addWidget(self.pauseButton)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.slider)
        hbox2.addWidget(self.timeLabel)
        self.timeLabel.setFixedHeight(10)

        vbox = QVBoxLayout()
        vbox.addWidget(self.videoFrame)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setGeometry(100, 100, 392, 410)
        self.show()

    def set_video_frame_handle(self):
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.player.set_xwindow(self.videoFrame.winId())
        elif sys.platform == "win32":  # for Windows
            self.player.set_hwnd(self.videoFrame.winId())
        elif sys.platform == "darwin":  # for macOS
            self.player.set_nsobject(int(self.videoFrame.winId()))

    def play_video(self):
        if self.player.get_state() == vlc.State.Ended or self.player.get_time() >= self.duration or self.player.get_time() == -1:
            # If the video finished playing, reset the player
            self.player.stop()
            self.player.play()
            self.player.pause()
        self.player.play()

    def pause_video(self):
        self.player.pause()

    def reset_video(self):
        if self.player.get_state() == vlc.State.Ended or self.player.get_time() >= self.duration or self.player.get_time() == -1:
            # If the video finished playing, reset the player
            self.player.stop()
            self.player.play()
        self.player.pause()
        self.player.set_time(int(self.start_time))
        self.player.play()

    def on_slider_pressed(self):
        position = self.slider.value()
        self.set_position(position)
        self.player.play()

    def set_position(self, position):
        if self.duration - position <= 1000:
            # To prevent deadlock of the buffer
            position = self.duration - 1000
        if self.player.get_state() == vlc.State.Ended or self.player.get_time() >= self.duration or self.player.get_time() == -1:
            # If the video finished playing, reset the player
            self.player.stop()
            self.player.play()
            self.player.pause()
        self.player.set_time(position)

    @staticmethod
    def format_time(ms):
        seconds = int(ms / 1000)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

    def update_time_label(self, current_time, total_duration):
        current_time_str = self.format_time(current_time)
        total_duration_str = self.format_time(total_duration)
        self.timeLabel.setText(f'{current_time_str}/{total_duration_str}')

    def update_slider(self):
        media_pos = self.player.get_time()
        self.slider.setValue(media_pos)
        self.update_time_label(media_pos, self.duration)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.move_one_frame(True)
        elif key == Qt.Key_Right:
            self.move_one_frame()
        else:
            super(VideoPlayer, self).keyPressEvent(event)

    def move_one_frame(self, backward=False):
        # Sometimes it requires pressing the key multiple times
        # before it updates the frame.
        # This is due to the nature of the time-based player.
        frame_time = 1000 / self.player.get_fps()
        current_time = self.player.get_time()
        if self.player.get_state() == vlc.State.Playing:
            self.player.pause()

        if backward:
            new_time = max(0, current_time - frame_time)
        else:
            new_time = min(self.duration, current_time + frame_time)

        self.player.set_time(int(new_time))
        self.slider.setValue(int(new_time))
        self.update_time_label(int(new_time), self.duration)

    def closeEvent(self, event):
        self.timer.stop()
        self.player.stop()
        self.player.release()
        self.instance.release()


def display_video(video_path, start_frame):
    app = QApplication(sys.argv)
    player = VideoPlayer(video_path, start_frame)
    sys.exit(app.exec_())


if __name__ == '__main__':
    display_video('..Videos/video6.mp4', 12240)
