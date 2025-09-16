# emp_planning_system/map/bridge.py
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class Bridge(QObject):
    mapClicked = pyqtSignal(float, float)
    mapBoundsReceived = pyqtSignal(float, float, float, float)
    mapViewReceived = pyqtSignal(float, float, int)
    
    # <<< THÊM MỚI >>> Tín hiệu cho sự kiện chuột phải vào đối tượng trên bản đồ
    objectRightClicked = pyqtSignal(str, str) # uuid, object_type

    @pyqtSlot(float, float)
    def onMapClicked(self, lat, lon):
        self.mapClicked.emit(lat, lon)
    
    @pyqtSlot(float, float, float, float)
    def onMapBoundsReceived(self, s, w, n, e):
        self.mapBoundsReceived.emit(s, w, n, e)

    @pyqtSlot(float, float, int)
    def onMapViewReceived(self, lat, lon, zoom):
        self.mapViewReceived.emit(lat, lon, zoom)
        
    # <<< THÊM MỚI >>> Slot nhận sự kiện chuột phải từ JS
    @pyqtSlot(str, str)
    def onObjectRightClicked(self, uuid, object_type):
        self.objectRightClicked.emit(uuid, object_type)