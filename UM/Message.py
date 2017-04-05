# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Application import Application
from UM.Signal import Signal, signalemitter


## Class for displaying messages to the user.
@signalemitter
class Message:
    ##  Class for displaying messages to the user.
    #   \param text Text that needs to be displayed in the message
    #   \param lifetime How long should the message be displayed (in seconds).
    #                   if lifetime is 0, it will never automatically be destroyed.
    #   \param dismissible Can the user dismiss the message?
    #   \progress Is there nay progress to be displayed? if -1, it's seen as indeterminate
    def __init__(self, text = "", lifetime = 30, dismissable = True, progress = None): #pylint: disable=bad-whitespace
        super().__init__()
        self._application = Application.getInstance()
        self._visible = False
        self._text = text
        self._progress = progress # If progress is set to -1, the progress is seen as indeterminate
        self._max_progress = 100
        self._lifetime = lifetime
        self._lifetime_timer = None
        self._dismissable = dismissable # Can the message be closed by user?
        self._actions = []

    actionTriggered = Signal()

    ##  Show the message (if not already visible)
    def show(self):
        if not self._visible:
            self._visible = True
            self._application.showMessageSignal.emit(self)

    ##  Can the message be closed by user?
    def isDismissable(self):
        return self._dismissable

    ##  Set the lifetime timer of the message.
    #   This is used by the QT application once the message is shown.
    #   If the lifetime is set to 0, no timer is added.
    def setTimer(self, timer):
        self._lifetime_timer = timer
        if self._lifetime_timer:
            if self._lifetime:
                self._lifetime_timer.setInterval(self._lifetime * 1000)
                self._lifetime_timer.setSingleShot(True)
                self._lifetime_timer.timeout.connect(self.hide)
                self._lifetime_timer.start()

    ##  Add an action to the message
    #   Actions are useful for making messages that require input from the user.
    #   \param action_id
    #   \param name The displayed name of the action
    #   \param icon Source of the icon to be used
    #   \param description Description of the item (used for mouse over, etc)
    def addAction(self, action_id, name, icon, description):
        self._actions.append({"action_id": action_id, "name": name, "icon": icon, "description": description})

    ##  Get the list of actions to display buttons for on the message.
    #
    #   Each action is a dictionary with the elements provided in ``addAction``.
    #
    #   \return A list of actions.
    def getActions(self):
        return self._actions

    ##  Changes the text on the message.
    #
    #   \param text The new text for the message. Please ensure that this text
    #   is internationalised.
    def setText(self, text: str):
        self._text = text

    ##  Returns the text in the message.
    #
    #   \return The text in the message.
    def getText(self) -> str:
        return self._text

    ##  Sets the maximum numerical value of the progress bar on the message.
    #
    #   If the reported progress hits this number, the bar will appear filled.
    def setMaxProgress(self, max_progress):
        self._max_progress = max_progress

    ##  Gets the maximum value of the progress bar on the message.
    #
    #   Note that this is not the _current_ value of the progress bar!
    #
    #   \return The maximum value of the progress bar on the message.
    #
    #   \see getProgress
    def getMaxProgress(self):
        return self._max_progress

    ##  Changes the state of the progress bar.
    #
    #   \param progress The new progress to display to the user. This should be
    #   between 0 and the value of ``getMaxProgress()``.
    def setProgress(self, progress):
        self._progress = progress
        self.progressChanged.emit(self)

    ##  Signal that gets emitted whenever the state of the progress bar on this
    #   message changes.
    progressChanged = Signal()

    ##  Returns the current progress.
    #
    #   This should be a value between 0 and the value of ``getMaxProgress()``.
    def getProgress(self):
        return self._progress

    ##  Hides this message.
    #
    #   While the message object continues to exist in memory, it appears to the
    #   user that it is gone.
    def hide(self):
        if self._visible:
            self._visible = False
            self._application.hideMessageSignal.emit(self)
