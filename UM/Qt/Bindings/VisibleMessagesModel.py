# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Union

from PyQt6.QtCore import Qt, QUrl

from UM.Application import Application
from UM.FlameProfiler import pyqtSlot
from UM.Qt.ListModel import ListModel


class VisibleMessagesModel(ListModel):
    TextRole = Qt.ItemDataRole.UserRole + 1
    MaxProgressRole = Qt.ItemDataRole.UserRole + 2
    ProgressRole = Qt.ItemDataRole.UserRole + 3
    IDRole = Qt.ItemDataRole.UserRole + 4
    ActionsRole = Qt.ItemDataRole.UserRole + 5
    IconRole = Qt.ItemDataRole.UserRole + 6
    DescriptionRole = Qt.ItemDataRole.UserRole + 7
    DismissableRole = Qt.ItemDataRole.UserRole + 8
    TileRole = Qt.ItemDataRole.UserRole + 9
    StyleRole = Qt.ItemDataRole.UserRole + 10
    ImageSourceRole = Qt.ItemDataRole.UserRole + 11
    ImageCaptionRole = Qt.ItemDataRole.UserRole + 12
    OptionTextRole = Qt.ItemDataRole.UserRole + 13
    OptionStateRole = Qt.ItemDataRole.UserRole + 14
    MessageTypeRole = Qt.ItemDataRole.UserRole + 15

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
        self.addRoleName(self.MessageTypeRole, "message_type")
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
            "image_source": self.getImageSourceAsQUrl(message.getImageSource()),
            "image_caption": message.getImageCaption(),
            "option_text": message.getOptionText(),
            "option_state": message.getOptionState(),
            "message_type": int(message.getMessageType())
        })
        message.titleChanged.connect(self._onMessageTitleChanged)
        message.textChanged.connect(self._onMessageTextChanged)
        message.progressChanged.connect(self._onMessageProgress)

    @staticmethod
    def getImageSourceAsQUrl(image_source: Union[QUrl, str]) -> QUrl:
        if type(image_source) is str:
            return QUrl.fromLocalFile(image_source)
        elif type(image_source) is QUrl:
            return image_source
        return QUrl.fromLocalFile("")

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
