import re
from os.path import basename, splitext
from referenceprocessor import ReferenceProcessor

class SpriteReferenceProcessor(ReferenceProcessor):
    """
    @import "sprites/*.png";
    sprite(relative/path/image.png); -> @include sprites-sprite(image);
    """

    def subdir(self):
        return "sprites"
    
    def match_to_filename(self, match):
        return match.group(2)
    
    def pattern(self):
        return re.compile(r"""
            ^
            (?!//)
            (.*?)
            sprite\(
            \s*
            ["']?
            (
            [^"'\)]+
            \.%(image_extension)s
            )
            ["']?
            \s*
            \)
            """ % {"image_extension": "png"}, re.VERBOSE | re.MULTILINE)
    
    def pattern_replacement(self, reference, match):
        return match.group(1) + r"@include sprites-sprite(%s)" % basename(splitext(self.imageregister.clone_path_of(reference))[0])
    
    def postprocess(self, filedata, some_replacements_made):
        if some_replacements_made:
            return '@import "sprites";\n' + filedata
        else:
            return filedata 
