# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Optional, Union, Dict, List

from UM.Signal import Signal, signalemitter
from UM.Logger import Logger
from PyQt5.QtCore import QTimer, pyqtSignal, QObject


## Class for displaying messages to the user.
@signalemitter
class Message(QObject):

    class ActionButtonStyle:
        DEFAULT = 0
        LINK = 1
        SECONDARY = 2


    class ActionButtonAlignment:
        ALIGN_LEFT = 2
        ALIGN_RIGHT = 3


    ##  Class for displaying messages to the user.
    #   Even though the lifetime can be set, in certain cases it can still have a lifetime if nothing happens with the
    #   the message.
    #   We define the following cases;
    #   - A message is dismissible; No timeout (set by lifetime or inactivity)
    #   - A message is set to not dismissible, without progress; We force the dismissible property to be true
    #   - A message is set to not dismissible, with progress; After 30 seconds of no progress updates we hide the message.
    #   \param text Text that needs to be displayed in the message
    #   \param lifetime How long should the message be displayed (in seconds).
    #                   if lifetime is 0, it will never automatically be destroyed.
    #   \param dismissible Can the user dismiss the message?
    #   \param title Phrase that will be shown above the message
    #   \progress Is there nay progress to be displayed? if -1, it's seen as indeterminate
    def __init__(self, text: str = "", lifetime: int = 30, dismissable: bool = True, progress: float = None,
                 title: Optional[str] = None, parent = None, use_inactivity_timer: bool = True, image_source: str = "", image_caption: str = "") -> None:
        super().__init__(parent)
        from UM.Application import Application
        self._application = Application.getInstance()
        self._visible = False
        self._text = text
        self._progress = progress  # If progress is set to -1, the progress is seen as indeterminate
        self._max_progress = 100  # type: float
        self._lifetime = lifetime
        self._lifetime_timer = None  # type: Optional[QTimer]

        self._image_source = image_source
        self._image_caption = image_caption

        self._use_inactivity_timer = use_inactivity_timer
        self._inactivity_timer = None  # type: Optional[QTimer]

        self._dismissable = dismissable  # Can the message be closed by user?
        if not self._dismissable:
            # If the message has no lifetime and no progress, it should be dismissible.
            # this is to prevent messages being permanently visible.
            if self._lifetime == 0 and self._progress is None:
                self._dismissable = True

        self._actions = []  # type: List[Dict[str, Union[str, int]]]
        self._title = title

    # We use these signals as QTimers need to be triggered from a qThread. By using signals to pass it,
    # the events are forced to be on the event loop (which is a qThread)
    inactivityTimerStop = pyqtSignal()
    inactivityTimerStart = pyqtSignal()
    actionTriggered = Signal()

    def _stopInactivityTimer(self) -> None:
        if self._inactivity_timer:
            self._inactivity_timer.stop()

    def _startInactivityTimer(self) -> None:
        if self._inactivity_timer:
            # There is some progress indication, but no lifetime, so the inactivity timer needs to run.
            if self._progress is not None and self._lifetime == 0:
                self._inactivity_timer.start()

    def _onInactivityTriggered(self) -> None:
        Logger.log("d", "Hiding message because of inactivity")
        self.hide()

    ##  Show the message (if not already visible)
    def show(self) -> None:
        if not self._visible:
            self._visible = True
            self._application.showMessageSignal.emit(self)
            self.inactivityTimerStart.emit()

    ## Returns a boolean indicating whether the message is currently visible.
    @property
    def visible(self) -> bool:
        return self._visible

    ##  Can the message be closed by user?
    def isDismissable(self) -> bool:
        return self._dismissable

    ##  Set the lifetime timer of the message.
    #   This is used by the QT application once the message is shown.
    #   If the lifetime is set to 0, no timer is added.
    #   This function is required as the QTimer needs to be created on a QThread.
    def setLifetimeTimer(self, timer: QTimer) -> None:
        self._lifetime_timer = timer
        if self._lifetime_timer:
            if self._lifetime:
                self._lifetime_timer.setInterval(self._lifetime * 1000)
                self._lifetime_timer.setSingleShot(True)
                self._lifetime_timer.timeout.connect(self.hide)
                self._lifetime_timer.start()
            self._startInactivityTimer()

    ##  Set the inactivity timer of the message.
    #   This function is required as the QTimer needs to be created on a QThread.
    def setInactivityTimer(self, inactivity_timer: QTimer) -> None:
        if not self._use_inactivity_timer:
            return
        self._inactivity_timer = inactivity_timer
        self._inactivity_timer.setInterval(30 * 1000)
        self._inactivity_timer.setSingleShot(True)
        self._inactivity_timer.timeout.connect(self._onInactivityTriggered)
        self.inactivityTimerStart.connect(self._startInactivityTimer)
        self.inactivityTimerStop.connect(self._stopInactivityTimer)

    ##  Add an action to the message
    #   Actions are useful for making messages that require input from the user.
    #   \param action_id
    #   \param name The displayed name of the action
    #   \param icon Source of the icon to be used
    #   \param button_style Description the button style (used for Button and Link)
    #   \param button_align Define horizontal position of the action item
    def addAction(self, action_id: str, name: str, icon: str, description: str, button_style: int = ActionButtonStyle.DEFAULT, button_align: int = ActionButtonAlignment.ALIGN_RIGHT):
        self._actions.append({"action_id": action_id, "name": name, "icon": icon, "description": description, "button_style": button_style, "button_align": button_align})

    ##  Get the list of actions to display buttons for on the message.
    #
    #   Each action is a dictionary with the elements provided in ``addAction``.
    #
    #   \return A list of actions.
    def getActions(self) -> List[Dict[str, Union[str, int]]]:
        return self._actions

    def getImageSource(self) -> str:
        return self._image_source

    def getImageCaption(self) -> str:
        return self._image_caption

    ##  Changes the text on the message.
    #
    #   \param text The new text for the message. Please ensure that this text
    #   is internationalised.
    def setText(self, text: str) -> None:
        self._text = text

    ##  Returns the text in the message.
    #
    #   \return The text in the message.
    def getText(self) -> str:
        return self._text

    ##  Sets the maximum numerical value of the progress bar on the message.
    #
    #   If the reported progress hits this number, the bar will appear filled.
    def setMaxProgress(self, max_progress: float) -> None:
        self._max_progress = max_progress

    ##  Gets the maximum value of the progress bar on the message.
    #
    #   Note that this is not the _current_ value of the progress bar!
    #
    #   \return The maximum value of the progress bar on the message.
    #
    #   \see getProgress
    def getMaxProgress(self) -> float:
        return self._max_progress

    ##  Changes the state of the progress bar.
    #
    #   \param progress The new progress to display to the user. This should be
    #   between 0 and the value of ``getMaxProgress()``.
    def setProgress(self, progress: float) -> None:
        if self._progress != progress:
            self._progress = progress
            self.progressChanged.emit(self)
        self.inactivityTimerStart.emit()

    ##  Signal that gets emitted whenever the state of the progress bar on this
    #   message changes.
    progressChanged = Signal()

    ##  Returns the current progress.
    #
    #   This should be a value between 0 and the value of ``getMaxProgress()``.
    #   If no progress is set (because the message doesn't have it) None is returned
    def getProgress(self) -> Optional[float]:
        return self._progress

    ##  Changes the message title.
    #
    #   \param text The new title for the message. Please ensure that this text
    #   is internationalised.
    def setTitle(self, title: str) -> None:
        self._title = title

    ##  Returns the message title.
    #
    #   \return The message title.
    def getTitle(self) -> Optional[str]:
        return self._title

    ##  Hides this message.
    #
    #   While the message object continues to exist in memory, it appears to the
    #   user that it is gone.
    def hide(self, send_signal = True) -> None:
        if self._visible:
            self._visible = False
            self.inactivityTimerStop.emit()
            if send_signal:
                self._application.hideMessageSignal.emit(self)
