# Copyright (c) 2026 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

from __future__ import annotations

from concurrent import futures
from queue import Empty, Full, Queue
import threading
from typing import Callable, Optional

import grpc
from UM.Application import Application


class GrpcBackendServer:
    """Runs one gRPC server endpoint and forwards stream messages to Qt's loop."""

    def __init__(self, servicer, add_servicer: Callable, host: str = "127.0.0.1", first_port: int = 49674):
        self._servicer = servicer
        self._add_servicer = add_servicer
        self._host = host
        self._port = first_port
        self._server: Optional[grpc.Server] = None
        self._lock = threading.Lock()
        self._connected = threading.Event()
        self._stopping = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._error: Optional[BaseException] = None
        self._active_context = None
        self._on_stream_ended: Optional[Callable] = None
        self._on_stream_connected: Optional[Callable] = None
        self._outgoing: Queue = Queue(maxsize=128)
        self._application = Application.getInstance()

    @property
    def port(self) -> int:
        return self._port

    @property
    def connected(self) -> bool:
        return self._connected.is_set()

    @property
    def error(self) -> Optional[BaseException]:
        return self._error

    def start(self) -> int:
        with self._lock:
            if self._server is not None:
                return self._port

            while self._port < 65535:
                server = grpc.server(
                    futures.ThreadPoolExecutor(max_workers=4),
                    options=(
                        ("grpc.max_send_message_length", 500 * 1024 * 1024),
                        ("grpc.max_receive_message_length", 500 * 1024 * 1024),
                    ),
                )
                self._add_servicer(self._servicer, server)
                port = server.add_insecure_port(f"{self._host}:{self._port}")
                if port:
                    self._server = server
                    self._server.start()
                    return self._port
                self._port += 1
            raise RuntimeError("Could not bind the Cura Engine gRPC endpoint")

    def wait_for_connection(self, timeout: float = 10.0) -> bool:
        return self._connected.wait(timeout)

    def mark_connected(self) -> None:
        self._connected.set()
        self._error = None
        if self._on_stream_connected:
            self._application.callLater(self._on_stream_connected)

    def run_stream(self, request_iterator, context, on_message: Callable) -> None:
        """Yield response envelopes while reading incoming envelopes concurrently."""
        requests_finished = threading.Event()
        self._active_context = context

        def receive_requests() -> None:
            try:
                for envelope in request_iterator:
                    if self._stopping.is_set() or not context.is_active():
                        break
                    self._application.callLater(on_message, envelope)
            except BaseException as error:
                self._error = error
            finally:
                requests_finished.set()

        self.mark_connected()
        reader = threading.Thread(target=receive_requests, name="CuraEngineGrpcReader", daemon=True)
        reader.start()
        try:
            while context.is_active() and not self._stopping.is_set():
                try:
                    response = self._outgoing.get(timeout=0.1)
                except Empty:
                    if requests_finished.is_set():
                        break
                    continue
                yield response
        finally:
            self._active_context = None
            self._connected.clear()
            while True:
                try:
                    self._outgoing.get_nowait()
                except Empty:
                    break
            if self._on_stream_ended:
                self._application.callLater(self._on_stream_ended, self._error)

    def send_message(self, envelope) -> bool:
        """Queue an envelope for the currently connected engine stream."""
        if self._stopping.is_set() or not self._connected.is_set():
            return False
        try:
            self._outgoing.put_nowait(envelope)
            return True
        except Full:
            return False

    def stop(self, grace: float = 1.0) -> None:
        self._stopping.set()
        self._connected.clear()
        if self._active_context is not None:
            self._active_context.cancel()
        while True:
            try:
                self._outgoing.get_nowait()
            except Empty:
                break
        with self._lock:
            server, self._server = self._server, None
        if server is not None:
            server.stop(grace).wait(timeout=max(grace + 1.0, 2.0))
