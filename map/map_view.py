# emp_planning_system/map/map_view.py
import os
import json
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from .bridge import Bridge # Import từ file cùng thư mục

class MapView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.channel = QWebChannel()
        # tạo một đối tượng Bridge
        self.bridge = Bridge()
        # dùng QWebChannel đăng ký đối tượng Bridge với tên "py_bridge" ở JS
        self.channel.registerObject("py_bridge", self.bridge)
        self.page().setWebChannel(self.channel)
        self._load_map()

    def _load_map(self):
        """
        Tải file HTML bản đồ từ thư mục web
        """
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        map_html_path = os.path.join(base_path, 'web', 'index.html')
        if os.path.exists(map_html_path):
            self.load(QUrl.fromLocalFile(map_html_path))
        else:
            print(f"Lỗi: Không tìm thấy file bản đồ tại: {map_html_path}")

    def run_js(self, script):
        self.page().runJavaScript(script)

    def add_object_to_map(self, obj):
        obj_json = json.dumps(obj.__dict__)
        # Kiểm tra sự tồn tại của thuộc tính 'power' để phân biệt EMP và Obstacle
        script = f"addEMPMarker({obj_json});" if hasattr(obj, 'power') else f"addObstacleShape({obj_json});"
        self.run_js(script)

    def remove_object_from_map(self, uuid):
        self.run_js(f"removeObject('{uuid}');")
    
    def clear_map(self):
        self.run_js("clearAllObjects();")

    def set_map_view(self, lat, lon, zoom):
        self.run_js(f"setMapView({lat}, {lon}, {zoom});")
        
    def request_map_view(self):
        self.run_js("getMapView();")

    def request_map_bounds(self):
        self.run_js("getMapBounds();")