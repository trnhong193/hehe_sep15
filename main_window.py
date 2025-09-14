# # emp_planning_system/main_window.py

# from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QStatusBar
# from PyQt5.QtCore import Qt

# # Import từ các module đã được tái cấu trúc
# from ui.actions import create_actions
# from ui.menus_toolbars import create_menu_bar, create_tool_bar
# from ui.control_panel import ControlPanel
# from map.map_view import MapView
# from core.application import ApplicationLogic

# class MainWindow(QMainWindow):
#     def __init__(self, parent=None):
#         super().__init__(parent)
        
#         # 1. Khởi tạo các thành phần giao diện
#         self.actions = create_actions(self)
#         create_menu_bar(self, self.actions)
#         create_tool_bar(self, self.actions)
#         self.setStatusBar(QStatusBar(self))

#         # 2. Thiết lập layout chính
#         main_widget = QWidget()
#         self.setCentralWidget(main_widget)
#         layout = QHBoxLayout(main_widget)
#         splitter = QSplitter(Qt.Horizontal)
        
#         self.control_panel = ControlPanel()
#         self.map_view = MapView()

#         splitter.addWidget(self.control_panel)
#         splitter.addWidget(self.map_view)
#         splitter.setSizes([450, 990])
#         layout.addWidget(splitter)
        
#         # 3. Khởi tạo và kết nối "bộ não" logic
#         # Lớp ApplicationLogic sẽ xử lý tất cả các sự kiện
#         self.app_logic = ApplicationLogic(self)

#     def closeEvent(self, event):
#         """Được gọi khi người dùng đóng cửa sổ."""
#         # Hỏi ý kiến của bộ não xem có được phép đóng không
#         if self.app_logic.check_dirty_and_save():
#             event.accept()
#         else:
#             event.ignore()


# emp_planning_system/main_window.py

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QStatusBar
from PyQt5.QtCore import Qt

from ui.actions import create_actions
from ui.menus_toolbars import create_menu_bar, create_tool_bar
from ui.control_panel import ControlPanel
from map.map_view import MapView
from core.application import ApplicationLogic

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hệ thống Hỗ trợ Quy hoạch và Cảnh báo EMP")
        self.setGeometry(100, 100, 1440, 800)
        self.actions = create_actions(self)
        create_menu_bar(self, self.actions)
        create_tool_bar(self, self.actions)
        self.setStatusBar(QStatusBar(self))
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        splitter = QSplitter(Qt.Horizontal)
        self.control_panel = ControlPanel()
        self.map_view = MapView()
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.map_view)
        splitter.setSizes([450, 990])
        layout.addWidget(splitter)
        self.app_logic = ApplicationLogic(self)

    def closeEvent(self, event):
        if self.app_logic.check_dirty_and_save():
            event.accept()
        else:
            event.ignore()