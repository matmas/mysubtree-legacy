import re
from os.path import relpath
from referenceprocessor import ReferenceProcessor
from ..imageregister import image_extensions


class ImageReferenceProcessor(ReferenceProcessor):
    """
    url(relative/path/image.png); -> url(/public/path/image.png);
    """

    def subdir(self):
        return "singles"
    
    def pattern(self):
        return re.compile(r"""
            url\(
            \s*
            ["']?
            (
            [^"'\)]+
            \.(%(image_extension)s)
            )
            ["']?
            \s*
            \)
            """ % {"image_extension": "|".join(exension.strip(".") for exension in image_extensions)}, re.VERBOSE)
    
    def pattern_replacement(self, reference, match):
        return r"url('%s/%s')" % (self.http_path, relpath(start=self.public_dir, path=self.imageregister.clone_path_of(reference))) 
