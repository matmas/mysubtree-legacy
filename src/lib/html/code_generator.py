from os.path import dirname  

from . import get_output_path

code_set = []

def generate_code(root_componentnode):
    for componentnode in root_componentnode.children:
        _register_code(componentnode.dump_tree())
        _generate_code_recursively(componentnode)

def _generate_code_recursively(componentnode):
    for child in componentnode.children:
        _generate_code_recursively(child)
    for code in componentnode.get_generated_codes():
        _register_code(code)

def _register_code(code):
    if code not in code_set:
        code_set.append(code)
        _write_to_file(code_set)

def _write_to_file(code_set):
    with open(get_output_path(), "w") as file:
        separator = "// -----------------------------------------------------------\n"
        file.write(separator.join(code_set))
