from register import Register
import os
import sys
from os.path import dirname, exists, relpath
import shutil


class CloneRegister(Register):

    def recognized_extensions(self):
        return () # to be overriden

    def clone_path_of(self, file):
        return None # to be overriden

    def should_do_clone_of(self, file):
        return True # may be overriden

    def new_file_detected(self, file):
        print >> sys.stderr, '[notice] new file was created: %s' % relpath(start=self.assets_dir, path=file)
        if self.should_do_clone_of(file):
            self.about_to_add_clone(file)
            self.ensure_clone(file)
            self.clone_added(file)

    def file_deleted(self, file):
        print >> sys.stderr, '[notice] file was deleted: %s' % relpath(start=self.assets_dir, path=file)
        if self.should_do_clone_of(file):
            self.about_to_delete_clone(file)
            self.delete_clone(file)
            self.clone_deleted(file)

    def file_modified(self, file):
        print >> sys.stderr, '[notice] file was modified: %s' % relpath(start=self.assets_dir, path=file)
        if self.should_do_clone_of(file):
            self.about_to_refresh_clone(file)
            self.ensure_clone(file)
            self.clone_refreshed(file)

    def about_to_add_clone(self, file):
        pass # may be overriden

    def about_to_delete_clone(self, file):
        pass # may be overriden

    def about_to_refresh_clone(self, file):
        pass # may be overriden

    def clone_added(self, file):
        pass # may be overriden
    
    def clone_refreshed(self, file):
        pass # may be overriden
    
    def clone_deleted(self, file):
        pass # may be overriden
    
    def make_clone(self, file, clone):
        shutil.copy(file, clone) # may be everrided

    #---------------------------------------------------------------------------

    def delete_clone(self, file):
        clone = self.clone_path_of(file)
        if exists(clone): # it may not exist when this function is called from some function in derived class
            os.remove(clone)
            try:
                os.removedirs(dirname(clone))
            except OSError:
                pass # ignore even if leaf directory is not empty

    def ensure_clone(self, file, ensure_make_clone=False):
        if exists(file):
            clone = self.clone_path_of(file)
            if ensure_make_clone or not exists(clone) or os.stat(file).st_mtime > os.stat(clone).st_mtime:
                if not exists(dirname(clone)):
                    os.makedirs(dirname(clone))
                self.make_clone(file, clone)
        else:
            self.file_not_found(file)
            
    def file_not_found(self, file):
        pass # may be overriden
