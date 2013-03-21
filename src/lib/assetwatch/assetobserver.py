import time
from watchdog.observers import Observer
#from watchdog.observers.polling import PollingObserver as Observer # https://github.com/gorakhargosh/watchdog/issues/46
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent, FileMovedEvent
from lib.fileextension import extension
from registers.sassregister import SassRegister
from registers.imageregister import ImageRegister
from registers.scriptregister import ScriptRegister

class EventHandler(FileSystemEventHandler):
    def __init__(self, registers):
        FileSystemEventHandler.__init__(self)
        self.registers = registers

    def on_any_event(self, event):
        file = event.src_path
        if hasattr(event, "dest_path"):
            print "[debug] watchdog %s: %s -> %s" % (type(event).__name__, event.src_path, event.dest_path)
        else:
            print "[debug] watchdog %s: %s" % (type(event).__name__, event.src_path)
            
        for register in self.registers:
            if extension(file) in register.recognized_extensions():
                if type(event) == FileCreatedEvent:
                    register.new_file_detected(file)
                elif type(event) == FileDeletedEvent:
                    register.file_deleted(file)
                elif type(event) == FileModifiedEvent:
                    register.file_modified(file)
            if type(event) == FileMovedEvent:
                if extension(event.src_path) in register.recognized_extensions():
                    register.file_deleted(event.src_path)
                if extension(event.dest_path) in register.recognized_extensions():
                    register.new_file_detected(event.dest_path)

def assetobserver(assets_dir, public_dir, http_path, environment):
    observer = Observer()
    imageregister = ImageRegister(assets_dir, public_dir, http_path, environment)
    sassregister = SassRegister(assets_dir, public_dir, http_path, environment, imageregister)
    scriptregister = ScriptRegister(assets_dir, public_dir, http_path, environment)
    observer.schedule(EventHandler([
        imageregister,
        sassregister,
        scriptregister,
    ]), path=assets_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
