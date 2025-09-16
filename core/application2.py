# emp_planning_system/core/application.py

import os
from datetime import datetime
import json
# from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem, QMenu, QProgressDialog
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
import uuid 
from data_models import EMP, Obstacle
from project_manager import save_project, load_project
from calculations import calculate_emp_field
from report_generator import generate_report

class ApplicationLogic:
    def __init__(self, main_window):
        self.main_window = main_window
        self.control_panel = main_window.control_panel
        self.map_view = main_window.map_view
        
        self.current_mode = None
        self.current_edit_uuid = None
        self.emp_sources = {}
        self.obstacles = {}
        self.current_project_path = None
        self.is_dirty = False
        self._save_path_pending = None
        self.current_map_state = {"center": [21.0285, 105.8542], "zoom": 13}

        self._connect_signals()
        self.main_window.statusBar().showMessage("Sẵn sàng.")

    def _connect_signals(self):
        actions = self.main_window.actions
        actions["new"].triggered.connect(self.new_project)
        actions["open"].triggered.connect(self.open_project)
        actions["save"].triggered.connect(self.save_project)
        actions["save_as"].triggered.connect(self.save_project_as)
        actions["exit"].triggered.connect(self.main_window.close)
        actions["add_emp"].triggered.connect(self.enter_add_emp_mode)
        actions["add_obstacle"].triggered.connect(self.enter_add_obstacle_mode)
        actions["calculate"].triggered.connect(self.trigger_calculation)
        actions["report"].triggered.connect(self.export_report)

        self.map_view.bridge.mapClicked.connect(self.on_map_clicked)
        self.map_view.bridge.mapBoundsReceived.connect(self.on_map_bounds_received)
        self.map_view.bridge.mapViewReceived.connect(self.on_map_view_received)
        
        self.control_panel.emp_table.itemClicked.connect(self.on_table_item_clicked)
        self.control_panel.emp_table.itemDoubleClicked.connect(self.on_table_item_double_clicked)
        self.control_panel.emp_table.customContextMenuRequested.connect(lambda pos: self.show_table_context_menu(self.control_panel.emp_table, pos))
        self.control_panel.obstacle_table.itemClicked.connect(self.on_table_item_clicked)
        self.control_panel.obstacle_table.itemDoubleClicked.connect(self.on_table_item_double_clicked)
        self.control_panel.obstacle_table.customContextMenuRequested.connect(lambda pos: self.show_table_context_menu(self.control_panel.obstacle_table, pos))

    def _get_object_by_uuid(self, uuid):
        return self.emp_sources.get(uuid) or self.obstacles.get(uuid)

    def _update_window_title(self):
        title = "Hệ thống Hỗ trợ Quy hoạch và Cảnh báo EMP"
        project_name = os.path.basename(self.current_project_path) if self.current_project_path else "Dự án mới"
        dirty_marker = "*" if self.is_dirty else ""
        self.main_window.setWindowTitle(f"{project_name}{dirty_marker} - {title}")

    def on_map_clicked(self, lat, lon):
        if self.current_mode in ["ADD_EMP", "ADD_OBSTACLE"]:
            # --- SỬA LỖI Ở ĐÂY ---
            # Truy cập trực tiếp vào các widget đã được lưu
            if hasattr(self.control_panel, 'input_widgets'):
                self.control_panel.input_widgets["lat"].setText(f"{lat:.6f}")
                self.control_panel.input_widgets["lon"].setText(f"{lon:.6f}")
                self.main_window.statusBar().showMessage(f"Đã chọn tọa độ. Vui lòng nhập thông tin.")
                self.control_panel.input_widgets["name"].setFocus()

    def on_table_item_clicked(self, item):
        uuid = item.data(Qt.UserRole)
        obj = self._get_object_by_uuid(uuid)
        if obj:
            self.cancel_details_form()
            self.control_panel.tab_widget.setCurrentWidget(self.control_panel.details_tab)
            obj_type = "EMP" if isinstance(obj, EMP) else "OBSTACLE"
            self.control_panel.populate_details_form(obj_type, obj, read_only=True)
            self.map_view.set_map_view(obj.lat, obj.lon, self.current_map_state.get('zoom', 15))

    def on_table_item_double_clicked(self, item):
        self.enter_edit_mode(item.tableWidget(), item)

    def show_table_context_menu(self, table, position):
        item = table.itemAt(position)
        if not item: return
        menu = QMenu()
        edit_action = menu.addAction("Sửa...")
        delete_action = menu.addAction("Xóa")
        action = menu.exec_(table.mapToGlobal(position))
        if action == edit_action:
            self.enter_edit_mode(table, item)
        elif action == delete_action:
            self.delete_object(table, item)

    def enter_add_emp_mode(self):
        self.cancel_details_form()
        self.current_mode = "ADD_EMP"
        self.main_window.statusBar().showMessage("Chế độ thêm nguồn EMP: Click lên bản đồ.")
        self.control_panel.populate_details_form("EMP")
        self.control_panel.tab_widget.setCurrentWidget(self.control_panel.details_tab)
        self.control_panel.save_button.clicked.connect(self.save_object)
        self.control_panel.cancel_button.clicked.connect(self.cancel_details_form)

    def enter_add_obstacle_mode(self):
        self.cancel_details_form()
        self.current_mode = "ADD_OBSTACLE"
        self.main_window.statusBar().showMessage("Chế độ thêm vật cản: Click lên bản đồ.")
        self.control_panel.populate_details_form("OBSTACLE")
        self.control_panel.tab_widget.setCurrentWidget(self.control_panel.details_tab)
        self.control_panel.save_button.clicked.connect(self.save_object)
        self.control_panel.cancel_button.clicked.connect(self.cancel_details_form)

    def enter_edit_mode(self, table, item):
        uuid = item.data(Qt.UserRole)
        obj = self._get_object_by_uuid(uuid)
        if not obj: return
        self.current_edit_uuid = uuid
        obj_type = "EMP" if isinstance(obj, EMP) else "OBSTACLE"
        self.current_mode = f"EDIT_{obj_type}"
        self.control_panel.populate_details_form(obj_type, obj)
        self.control_panel.tab_widget.setCurrentWidget(self.control_panel.details_tab)
        self.control_panel.save_button.clicked.connect(self.save_object)
        self.control_panel.cancel_button.clicked.connect(self.cancel_details_form)

    def save_object(self):
        form_widget = self.control_panel.details_layout.itemAt(0).widget()
        if not hasattr(self.control_panel, 'input_widgets'): return
        inputs = self.control_panel.input_widgets
        
        try:
            name = inputs["name"].text().strip()
            if not name:
                QMessageBox.warning(self.main_window, "Thiếu thông tin", "Tên đối tượng không được để trống.")
                return
            lat = float(inputs["lat"].text())
            lon = float(inputs["lon"].text())
            
            uuid_to_save = self.current_edit_uuid if self.current_mode.startswith("EDIT") else str(uuid.uuid4())
            
            if self.current_mode in ["ADD_EMP", "EDIT_EMP"]:
                obj = EMP(name=name, lat=lat, lon=lon,
                          power=float(inputs["power"].text()),
                          frequency=float(inputs["frequency"].text()),
                          height=float(inputs["height"].text()))
                obj.uuid = uuid_to_save
                self.emp_sources[obj.uuid] = obj
            elif self.current_mode in ["ADD_OBSTACLE", "EDIT_OBSTACLE"]:
                obj = Obstacle(name=name, lat=lat, lon=lon,
                               length=float(inputs["length"].text()),
                               width=float(inputs["width"].text()),
                               height=float(inputs["height"].text()))
                obj.uuid = uuid_to_save
                self.obstacles[obj.uuid] = obj
            
            self.map_view.add_object_to_map(obj)
            self._refresh_object_tables()
            self.is_dirty = True
            self._update_window_title()
            self.cancel_details_form()
            self.control_panel.tab_widget.setCurrentIndex(0)
        except (ValueError, AttributeError):
            QMessageBox.warning(self.main_window, "Lỗi Nhập liệu", "Vui lòng nhập đúng định dạng số cho các thông số.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi không xác định", f"Đã có lỗi xảy ra: {e}")

    def delete_object(self, table, item):
        uuid = item.data(Qt.UserRole)
        name = item.text()
        reply = QMessageBox.question(self.main_window, 'Xác nhận xóa', f"Bạn có chắc chắn muốn xóa '{name}' không?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if table is self.control_panel.emp_table and uuid in self.emp_sources: del self.emp_sources[uuid]
            elif table is self.control_panel.obstacle_table and uuid in self.obstacles: del self.obstacles[uuid]
            self.map_view.remove_object_from_map(uuid)
            self._refresh_object_tables()
            self.cancel_details_form()
            self.is_dirty = True
            self._update_window_title()

    def cancel_details_form(self):
        self.current_mode = None
        self.current_edit_uuid = None
        self.control_panel.clear_details_form()
        self.main_window.statusBar().showMessage("Sẵn sàng.")

    def new_project(self):
        if not self.check_dirty_and_save(): return
        self.emp_sources.clear()
        self.obstacles.clear()
        self.map_view.clear_map()
        self._refresh_object_tables()
        self.cancel_details_form()
        self.current_project_path = None
        self.is_dirty = False
        self._update_window_title()
        self.main_window.statusBar().showMessage("Đã tạo dự án mới.")

    def open_project(self):
        if not self.check_dirty_and_save(): return
        path, _ = QFileDialog.getOpenFileName(self.main_window, "Mở dự án", "", "EMP Project Files (*.emp_proj);;All Files (*)")
        if path:
            success, data = load_project(path)
            if success:
                self.new_project()
                self.emp_sources = data.get('emps', {})
                self.obstacles = data.get('obstacles', {})
                self._refresh_object_tables()
                for obj in self.emp_sources.values(): self.map_view.add_object_to_map(obj)
                for obj in self.obstacles.values(): self.map_view.add_object_to_map(obj)
                map_state = data.get('map_state')
                if map_state: self.map_view.set_map_view(map_state['center'][0], map_state['center'][1], map_state['zoom'])
                self.current_project_path = path
                self.is_dirty = False
                self._update_window_title()
                self.main_window.statusBar().showMessage(f"Đã mở dự án: {path}")
            else:
                QMessageBox.critical(self.main_window, "Lỗi", data)

    def save_project(self):
        if not self.current_project_path: return self.save_project_as()
        self.main_window.statusBar().showMessage("Đang lấy trạng thái bản đồ để lưu...")
        self._save_path_pending = self.current_project_path
        self.map_view.request_map_view()
        return True

    def save_project_as(self):
        path, _ = QFileDialog.getSaveFileName(self.main_window, "Lưu dự án thành", "Dự án EMP mới.emp_proj", "EMP Project Files (*.emp_proj);;All Files (*)")
        if path:
            self._save_path_pending = path
            self.map_view.request_map_view()
            return True
        return False
    
    def on_map_view_received(self, lat, lon, zoom):
        self.current_map_state = {"center": [lat, lon], "zoom": zoom}
        if self._save_path_pending:
            success, message = save_project(self._save_path_pending, self.emp_sources, self.obstacles, self.current_map_state)
            if success:
                self.is_dirty = False
                self.current_project_path = self._save_path_pending
                self._update_window_title()
                self.main_window.statusBar().showMessage(message)
            else:
                QMessageBox.critical(self.main_window, "Lỗi", message)
            self._save_path_pending = None

    def check_dirty_and_save(self):
        if not self.is_dirty: return True
        reply = QMessageBox.question(self.main_window, 'Lưu thay đổi?', 'Dự án của bạn có những thay đổi chưa được lưu. Bạn có muốn lưu lại không?', QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
        if reply == QMessageBox.Cancel: return False
        if reply == QMessageBox.Save: return self.save_project()
        return True

    def trigger_calculation(self):
        if not self.emp_sources:
            QMessageBox.information(self.main_window, "Thông báo", "Chưa có nguồn EMP nào để tính toán.")
            return
        self.progress_dialog = QProgressDialog("Đang yêu cầu thông tin bản đồ...", "Hủy", 0, 100, self.main_window)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setValue(5)
        self.progress_dialog.show()
        self.map_view.request_map_bounds()

    def on_map_bounds_received(self, s, w, n, e):
        self.progress_dialog.setLabelText("Đang tính toán, vui lòng chờ...")
        self.progress_dialog.setValue(20)
        bounds = {'lat_min': s, 'lon_min': w, 'lat_max': n, 'lon_max': e}
        user_altitude = self.control_panel.altitude_input.value()
        QTimer.singleShot(50, lambda: self._perform_calculation(bounds, user_altitude))

    def _perform_calculation(self, bounds, user_altitude):
        try:
            grid_data = calculate_emp_field(list(self.emp_sources.values()), list(self.obstacles.values()), user_altitude, bounds, grid_size=(200, 200))
            self.progress_dialog.setValue(70)
            self._create_heatmap_image_with_contours(grid_data)
            self.progress_dialog.setValue(90)
            self.map_view.run_js(f"updateOverlayImage('temp_overlay.png', {bounds['lat_min']}, {bounds['lon_min']}, {bounds['lat_max']}, {bounds['lon_max']});")
            self.progress_dialog.setValue(100)
        except Exception as e:
            QMessageBox.critical(self.main_window, "Lỗi Tính toán", f"Đã có lỗi xảy ra: {e}")
        finally:
            if hasattr(self, 'progress_dialog'): self.progress_dialog.close()

    def _create_heatmap_image_with_contours(self, grid_data):
        try:
            levels = [10, 50]
            colors = ['#FFD700', '#FF4500']
            if np.max(grid_data) < levels[0]: return
            height, width = grid_data.shape
            fig = plt.figure(figsize=(width / 100.0, height / 100.0), dpi=100)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')
            smoothed_grid = zoom(grid_data, 3, order=1)
            ax.contourf(smoothed_grid, levels=levels, colors=colors, alpha=0.5, extend='max', origin='lower')
            ax.contour(smoothed_grid, levels=levels, colors='black', linewidths=0.7, origin='lower')
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            save_path = os.path.join(base_path, 'web', 'temp_overlay.png')
            fig.savefig(save_path, transparent=True, dpi=100)
            plt.close(fig)
        except Exception as e:
            print(f"Lỗi khi tạo heatmap: {e}")

    def export_report(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_path, 'web', 'temp_overlay.png')
        if not os.path.exists(image_path):
            QMessageBox.warning(self.main_window, "Thiếu dữ liệu", "Vui lòng chạy 'Tính toán' trước khi xuất báo cáo.")
            return
        default_filename = f"BaoCao_EMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        save_path, _ = QFileDialog.getSaveFileName(self.main_window, "Lưu báo cáo PDF", default_filename, "PDF Files (*.pdf)")
        if save_path:
            report_data = {'emps': list(self.emp_sources.values()), 'obstacles': list(self.obstacles.values()), 'image_path': image_path, 'altitude': self.control_panel.altitude_input.value()}
            success, message = generate_report(save_path, report_data)
            if success:
                QMessageBox.information(self.main_window, "Thành công", message)
            else:
                QMessageBox.critical(self.main_window, "Thất bại", message)

    def _refresh_object_tables(self):
        self.control_panel.emp_table.setRowCount(0)
        for uuid, emp in self.emp_sources.items():
            row = self.control_panel.emp_table.rowCount()
            self.control_panel.emp_table.insertRow(row)
            name_item = QTableWidgetItem(emp.name)
            name_item.setData(Qt.UserRole, uuid)
            self.control_panel.emp_table.setItem(row, 0, name_item)
            self.control_panel.emp_table.setItem(row, 1, QTableWidgetItem(f"{emp.lat:.6f}"))
            self.control_panel.emp_table.setItem(row, 2, QTableWidgetItem(f"{emp.lon:.6f}"))
        self.control_panel.obstacle_table.setRowCount(0)
        for uuid, obs in self.obstacles.items():
            row = self.control_panel.obstacle_table.rowCount()
            self.control_panel.obstacle_table.insertRow(row)
            name_item = QTableWidgetItem(obs.name)
            name_item.setData(Qt.UserRole, uuid)
            self.control_panel.obstacle_table.setItem(row, 0, name_item)
            self.control_panel.obstacle_table.setItem(row, 1, QTableWidgetItem(f"{obs.lat:.6f}"))
            self.control_panel.obstacle_table.setItem(row, 2, QTableWidgetItem(f"{obs.lon:.6f}"))