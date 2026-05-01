"""@threaded decorator tests."""

import threading
import time

from generics.multiprogramming import threaded


def test_threaded_runs_in_a_separate_daemon_thread():
    seen = {}
    done = threading.Event()

    @threaded
    def work():
        seen['thread'] = threading.current_thread()
        seen['daemon'] = threading.current_thread().daemon
        done.set()

    work()
    assert done.wait(timeout=2.0), "threaded function never ran"

    assert seen['thread'] is not threading.main_thread()
    assert seen['daemon'] is True


def test_threaded_passes_args_and_kwargs():
    seen = {}
    done = threading.Event()

    @threaded
    def work(a, b, *, c):
        seen['call'] = (a, b, c)
        done.set()

    work(1, 2, c=3)
    assert done.wait(timeout=2.0)
    assert seen['call'] == (1, 2, 3)


def test_threaded_returns_none_immediately():
    """@threaded fires-and-forgets: it must not block the caller."""
    started = threading.Event()
    release = threading.Event()
    finished = threading.Event()

    @threaded
    def slow():
        started.set()
        release.wait(timeout=2.0)
        finished.set()

    t0 = time.monotonic()
    result = slow()
    elapsed = time.monotonic() - t0

    assert result is None
    assert elapsed < 0.5, "threaded() should not block the caller"
    assert started.wait(timeout=1.0)
    release.set()
    assert finished.wait(timeout=2.0)
