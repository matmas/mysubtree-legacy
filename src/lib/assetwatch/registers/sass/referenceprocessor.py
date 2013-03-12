from os.path import dirname, exists, isfile

class ReferenceProcessor:
    def __init__(self, assets_dir, public_dir, http_path, environment, imageregister):
        self.assets_dir = assets_dir
        self.public_dir = public_dir
        self.http_path = http_path
        self.environment = environment
        self.imageregister = imageregister
        self.file_references = {}

    def match_to_filename(self, match):
        return match.group(1) # may be overriden
        
    def process(self, filedata, file):
        previous_references = self.file_references.get(file, [])
        
        added_references = []
        def replacement(match):
            filename = self.match_to_filename(match)
            local_dir = dirname(file)
            local_reference = local_dir + "/" + filename
            global_reference = self.assets_dir + "/" + filename
            if exists(global_reference) and not exists(local_reference) and isfile(global_reference):
                reference = global_reference
            else:
                reference = local_reference
            
            if reference not in previous_references:
                self.imageregister.add_referenced_file(reference, self.subdir())
            added_references.append(reference)
            return self.pattern_replacement(reference, match)
            
        filedata = self.pattern().sub(replacement, filedata)
        
        for removed_reference in (reference for reference in previous_references if reference not in added_references):
            self.imageregister.remove_referenced_file(removed_reference)
        self.file_references[file] = added_references
        if added_references: # nonempty
            some_replacements_made = True
        else:
            some_replacements_made = False
        filedata = self.postprocess(filedata, some_replacements_made)
        return filedata
    
    def postprocess(self, filedata, some_replacements_made):
        return filedata 
