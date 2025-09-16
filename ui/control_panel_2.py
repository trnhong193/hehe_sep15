# emp_planning_system/ui/control_panel.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QFormLayout, 
                             QDoubleSpinBox, QTabWidget, QTableWidget, 
                             QLineEdit, QPushButton, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt

class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        general_group = self._create_general_group()
        
        self.tab_widget = QTabWidget()
        objects_tab = self._create_objects_tab()
        self.details_tab = self._create_details_tab()
        self.tab_widget.addTab(objects_tab, "Danh sách đối tượng")
        self.tab_widget.addTab(self.details_tab, "Thuộc tính")

        main_layout.addWidget(general_group)
        main_layout.addWidget(self.tab_widget)

    def _create_general_group(self):
        group_box = QGroupBox("Thiết lập chung")
        layout = QFormLayout()
        self.altitude_input = QDoubleSpinBox()
        self.altitude_input.setRange(-1000, 10000)
        self.altitude_input.setValue(5.0)
        self.altitude_input.setSuffix(" m")
        layout.addRow("Độ cao xét ảnh hưởng:", self.altitude_input)
        group_box.setLayout(layout)
        return group_box

    def _create_objects_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        emp_group = QGroupBox("Danh sách nguồn EMP")
        emp_layout = QVBoxLayout()
        self.emp_table = QTableWidget()
        self.emp_table.setColumnCount(3)
        self.emp_table.setHorizontalHeaderLabels(["Tên", "Vĩ độ", "Kinh độ"])
        self.emp_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.emp_table.setAlternatingRowColors(True)
        self.emp_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.emp_table.horizontalHeader().setStretchLastSection(True)
        emp_layout.addWidget(self.emp_table)
        emp_group.setLayout(emp_layout)
        
        obstacle_group = QGroupBox("Danh sách vật cản")
        obstacle_layout = QVBoxLayout()
        self.obstacle_table = QTableWidget()
        self.obstacle_table.setColumnCount(3)
        self.obstacle_table.setHorizontalHeaderLabels(["Tên", "Vĩ độ", "Kinh độ"])
        self.obstacle_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.obstacle_table.setAlternatingRowColors(True)
        self.obstacle_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.obstacle_table.horizontalHeader().setStretchLastSection(True)
        obstacle_layout.addWidget(self.obstacle_table)
        obstacle_group.setLayout(obstacle_layout)

        layout.addWidget(emp_group)
        layout.addWidget(obstacle_group)
        return tab

    def _create_details_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.details_group = QGroupBox("Thuộc tính")
        self.details_layout = QFormLayout()
        self.details_placeholder = QLabel("<i>Chọn một đối tượng từ danh sách để xem thuộc tính,\nhoặc chọn một hành động 'Thêm' để bắt đầu.</i>")
        self.details_placeholder.setAlignment(Qt.AlignCenter)
        self.details_placeholder.setWordWrap(True)
        self.details_layout.addWidget(self.details_placeholder)
        self.details_group.setLayout(self.details_layout)
        layout.addWidget(self.details_group)
        return tab

    def clear_details_form(self):
        old_widget = self.details_layout.itemAt(0).widget()
        if old_widget: old_widget.deleteLater()
        self.details_placeholder = QLabel("<i>Chọn một đối tượng từ danh sách để xem thuộc tính,\nhoặc chọn một hành động 'Thêm' để bắt đầu.</i>")
        self.details_placeholder.setAlignment(Qt.AlignCenter)
        self.details_placeholder.setWordWrap(True)
        self.details_layout.addWidget(self.details_placeholder)

    def populate_details_form(self, object_type, data_object=None, read_only=False):
        old_widget = self.details_layout.itemAt(0).widget()
        if old_widget: old_widget.deleteLater()

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Tạo và lưu trữ các widget input để logic có thể truy cập
        self.input_widgets = {}

        # Các trường chung
        self.input_widgets["name"] = QLineEdit(data_object.name if data_object else "", readOnly=read_only)
        self.input_widgets["lat"] = QLineEdit(f"{data_object.lat:.6f}" if data_object else "", readOnly=read_only)
        self.input_widgets["lon"] = QLineEdit(f"{data_object.lon:.6f}" if data_object else "", readOnly=read_only)

        form_layout.addRow("Tên:", self.input_widgets["name"])
        form_layout.addRow("Vĩ độ (Lat):", self.input_widgets["lat"])
        form_layout.addRow("Kinh độ (Lon):", self.input_widgets["lon"])
        
        # Các trường riêng
        if object_type == "EMP":
            self.details_group.setTitle("Chi tiết nguồn EMP")
            self.input_widgets["power"] = QLineEdit(str(data_object.power) if data_object else "1000", readOnly=read_only)
            self.input_widgets["frequency"] = QLineEdit(str(data_object.frequency) if data_object else "300", readOnly=read_only)
            self.input_widgets["height"] = QLineEdit(str(data_object.height) if data_object else "10", readOnly=read_only)
            form_layout.addRow("Công suất (W):", self.input_widgets["power"])
            form_layout.addRow("Tần số (MHz):", self.input_widgets["frequency"])
            form_layout.addRow("Độ cao lắp đặt (m):", self.input_widgets["height"])
        elif object_type == "OBSTACLE":
            self.details_group.setTitle("Chi tiết vật cản")
            self.input_widgets["length"] = QLineEdit(str(data_object.length) if data_object else "20", readOnly=read_only)
            self.input_widgets["width"] = QLineEdit(str(data_object.width) if data_object else "10", readOnly=read_only)
            self.input_widgets["height"] = QLineEdit(str(data_object.height) if data_object else "15", readOnly=read_only)
            form_layout.addRow("Chiều dài (m):", self.input_widgets["length"])
            form_layout.addRow("Chiều rộng (m):", self.input_widgets["width"])
            form_layout.addRow("Chiều cao (m):", self.input_widgets["height"])

        if not read_only:
            self.save_button = QPushButton("Lưu")
            self.cancel_button = QPushButton("Hủy")
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(self.save_button)
            btn_layout.addWidget(self.cancel_button)
            form_layout.addRow(btn_layout)

        self.details_layout.addWidget(form_widget)