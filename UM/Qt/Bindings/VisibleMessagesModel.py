from UM.Qt.ListModel import ListModel
from UM.Application import Application
from PyQt5.QtCore import Qt, pyqtSlot

class VisibleMessagesModel(ListModel):
    TextRole = Qt.UserRole + 1
    MaxProgressRole = Qt.UserRole + 2
    ProgressRole = Qt.UserRole + 3
    IDRole = Qt.UserRole + 4
    
    def __init__(self, parent = None):
        super().__init__(parent)
        Application.getInstance().visibleMessageAdded.connect(self.addMessage)
        Application.getInstance().visibleMessageRemoved.connect(self.removeMessage)
        self.addRoleName(self.TextRole, "text")
        self.addRoleName(self.MaxProgressRole, "max_progress")
        self.addRoleName(self.ProgressRole, "progress")
        self.addRoleName(self.IDRole, "id")
        self._populateMessageList()
    
    def _populateMessageList(self):
        for message in Application.getInstance().getVisibleMessages():
            self.addMessage(message)
    
    def addMessage(self, message):
        self.appendItem({
                'text': message.getText(),
                'progress': message.getProgress(),
                'max_progress': message.getMaxProgress(),
                'id': id(message)
            })
    
    @pyqtSlot("long")
    def hideMessage(self, message_id):
        Application.getInstance().hideMessageById(message_id)
    
    def removeMessage(self, message):
        message_id = id(message)
        for index in range(0,len(self.items)):
            if self.items[index]["id"] == message_id:
                self.removeItem(index)