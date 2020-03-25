# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt

from UM.Application import Application
from UM.FlameProfiler import pyqtSlot
from UM.Qt.ListModel import ListModel


class VisibleMessagesModel(ListModel):
    TextRole = Qt.UserRole + 1
    MaxProgressRole = Qt.UserRole + 2
    ProgressRole = Qt.UserRole + 3
    IDRole = Qt.UserRole + 4
    ActionsRole = Qt.UserRole + 5
    IconRole = Qt.UserRole + 6
    DescriptionRole = Qt.UserRole + 7
    DismissableRole = Qt.UserRole + 8
    TileRole = Qt.UserRole + 9
    StyleRole = Qt.UserRole + 10
    ImageSourceRole = Qt.UserRole + 11
    ImageCaptionRole = Qt.UserRole + 12
    OptionTextRole = Qt.UserRole + 13
    OptionStateRole = Qt.UserRole + 14

    def __init__(self, parent=None):
        super().__init__(parent)
        Application.getInstance().visibleMessageAdded.connect(self.addMessage)
        Application.getInstance().visibleMessageRemoved.connect(self.removeMessage)
        self.addRoleName(self.TextRole, "text")
        self.addRoleName(self.MaxProgressRole, "max_progress")
        self.addRoleName(self.ProgressRole, "progress")
        self.addRoleName(self.IDRole, "id")
        self.addRoleName(self.ActionsRole, "actions")
        self.addRoleName(self.DismissableRole, "dismissable")
        self.addRoleName(self.TileRole, "title")
        self.addRoleName(self.ImageSourceRole, "image_source")
        self.addRoleName(self.ImageCaptionRole, "image_caption")
        self.addRoleName(self.OptionTextRole, "option_text")
        self.addRoleName(self.OptionStateRole, "option_state")
        self._populateMessageList()

    def _populateMessageList(self):
        for message in Application.getInstance().getVisibleMessages():
            self.addMessage(message)

    def addMessage(self, message):
        self.appendItem({
            "text": message.getText(),
            "progress": message.getProgress(),
            "max_progress": message.getMaxProgress(),
            "id": str(id(message)),
            "actions": self.createActionsModel(message.getActions()),
            "dismissable": message.isDismissable(),
            "title": message.getTitle(),
            "image_source": message.getImageSource(),
            "image_caption": message.getImageCaption(),
            "option_text": message.getOptionText(),
            "option_state": message.getOptionState()
        })
        message.titleChanged.connect(self._onMessageTitleChanged)
        message.textChanged.connect(self._onMessageTextChanged)
        message.progressChanged.connect(self._onMessageProgress)

    def createActionsModel(self, actions):
        model = ListModel()
        model.addRoleName(self.IDRole, "action_id")
        model.addRoleName(self.TextRole,"name")
        model.addRoleName(self.IconRole, "icon")
        model.addRoleName(self.DescriptionRole, "description")
        model.addRoleName(self.StyleRole, "button_style")

        for action in actions:
            model.appendItem(action)
        return model

    @pyqtSlot(str)
    def hideMessage(self, message_id):
        Application.getInstance().hideMessageById(message_id)

    @pyqtSlot(str, bool)
    def optionToggled(self, message_id, value):
        for message in Application.getInstance().getVisibleMessages():
            if str(id(message)) == message_id:
                message.optionToggled.emit(value)
                break

    @pyqtSlot(str, str)
    def actionTriggered(self, message_id, action_id):
        for message in Application.getInstance().getVisibleMessages():
            if str(id(message)) == message_id:
                message.actionTriggered.emit(message, action_id)
                break

    def removeMessage(self, message):
        message_id = str(id(message))
        for index in range(0,len(self.items)):
            if self.items[index]["id"] == message_id:
                self.removeItem(index)
                break

    def _onMessageTitleChanged(self, message):
        index = self.find("id", str(id(message)))

        if index != -1:
            self.setProperty(index, "title", message.getTitle())

    def _onMessageTextChanged(self, message):
        index = self.find("id", str(id(message)))

        if index != -1:
            self.setProperty(index, "text", message.getText())

    def _onMessageProgress(self, message):
        index = self.find("id", str(id(message)))

        if index != -1:
            self.setProperty(index, "progress", message.getProgress())
