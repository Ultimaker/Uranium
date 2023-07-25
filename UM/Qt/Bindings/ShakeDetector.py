
from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot


class ShakeDetector(QObject):

    shakeDetected = pyqtSignal()
    def __init__(self, parent = None):
        super().__init__()
        self.prev_pos = None
        self.threshold = 5
        self.shake_count = 0
        self.number_of_shakes = 0

    @pyqtSlot(int, int)
    def checkForShake(self, x, y):

        if self.prev_pos is not None:
            # Calculate the distance moved between the previous and current positions
            distance = ((x - self.prev_pos[0]) ** 2 + (y - self.prev_pos[1]) ** 2) ** 0.5
            # If the distance is greater than a threshold, emit the shakeDetected signal
            if distance > self.threshold:
                self.shake_count += 1
                if self.shake_count > 3:
                    self.shake_count = 0
                    self.number_of_shakes +=1
                    self.shakeDetected.emit()

        # Update the previous position with the current one
        self.prev_pos = (x, y)

    @pyqtProperty(int, notify = shakeDetected)
    def shakeIsdetected(self):
        return self.number_of_shakes