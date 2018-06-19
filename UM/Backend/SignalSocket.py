# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import collections
import threading

import Arcus


class CallbackHandlerThread(threading.Thread):

    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()
        self._queue = collections.deque()
        self._done = False
        self._event = threading.Event()

    def put(self, callback):
        with self._lock:
            self._queue.append(callback)
            self._event.set()

    def done(self):
        with self._lock:
            self._done = True
            self._event.set()

    def run(self):
        while True:
            if not self._event.wait(0.01):
                continue

            with self._lock:
                while self._queue:
                    item = self._queue.popleft()
                    item()

                if self._done:
                    return

                self._event.clear()


class SignalSocket(Arcus.Socket):
    def __init__(self, on_state_changed_callback = None, on_message_received_callback = None, on_error_callback = None):
        super().__init__()

        self._on_state_changed_callback = self._onStateChanged
        self._on_message_received_callback = self._onMessageReceived
        self._on_error_callback = self._onError

        if on_state_changed_callback is not None:
            self._on_state_changed_callback = on_state_changed_callback
        if on_message_received_callback is not None:
            self._on_message_received_callback = on_message_received_callback
        if on_error_callback is not None:
            self._on_error_callback = on_error_callback

        self.callback_thread = CallbackHandlerThread()
        self.callback_thread.start()

        self._listener = _SocketListener()
        self._listener.stateChangedCallback = self._on_state_changed_callback
        self._listener.messageReceivedCallback = self._on_message_received_callback
        self._listener.errorCallback = self._on_error_callback
        self.addListener(self._listener)

    def _onStateChanged(self, state):
        self.callback_thread.put(lambda s = state: self._listener.stateChangedCallback(s))

    def _onMessageReceived(self):
        self.callback_thread.put(lambda : self._listener.stateChangedCallback())
        self._listener.messageReceivedCallback()

    def _onError(self, error):
        self.callback_thread.put(lambda e = error: self._listener.errorCallback(e))


class _SocketListener(Arcus.SocketListener):
    def __init__(self):
        super().__init__()

        self.stateChangedCallback = None
        self.messageReceivedCallback = None
        self.errorCallback = None

    def stateChanged(self, state):
        try:
            if self.stateChangedCallback:
                self.stateChangedCallback(state)
        except AttributeError:
            # For some reason, every so often, it seems to feel that the attribute stateChangedCallback doesn't exist.
            # Ignoring this prevents crashes.
            pass

    def messageReceived(self):
        if self.messageReceivedCallback:
            self.messageReceivedCallback()

    def error(self, error):
        if self.errorCallback:
            self.errorCallback(error)
