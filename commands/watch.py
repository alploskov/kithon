import time
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    is_watch_install = True
except ImportError:
    is_watch_install = False

def watch(action, path):
    if not is_watch_install:
        raise Exception(
            "requires watchdog library\n"
            "\trun 'python -m pip install kithon[watch]' to fix"
        )
    class handl(FileSystemEventHandler):
        def on_modified(self, event):
            if event.is_directory:
                return
            if event.src_path.split('.')[-1] not in ['py', 'coco', 'hy', 'pyx', 'cocox']:
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
