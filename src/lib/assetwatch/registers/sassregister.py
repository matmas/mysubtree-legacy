from os.path import dirname, relpath, splitext, exists
import os
import re
from lib.fileextension import extension
from lib.check_output import check_output
from ext.commonprefix import commonprefix as common_parent
from cloneregister import CloneRegister
from dependencies.dependencies import DependencyResolver
import subprocess
from sass.sassprocessor import SassProcessor

class SassRegister(CloneRegister):

    def recognized_extensions(self):
        return (".scss", ".sass")

    def project_dir(self):
        #return common_parent(self.assets_dir, self.public_dir)
        return self.public_dir
    
    def clone_dir(self):
        return self.public_dir + "/_input_sass"
    
    def clone_path_of(self, file):
        return self.clone_dir() + "/" + relpath(start=self.assets_dir, path=file)
    
    def compass_config(self):
        return self.public_dir + "/config.rb"
    
    def __init__(self, assets_dir, public_dir, http_path, environment, imageregister):
        self.assets_dir = assets_dir
        self.public_dir = public_dir
        self.http_path = http_path
        self.environment = environment
        self.imageregister = imageregister
        self.sassprocessor = SassProcessor(assets_dir, public_dir, http_path, environment, imageregister)
        self.dependencyresolver = DependencyResolver(assets_dir, public_dir, environment, possible_extensions=self.recognized_extensions())
        self._sass_files = []
        self.add_files_recursively(assets_dir)
        
        # Configure compass:
        with open(self.compass_config(), "w") as file:
            file.write("""
                http_path = "/"
                additional_import_paths = ["%(additional_import_path)s"]
                sass_dir = "%(sass_dir)s"
                css_dir = "%(css_dir)s"
                images_dir = "%(images_dir)s"
                javascripts_dir = "%(javascripts_dir)s"
                relative_assets = true
                
                # You can select your preferred output style here (can be overridden via the command line):
                #output_style = :expanded or :nested or :compact or :compressed
                
                # To disable debugging comments that display the original location of your selectors. Uncomment:
                #line_comments = false
                
                #require 'compass-rmagick-engine'
                #sprite_engine = :rmagick
            """ % {
                "additional_import_path": self.assets_dir,
                       "sass_dir": relpath(start=self.project_dir(), path=self.clone_dir()),
                        "css_dir": relpath(start=self.project_dir(), path=self.public_dir) + "/output_css",
                     "images_dir": relpath(start=self.project_dir(), path=self.imageregister.images_dir()),
                "javascripts_dir": relpath(start=self.project_dir(), path=self.public_dir) + "/output_javascripts", # probabaly unused
            })
        self.recompile_all()
    
    def add_files_recursively(self, directory):
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if extension(filename) in self.recognized_extensions():
                    file = os.path.join(root, filename)
                    self._sass_files.append(file)
                    self.ensure_clone(file, ensure_make_clone=True)

    def clone_added(self, file):
        self._sass_files.append(file)
        self.recompile_all()

    def clone_deleted(self, file):
        self._sass_files.remove(file)
        self.recompile_all()

    def clone_refreshed(self, file):
        self.recompile_all()

    def make_clone(self, file, clone):
        filedata = open(file).read()
        filedata = self.sassprocessor.process(filedata, file)
        with open(clone, "w") as f:
            f.write(filedata)

    def ensure_sprites(self):
        with open(self.clone_dir() + "/_sprites.scss", "w") as f:
            f.write("""@import "compass/utilities/sprites/base";

// General Sprite Defaults
// You can override them before you import this file.
$sprites-sprite-base-class: ".sprites-sprite" !default;
$sprites-sprite-dimensions: false !default;
$sprites-position: 0% !default;
$sprites-spacing: 0 !default;
$sprites-repeat: no-repeat !default;
$sprites-prefix: '' !default;
$sprites-clean-up: true !default;

$sprites-sprites: sprite-map("sprites/*.png", $cleanup: $sprites-clean-up);

// All sprites should extend this class
// The sprites-sprite mixin will do so for you.


// Use this to set the dimensions of an element
// based on the size of the original image.
@mixin sprites-sprite-dimensions($name) {
  @include sprite-dimensions($sprites-sprites, $name)
}

// Move the background position to display the sprite.
@mixin sprites-sprite-position($name, $offset-x: 0, $offset-y: 0) {
  @include sprite-background-position($sprites-sprites, $name, $offset-x, $offset-y)
}

// Extends the sprite base class and set the background position for the desired sprite.
// It will also apply the image dimensions if $dimensions is true.
@mixin sprites-sprite($name, $dimensions: $sprites-sprite-dimensions, $offset-x: 0, $offset-y: 0) {
  @extend #{$sprites-sprite-base-class} !optional; // NOT SURE ABOUT !optional
  @include sprite($sprites-sprites, $name, $dimensions, $offset-x, $offset-y)
}

@mixin sprites-sprites($sprite-names, $dimensions: $sprites-sprite-dimensions, $prefix: sprite-map-name($sprites-sprites)) {
  @include sprites($sprites-sprites, $sprite-names, $sprites-sprite-base-class, $dimensions, $prefix)
}

            """)
            
    def ensure_combined_sass(self):
        combined_sass_file = self.clone_dir() + "/combined_screen.scss"
        combined_sass = []
        if len(os.listdir("%s/sprites/" % self.imageregister.images_dir())) > 0:
            combined_sass.append('@import "sprites";\n')
            combined_sass.append('#{$sprites-sprite-base-class} {\n background: $sprites-sprites no-repeat;\n}\n')
        for file in self.dependencyresolver.get_ordered_files(self._sass_files):
            combined_sass.append('@import "%s";\n' % splitext(relpath(start=self.assets_dir, path=file))[0]) # without file extension
        combined_sass = "".join(combined_sass)

        if not exists(combined_sass_file) or open(combined_sass_file).read() != combined_sass:
            with open(combined_sass_file, "w") as f:
                f.write(combined_sass)
    
    def recompile_all(self):
        self.ensure_sprites()
        self.ensure_combined_sass()
        output = check_output("compass compile --boring --quiet; exit 0", shell=True, cwd=self.project_dir())
        create = re.compile(r"^   create .+$\n", flags=re.MULTILINE)
        remove = re.compile(r"^   remove .+$\n", flags=re.MULTILINE)
        output = create.sub("", output)
        output = remove.sub("", output)
        if len(output) > 0:
            print output
        