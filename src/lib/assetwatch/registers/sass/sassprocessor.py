from imagereferenceprocessor import ImageReferenceProcessor
from spritereferenceprocessor import SpriteReferenceProcessor


class SassProcessor:

    def __init__(self, assets_dir, public_dir, http_path, environment, imageregister):
        self.assets_dir = assets_dir
        self.public_dir = public_dir
        self.http_path = http_path
        self.environment = environment
        self.imageregister = imageregister
        self.imagereferenceprocessor = ImageReferenceProcessor(assets_dir, public_dir, http_path, environment, imageregister)
        self.spritereferenceprocessor = SpriteReferenceProcessor(assets_dir, public_dir, http_path, environment, imageregister)
    
    def process(self, filedata, file):
        filedata = self.imagereferenceprocessor.process(filedata, file)
        filedata = self.spritereferenceprocessor.process(filedata, file)
        return filedata
    

#assert relative_image_pattern.sub(r"url(some_prefix/\1)", "url('test.png')")   == "url(some_prefix/test.png)"
#assert relative_image_pattern.sub(r"url(some_prefix/\1)", "url(\"test.png\")") == "url(some_prefix/test.png)"
#assert relative_image_pattern.sub(r"url(some_prefix/\1)", "url(test.png)")     == "url(some_prefix/test.png)"
#assert relative_image_pattern.sub(r"url(some_prefix/\1)", "url(test.htc)")     == "url(test.htc)"
