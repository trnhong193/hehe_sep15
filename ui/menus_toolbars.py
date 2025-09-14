# emp_planning_system/ui/menus_toolbars.py
from PyQt5.QtWidgets import QToolBar

def create_menu_bar(main_window, actions):
    """
    Tạo menu bar cho cửa sổ chính với các menu và hành động đã định nghĩa.
    """
    menu_bar = main_window.menuBar()
    # Menu: Tệp tin
    file_menu = menu_bar.addMenu("&Tệp tin")
    file_menu.addAction(actions["new"])
    file_menu.addAction(actions["open"])
    file_menu.addAction(actions["save"])
    file_menu.addAction(actions["save_as"])
    file_menu.addSeparator()
    file_menu.addAction(actions["exit"])
    
    # Menu: Hành động
    action_menu = menu_bar.addMenu("&Hành động")
    action_menu.addAction(actions["add_emp"])
    action_menu.addAction(actions["add_obstacle"])
    action_menu.addSeparator()
    action_menu.addAction(actions["calculate"])
    action_menu.addAction(actions["report"])

def create_tool_bar(main_window, actions):
    """
    Tạo và điền dữ liệu cho thanh công cụ chính 
    """
    tool_bar = QToolBar("Thanh công cụ chính")
    main_window.addToolBar(tool_bar)
    
    tool_bar.addAction(actions["new"])
    tool_bar.addAction(actions["open"])
    tool_bar.addAction(actions["save"])
    tool_bar.addSeparator()
    tool_bar.addAction(actions["add_emp"])
    tool_bar.addAction(actions["add_obstacle"])
    tool_bar.addSeparator()
    tool_bar.addAction(actions["calculate"])
    tool_bar.addAction(actions["report"])