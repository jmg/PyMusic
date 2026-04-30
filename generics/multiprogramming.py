import threading


def threaded(f):
    """A decorator that runs the wrapped function in a new daemon thread."""
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=f, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return wrapper
