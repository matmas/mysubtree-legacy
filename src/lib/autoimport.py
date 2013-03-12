import os

def autoimport_modules(current_file, current_package, first_line_trigger="#autoimport"):
    """
    Example:
    for module in autoimport_modules(__file__, __package__):
        __import__(module)
    """
    modules = []
    for dir, dirs, files in os.walk(os.path.dirname(os.path.abspath(current_file)) + "/"):
        for filename in files:
            if filename.endswith(".py"):
                file = os.path.join(dir, filename)
                with open(file) as f:
                    first_line = f.readline()
                    if first_line == first_line_trigger + "\n":
                        relative_file = file[len(os.path.dirname(os.path.abspath(current_file))) + 1:] # make relative path to current_file
                        parts = relative_file[:-len(".py")].split('/')
                        module = ".".join(parts)
                        if current_package:
                            module = current_package + "." + module
                        modules.append(module)
    return modules