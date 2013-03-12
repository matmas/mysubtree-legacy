import time
#from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver as Observer # https://github.com/gorakhargosh/watchdog/issues/46
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent, FileMovedEvent
from lib.fileextension import extension
from registers.sassregister import SassRegister
from registers.imageregister import ImageRegister
from registers.scriptregister import ScriptRegister

class EventHandler(FileSystemEventHandler):
    def __init__(self, register):
        FileSystemEventHandler.__init__(self)
        self.register = register

    def on_any_event(self, event):
        file = event.src_path
        if extension(file) in self.register.recognized_extensions():
            if type(event) == FileCreatedEvent:
                self.register.new_file_detected(file)
            elif type(event) == FileDeletedEvent:
                self.register.file_deleted(file)
            elif type(event) == FileModifiedEvent:
                self.register.file_modified(file)
        if type(event) == FileMovedEvent:
            if extension(event.src_path) in self.register.recognized_extensions():
                self.register.file_deleted(event.src_path)
            if extension(event.dest_path) in self.register.recognized_extensions():
                self.register.new_file_detected(event.dest_path)

def assetobserver(assets_dir, public_dir, http_path, environment):
    observer = Observer()
    
    imageregister = ImageRegister(assets_dir, public_dir, http_path, environment)
    observer.schedule(EventHandler(imageregister), path=assets_dir, recursive=True)
    
    sassregister = SassRegister(assets_dir, public_dir, http_path, environment, imageregister)
    observer.schedule(EventHandler(sassregister), path=assets_dir, recursive=True)
    
    scriptregister = ScriptRegister(assets_dir, public_dir, http_path, environment)
    observer.schedule(EventHandler(scriptregister), path=assets_dir, recursive=True)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
