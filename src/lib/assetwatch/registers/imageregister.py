from cloneregister import CloneRegister
from os.path import relpath
import sys

image_extensions = (".png", ".gif", ".jpg")


class ImageRegister(CloneRegister):

    def recognized_extensions(self):
        return image_extensions

    def __init__(self, assets_dir, public_dir, http_path, environment):
        self.assets_dir = assets_dir
        self.public_dir = public_dir
        self.http_path = http_path
        self.environment = environment
        self._files = []
        self._clone_subdirs = {}
    
    def images_dir(self):
        return self.public_dir + "/images"
    
    def clone_path_of(self, file):
        dir = self.images_dir()
        clone_filename = relpath(start=self.assets_dir, path=file).replace("/", "_")
        subdir = self._clone_subdirs.get(file)
        if subdir is None:
            return dir + "/" + clone_filename
        else:
            return dir + "/" + subdir + "/" + clone_filename

    def should_do_clone_of(self, file):
        return file in self._files

    def about_to_add_clone(self, file):
        print >> sys.stderr, '[notice] referenced image ok: %s' % relpath(start=self.assets_dir, path=file)

    def about_to_delete_clone(self, file):
        print >> sys.stderr, '[warn] referenced image was deleted: %s' % relpath(start=self.assets_dir, path=file)

    def about_to_refresh_clone(self, file):
        print >> sys.stderr, '[notice] referenced image was modified: %s' % relpath(start=self.assets_dir, path=file)

    def add_referenced_file(self, file, clone_subdir=None):
        self._files.append(file)
        self._clone_subdirs[file] = clone_subdir
        self.ensure_clone(file)

    def remove_referenced_file(self, file):
        self._files.remove(file)
        self.delete_clone(file)

    def file_not_found(self, file):
        print >> sys.stderr, '[warn] image not found: %s' % relpath(start=self.assets_dir, path=file)
