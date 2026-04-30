"""Background workers (scanning, lyrics) running on a Qt thread pool."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class _WorkerSignals(QObject):
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(object)


class Worker(QRunnable):
    """Run a callable in the global ``QThreadPool`` and emit Qt signals.

    The callable receives an ``on_progress`` keyword if accepted, so a
    long-running job can stream updates back to the UI thread.
    """

    def __init__(self, fn: Callable, *args, **kwargs) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = _WorkerSignals()

    def run(self) -> None:  # noqa: D401 - QRunnable hook
        try:
            kwargs = dict(self.kwargs)
            if "on_progress" in self.fn.__code__.co_varnames:
                kwargs.setdefault("on_progress", self.signals.progress.emit)
            result = self.fn(*self.args, **kwargs)
            self.signals.finished.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.signals.error.emit(f"{type(exc).__name__}: {exc}")


def submit(fn: Callable, *args,
           on_finished: Optional[Callable] = None,
           on_error: Optional[Callable[[str], None]] = None,
           on_progress: Optional[Callable] = None,
           **kwargs) -> Worker:
    worker = Worker(fn, *args, **kwargs)
    if on_finished is not None:
        worker.signals.finished.connect(on_finished)
    if on_error is not None:
        worker.signals.error.connect(on_error)
    if on_progress is not None:
        worker.signals.progress.connect(on_progress)
    QThreadPool.globalInstance().start(worker)
    return worker
