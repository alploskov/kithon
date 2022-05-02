import time
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    raise Exception(
        "requires watchdog library\n"
        "\trun 'python -m pip install kithon[watch]' to fix"
    )


def watch(action, path):
    class handl(FileSystemEventHandler):
        def on_modified(self, event):
            if event.is_directory:
                return
            action()
    obs = Observer()
    obs.schedule(handl(), path=path)
    obs.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()
