import os


def get_files_recursively(directory=".", suffix=""):
    all_files = []
    for dirname, dirs, files in os.walk(directory):
        for filename in files:
            file = os.path.join(dirname, filename)
            if os.path.isfile(file) and file.endswith(suffix):
                all_files.append(file)
    return all_files
