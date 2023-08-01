from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty

from typing import Optional

class ShakeDetector(QObject):
    shakeDetected = pyqtSignal()
    pointChanged = pyqtSignal()

    def getPoint(self) -> Optional["QPoint"]:
        return self._curr_pos

    def setPoint(self, point: "QPoint"):
        self._curr_pos = point
        self.pointChanged.emit()

    position = pyqtProperty('QPoint', fget=getPoint, fset=setPoint, notify=pointChanged)

    def __init__(self, _parent = None):
        super().__init__()

        self._curr_pos = None
        self._prev_pos = None
        self.threshold = 50
        self.shake_count = 0
        self.number_of_shakes = 0

        self.pointChanged.connect(self._checkForShake)

    def _checkForShake(self):
        if self._prev_pos is not None:
            # Calculate the distance moved between the previous and current positions
            distance = ((self._curr_pos.x() - self._prev_pos.x()) ** 2 + (self._curr_pos.y() - self._curr_pos.y()) ** 2) ** 0.5
            # If the distance is greater than a threshold, emit the shakeDetected signal
            if distance > self.threshold:
                self.shake_count += 1
                if self.shake_count > 10:
                    self.shake_count = 0
                    self.number_of_shakes += 1
                    self.shakeDetected.emit()

        # Update the previous position with the current one
        self._prev_pos = self._curr_pos

    @pyqtProperty(int, notify = shakeDetected)
    def shakeIsdetected(self):
        return self.number_of_shakes