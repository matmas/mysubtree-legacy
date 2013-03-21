import os
import urllib2
import shutil
import sys
from operator import itemgetter
from os.path import basename, getsize, relpath
from lib.fileextension import extension
from register import Register
from dependencies.dependencies import DependencyResolver
from script import coffeescript
from script.uglifyjs import uglifyjs

def sizeof_fmt(num):
    #http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


class ScriptRegister(Register):

    def __init__(self, assets_dir, public_dir, http_path, environment):
        self.assets_dir = assets_dir
        self.public_dir = public_dir
        self.http_path = http_path
        self.environment = environment
        self._files = []
        self._compiled_files = {}
        self.dependencyresolver = DependencyResolver(assets_dir, public_dir, environment, possible_extensions=self.recognized_extensions())
        
        self.add_files_recursively(self.assets_dir)
        self.reassemble_all()
        
    def add_files_recursively(self, directory):
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if extension(filename) in self.recognized_extensions():
                    file = os.path.join(root, filename)
                    self._files.append(file)
    
    def recognized_extensions(self):
        return (".js", ".coffee") #, ".jsurl")
        
    def new_file_detected(self, file):
        print >> sys.stderr, '[notice] new script was created: %s' % relpath(start=self.assets_dir, path=file)
        self._files.append(file)
        self.get_compiled(file, recompile=True)
        self.reassemble_all()
    
    def file_deleted(self, file):
        print >> sys.stderr, '[notice] script was deleted: %s' % relpath(start=self.assets_dir, path=file)
        self._files.remove(file)
        self.reassemble_all()
    
    def file_modified(self, file):
        print >> sys.stderr, '[notice] script was modified: %s' % relpath(start=self.assets_dir, path=file)
        self.get_compiled(file, recompile=True)
        self.reassemble_all()
    
    def get_compiled(self, file, recompile=False):
        compiled = self._compiled_files.get(file)
        if not compiled or recompile:
            if extension(file) == ".js":
                compiled = open(file).read()
            elif extension(file) == ".coffee":
                compiled = coffeescript.convert_to_javascript(file)
            #elif extension(file) == ".jsurl":
                #url = open(file).read()
                #resource = urllib2.urlopen(url)
                #compiled = resource.read()
                #resource.close()
            else:
                raise Exception("Unsupported script extension.")
            self._compiled_files[file] = compiled
        return compiled
    
    def reassemble_all(self):
        ordered_files = self.dependencyresolver.get_ordered_files(self._files)
        
        if self.environment == "production":
            output_file = self.public_dir + "/combined.js"
            
            header = "" # "(function () {"
            footer = "" # "})();"
            
            output = []
            output.append("// Included files:")
        
            for file, size in sorted([(file, getsize(file)) for file in ordered_files], key=itemgetter(1), reverse=True):
                output.append('//  - %s (%s)' % (basename(file), sizeof_fmt(size)))
            output.append("")
            output.append("// Dependencies:")
            for file in ordered_files:
                output.append('//  - %s' % (basename(file)))
                for dependency in self.dependencyresolver.dependencies_of(file):
                    output.append('//      - depends on %s' % basename(dependency))
            output.append("")
            output.append(header)
            for file in ordered_files:
                output.append("")
                output.append("//=======================================================")
                output.append('// %s:' % basename(file))
                output.append("//=======================================================")
                output.append("")
                output.append(self.get_compiled(file))
                
            output.append(footer)
            output = "\n".join(output)
            
            output = uglifyjs(output)
            
            with open(output_file, "w") as f:
                f.write(output)
        else:
            dirname = self.public_dir + "/input_js"
            try:
                shutil.rmtree(dirname)
            except OSError:
                pass # it is OK if it does not exists
            os.makedirs(dirname)
            
            for index, file in enumerate(ordered_files):
                out_filename = dirname + "/%03d-%s" % (index, basename(file))
                with open(out_filename, "w") as f:
                    f.write(self.get_compiled(file))
