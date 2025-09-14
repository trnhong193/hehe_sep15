# emp_planning_system/map/bridge.py
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class Bridge(QObject):
    """
    Lớp cầu nối giao tieeps 2 chiều Python <-> JavaScript (Leaflet)
    Các hàm @pyqtSlot sẽ được gọi từ JS
    Các pystSignal được phát ra để ApplicationLogic lắng nghe
    """
    # Tín hiệu phát ra khi người dùng click vào bản đồ
    mapClicked = pyqtSignal(float, float)
    # Tín hiệu phát ra khi nhận được thông tin 4 góc bản đồ (để tính toán)
    mapBoundsReceived = pyqtSignal(float, float, float, float)
    # Tín hiệu phát ra khi nhận được vị trí trung tâm và mức zoom hiện tại của bản đồ(để lưu file)
    mapViewReceived = pyqtSignal(float, float, int)

    @pyqtSlot(float, float)
    def onMapClicked(self, lat, lon):
        # Được gọi từ JS khi người dùng click vào bản đồ
        self.mapClicked.emit(lat, lon)
    
    @pyqtSlot(float, float, float, float)
    def onMapBoundsReceived(self, s, w, n, e):
        # Được gọi từ JS khi Python yêu cầu lấy giới hạn bản đồ
        self.mapBoundsReceived.emit(s, w, n, e)

    @pyqtSlot(float, float, int)
    def onMapViewReceived(self, lat, lon, zoom):
        # Được gọi từ JS khi Python yêu cầu lấy vị trí và mức zoom hiện tại của bản đồ
        self.mapViewReceived.emit(lat, lon, zoom)