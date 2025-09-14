# emp_planning_system/main.py

import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow

def main():
    # Mỗi ứng dụng PyQt cần một đối tượng QApplication
    app = QApplication(sys.argv)
    
    # Tạo một instance của cửa sổ chính
    main_win = MainWindow()
    
    # Hiển thị cửa sổ
    main_win.show()
    
    # Bắt đầu vòng lặp sự kiện của ứng dụng
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()