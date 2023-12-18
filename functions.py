import os

def is_file_in_directory(directory, filename):
    filepath = os.path.join(directory, filename)
    return os.path.isfile(filepath)