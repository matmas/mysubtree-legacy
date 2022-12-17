import re
import sys
from os.path import exists, dirname, relpath, isfile, basename


class DependencyResolver:
    
    def __init__(self, assets_dir, public_dir, environment, possible_extensions):
        self.assets_dir = assets_dir
        self.public_dir = public_dir
        self.environment = environment
        self.possible_extensions = possible_extensions
    
    def get_ordered_files(self, unordered_files):
        remaining_files = list(unordered_files)
        ordered_files = []
        while remaining_files:
            self._add_file_ordered(remaining_files[0], remaining_files, ordered_files)
        assert len(unordered_files) == len(ordered_files)
        return ordered_files
    
    def _add_file_ordered(self, file, remaining_files, ordered_files):
        if file in remaining_files:
            dependencies = self.dependencies_of(file)
            if dependencies:
                for dependency in dependencies:
                    #print '"%s" depends on "%s"' % (basename(file), basename(dependency))
                    self._add_file_ordered(dependency, remaining_files, ordered_files)
            ordered_files.append(file)
            remaining_files.remove(file)
        
    def dependencies_of(self, file):
        require_pattern = re.compile(r"""
            ^
            (\#|//)
            =
            \s*
            require
            \s*
            \(?
            \s*
            ["']?
            (
            [^"'\);\n]+
            )
            ["']?
            \s*
            \)?
            \s*
            ;?
            $
            """, re.VERBOSE | re.MULTILINE)
        dependencies = []
        for match in require_pattern.finditer(open(file).read()):
            reference = match.group(2)
            local_dir = dirname(file)
            dependency = self._require_reference_to_file(reference, src_file=file, search_paths=(self.assets_dir, local_dir), possible_extensions=self.possible_extensions)
            if dependency is not None:
                dependencies.append(dependency)
        return dependencies
    
    def _require_reference_to_file(self, reference, src_file, search_paths, possible_extensions):
        for directory in search_paths:
            for possible_extension in possible_extensions:
                file = directory + "/" + reference + possible_extension
                if exists(file) and isfile(file):
                    return file
        print >> sys.stderr, '[warn] Dependency "%s" not found (required in "%s")' % (reference, relpath(start=self.assets_dir, path=src_file))
        return None 
