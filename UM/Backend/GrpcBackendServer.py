# Copyright (c) 2026 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

from __future__ import annotations

from concurrent import futures
from queue import Empty, Full, Queue
import threading
from typing import Callable, Iterator, Optional, TYPE_CHECKING

import grpc

from UM.Signal import Signal
from UM.Logger import Logger

if TYPE_CHECKING:
    from google.protobuf.message import Message as ProtoMessage
    from grpc.framework.interfaces.base.base import Servicer as GrpcServicer


class GrpcBackendServer:
    """Runs one gRPC server endpoint and forwards stream messages to Qt's loop."""

    def __init__(self) -> None:
        self._port: int = 0
        self._server: Optional[grpc.Server] = None
        self._connected: threading.Event = threading.Event()
        self._server_stopping: threading.Event = threading.Event()
        self._error: Optional[BaseException] = None
        self._active_client_context: Optional[grpc.ServicerContext] = None
        self._active_client_context_lock = threading.Lock()
        self._outgoing: Queue[Optional["ProtoMessage"]] = Queue(maxsize=128)

        self.streamConnected = Signal()
        self.streamEnded = Signal()
        self.messageReceived = Signal()

    @property
    def connected(self) -> bool:
        return self._connected.is_set()

    def start(
        self,
        host: str,
        first_port: int,
        servicer: "GrpcServicer",
        add_servicer: Callable[["GrpcServicer", grpc.Server], None],
    ) -> int:
        if self._server is not None:
            return self._port

        self._port = first_port
        while self._port < 65535:
            server = grpc.server(
                futures.ThreadPoolExecutor(max_workers=4),
                options=(
                    ("grpc.max_send_message_length", 500 * 1024 * 1024),
                    ("grpc.max_receive_message_length", 500 * 1024 * 1024),
                ),
            )

            add_servicer(servicer, server)
            port = server.add_insecure_port(f"{host}:{self._port}")

            if port:
                self._server = server
                self._server.start()
                return self._port

            self._port += 1

        raise RuntimeError("Could not bind the Cura Engine gRPC endpoint")

    def run_stream(
        self,
        request_iterator: Iterator["ProtoMessage"],
        context: grpc.ServicerContext,
    ) -> Iterator["ProtoMessage"]:
        """Yield response envelopes while reading incoming envelopes concurrently."""
        with self._active_client_context_lock:
            self._active_client_context = context

        client_stopping = threading.Event()

        # Clear the outgoing messages queue
        while True:
            try:
                self._outgoing.get_nowait()
            except Empty:
                break

        def receive_requests() -> None:
            try:
                for envelope in request_iterator:
                    if self._server_stopping.is_set() or client_stopping.is_set() or not context.is_active():
                        break
                    Logger.debug(f"<<<<<<<<<<<<< Received message {envelope.WhichOneof("message")}")
                    self.messageReceived.emit(envelope)
            except BaseException as error:
                self._error = error
            finally:
                client_stopping.set()

        self._connected.set()
        self._error = None

        self.streamConnected.emit()

        # Secondary co-routine path, spawned in a separate thread, handles the received of messages
        reader = threading.Thread(target=receive_requests, name="CuraEngineGrpcReader", daemon=True)
        reader.start()

        try:
            # Primary co-routine path handles the writing of messages
            while context.is_active() and not self._server_stopping.is_set() and not client_stopping.is_set():
                try:
                    response = self._outgoing.get(timeout=0.1)
                except Empty:
                    continue

                if response is None:
                    continue

                Logger.debug(f">>>>>>>>>>>>> Sending message {response.WhichOneof("message")}")
                yield response
        finally:
            client_stopping.set()

            with self._active_client_context_lock:
                self._active_client_context.cancel()
                self._active_client_context = None

            self._connected.clear()

            self.streamEnded.emit(self._error)

    def send_message(self, envelope: "ProtoMessage") -> bool:
        """Queue an envelope for the current or next engine stream."""
        try:
            self._outgoing.put_nowait(envelope)
            return True
        except Full:
            return False

    def stop(self) -> None:
        self._connected.clear()

        # Notify the read loop to gently stop by setting stopping to true and cancelling the client context
        self._server_stopping.set()
        with self._active_client_context_lock:
            if self._active_client_context is not None:
                self._active_client_context.cancel()
                self._active_client_context = None

        try:
            # Notify the send loop to gently stop by adding an empty message
            self._outgoing.put_nowait(None)
        except Full:
            pass

        self._server.stop(1.0).wait(timeout=2.0)
        self._server = None
