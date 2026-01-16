#!/usr/bin/env python3
"""
D435 Stereo + Color + Depth Viewer - RealSense D435 좌우 IR + Color + Depth 뷰어 및 이미지 저장
ROS2 없이 순수 Python으로 실행 가능
"""

import sys
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5 import uic

# RealSense 라이브러리 (없으면 데모 모드)
try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
except ImportError:
    REALSENSE_AVAILABLE = False
    print("[Warning] pyrealsense2 not installed. Running in demo mode.")


class StereoViewer(QMainWindow):
    """D435 스테레오 + Color + Depth 뷰어 메인 윈도우"""

    def __init__(self):
        super().__init__()

        # UI 파일 경로 (스크립트 위치 기준)
        script_dir = Path(__file__).parent.resolve()
        ui_path = script_dir.parent / "ui" / "stereo_viewer.ui"

        if not ui_path.exists():
            raise FileNotFoundError(f"UI file not found: {ui_path}")

        uic.loadUi(str(ui_path), self)

        # 카메라 상태
        self.pipeline = None
        self.is_connected = False
        self.left_frame = None
        self.right_frame = None
        self.color_frame = None
        self.depth_frame = None
        self.depth_colormap = None

        # 해상도 옵션 (IR/Depth, Color, FPS)
        self.resolution_options = [
            {"name": "640x480 @ 30fps", "ir": (640, 480), "color": (640, 480), "depth": (640, 480), "fps": 30},
            {"name": "848x480 @ 30fps", "ir": (848, 480), "color": (848, 480), "depth": (848, 480), "fps": 30},
            {"name": "1280x720 @ 30fps", "ir": (1280, 720), "color": (1280, 720), "depth": (1280, 720), "fps": 30},
            {"name": "1280x720 @ 15fps", "ir": (1280, 720), "color": (1280, 720), "depth": (1280, 720), "fps": 15},
            {"name": "1920x1080 @ 30fps (Color only)", "ir": (1280, 720), "color": (1920, 1080), "depth": (1280, 720), "fps": 30},
        ]

        # 해상도 콤보박스 초기화
        for opt in self.resolution_options:
            self.resolutionComboBox.addItem(opt["name"])
        self.resolutionComboBox.setCurrentIndex(0)

        # 타이머 (30 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)

        # 기본 저장 경로
        default_path = script_dir.parent / "images"
        self.pathLineEdit.setText(str(default_path))

        # 시그널 연결
        self.connectButton.clicked.connect(self.toggle_connection)
        self.browseButton.clicked.connect(self.browse_folder)
        self.captureButton.clicked.connect(self.capture_all)

        # 스페이스바 단축키 (캡처)
        self.shortcut_capture = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.shortcut_capture.activated.connect(self.capture_all)

        self.statusbar.showMessage("Ready. Click 'Connect Camera' to start. Press SPACE to capture.")

    def toggle_connection(self):
        """카메라 연결/해제"""
        if self.is_connected:
            self.disconnect_camera()
        else:
            self.connect_camera()

    def connect_camera(self):
        """RealSense D435 연결"""
        if not REALSENSE_AVAILABLE:
            QMessageBox.warning(
                self, "Error",
                "pyrealsense2 not found.\n"
                "Install: pip install pyrealsense2"
            )
            return

        try:
            self.pipeline = rs.pipeline()
            config = rs.config()

            # 선택된 해상도 가져오기
            res_idx = self.resolutionComboBox.currentIndex()
            res = self.resolution_options[res_idx]
            ir_w, ir_h = res["ir"]
            color_w, color_h = res["color"]
            depth_w, depth_h = res["depth"]
            fps = res["fps"]

            # IR 스트림 (좌/우)
            config.enable_stream(rs.stream.infrared, 1, ir_w, ir_h, rs.format.y8, fps)
            config.enable_stream(rs.stream.infrared, 2, ir_w, ir_h, rs.format.y8, fps)
            # Color 스트림
            config.enable_stream(rs.stream.color, color_w, color_h, rs.format.bgr8, fps)
            # Depth 스트림
            config.enable_stream(rs.stream.depth, depth_w, depth_h, rs.format.z16, fps)

            self.pipeline.start(config)
            self.is_connected = True
            self.timer.start(33)

            # UI 상태 변경
            self.connectButton.setText("Disconnect")
            self.connectButton.setStyleSheet("background-color: #da3633;")
            self.statusLabel.setText("● Connected")
            self.statusLabel.setStyleSheet("color: #3fb950; font-weight: bold;")
            self.resolutionComboBox.setEnabled(False)
            self.statusbar.showMessage(f"Camera connected. Resolution: {res['name']}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed:\n{e}")
            self.pipeline = None

    def disconnect_camera(self):
        """카메라 해제"""
        self.timer.stop()
        if self.pipeline:
            self.pipeline.stop()
            self.pipeline = None

        self.is_connected = False
        self.left_frame = None
        self.right_frame = None
        self.color_frame = None
        self.depth_frame = None
        self.depth_colormap = None

        self.connectButton.setText("Connect Camera")
        self.connectButton.setStyleSheet("background-color: #2ea043;")
        self.statusLabel.setText("● Disconnected")
        self.statusLabel.setStyleSheet("color: #f85149; font-weight: bold;")
        self.resolutionComboBox.setEnabled(True)
        self.leftImageLabel.setText("No Image")
        self.rightImageLabel.setText("No Image")
        self.colorImageLabel.setText("No Image")
        self.depthImageLabel.setText("No Image")
        self.statusbar.showMessage("Camera disconnected.")

    def update_frames(self):
        """프레임 갱신"""
        if not self.is_connected or not self.pipeline:
            return

        try:
            frames = self.pipeline.wait_for_frames(timeout_ms=1000)

            # 좌측 IR
            left_ir = frames.get_infrared_frame(1)
            if left_ir:
                self.left_frame = np.asanyarray(left_ir.get_data())
                self.display_image(self.left_frame, self.leftImageLabel)

            # 우측 IR
            right_ir = frames.get_infrared_frame(2)
            if right_ir:
                self.right_frame = np.asanyarray(right_ir.get_data())
                self.display_image(self.right_frame, self.rightImageLabel)

            # Color
            color = frames.get_color_frame()
            if color:
                self.color_frame = np.asanyarray(color.get_data())
                self.display_image(self.color_frame, self.colorImageLabel, is_color=True)

            # Depth
            depth = frames.get_depth_frame()
            if depth:
                self.depth_frame = np.asanyarray(depth.get_data())
                # Depth를 컬러맵으로 변환 (시각화용)
                self.depth_colormap = cv2.applyColorMap(
                    cv2.convertScaleAbs(self.depth_frame, alpha=0.03),
                    cv2.COLORMAP_JET
                )
                self.display_image(self.depth_colormap, self.depthImageLabel, is_color=True)

        except Exception as e:
            self.statusbar.showMessage(f"Frame error: {e}")

    def draw_crosshair(self, frame):
        """이미지에 중심선(수평/수직) 표시"""
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2

        # 컬러 이미지로 변환 (그레이스케일인 경우)
        if len(frame.shape) == 2:
            frame_color = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        else:
            frame_color = frame.copy()

        # 수평선 (녹색)
        cv2.line(frame_color, (0, cy), (w, cy), (0, 255, 0), 1)
        # 수직선 (녹색)
        cv2.line(frame_color, (cx, 0), (cx, h), (0, 255, 0), 1)

        return frame_color

    def display_image(self, frame, label, is_color=False):
        """이미지를 QLabel에 표시"""
        if frame is None:
            return

        # 중심선 표시
        frame_with_cross = self.draw_crosshair(frame)

        # BGR to RGB 변환
        frame_rgb = cv2.cvtColor(frame_with_cross, cv2.COLOR_BGR2RGB)

        h, w, ch = frame_rgb.shape
        q_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img).scaled(
            label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        label.setPixmap(pixmap)

    def browse_folder(self):
        """폴더 선택"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", self.pathLineEdit.text())
        if folder:
            self.pathLineEdit.setText(folder)

    def get_save_path(self):
        """저장 경로 (없으면 생성)"""
        save_dir = Path(self.pathLineEdit.text())
        save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    def capture_all(self):
        """모든 이미지 저장 (좌/우 IR + Color + Depth)"""
        if self.left_frame is None or self.right_frame is None or self.color_frame is None or self.depth_frame is None:
            QMessageBox.warning(self, "Warning", "All images not available.")
            return

        save_dir = self.get_save_path()
        left_dir = save_dir / "left"
        right_dir = save_dir / "right"
        color_dir = save_dir / "color"
        depth_dir = save_dir / "depth"
        left_dir.mkdir(parents=True, exist_ok=True)
        right_dir.mkdir(parents=True, exist_ok=True)
        color_dir.mkdir(parents=True, exist_ok=True)
        depth_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

        # 좌/우 IR 저장
        cv2.imwrite(str(left_dir / f"{ts}.png"), self.left_frame)
        cv2.imwrite(str(right_dir / f"{ts}.png"), self.right_frame)

        # Color 저장
        cv2.imwrite(str(color_dir / f"{ts}.png"), self.color_frame)

        # Depth 저장 (16bit raw + colormap)
        cv2.imwrite(str(depth_dir / f"{ts}.png"), self.depth_frame)
        cv2.imwrite(str(depth_dir / f"{ts}_color.png"), self.depth_colormap)

        self.statusbar.showMessage(f"Saved: left/{ts}.png, right/{ts}.png, color/{ts}.png, depth/{ts}.png")

    def closeEvent(self, event):
        """종료 시 카메라 해제"""
        self.disconnect_camera()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = StereoViewer()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
