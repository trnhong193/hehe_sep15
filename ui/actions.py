# emp_planning_system/ui/actions.py
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

def create_actions(parent):
    """Tạo một dictionary chứa tất cả các QAction của ứng dụng."""
    actions = {
        "new": QAction("&Dự án mới", parent),
        "open": QAction("&Mở dự án...", parent),
        "save": QAction("&Lưu dự án", parent),
        "save_as": QAction("Lưu thành...", parent),
        "exit": QAction("Thoát", parent),
        "add_emp": QAction("Thêm nguồn EMP", parent),
        "add_obstacle": QAction("Thêm vật cản", parent),
        "calculate": QAction("Tính toán vùng ảnh hưởng", parent),
        "report": QAction("Xuất báo cáo PDF", parent)
    }
    # Thêm phím tắt (shortcuts)
    actions["new"].setShortcut("Ctrl+N")
    actions["open"].setShortcut("Ctrl+O")
    actions["save"].setShortcut("Ctrl+S")
    actions["exit"].setShortcut("Ctrl+Q")
    
    return actions