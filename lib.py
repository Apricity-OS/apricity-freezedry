import os


def any_in(list_a, list_b):
    any_a_in_b = False
    for val in list_a:
        if val in list_b:
            any_a_in_b = True
    return any_a_in_b


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
