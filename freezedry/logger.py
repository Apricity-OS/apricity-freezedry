class Logger(object):
    def __init__(self):
        self.errors = []

    def log_error(self, error):
        print(error)
        self.errors.append(error)

    def display_errors(self):
        def key(error):
            return error.level

        errors = sorted(self.errors, key=key)
        if len(errors) > 0:
            print('=' * 20 + ' Error log ' + '=' * 20)
        for error in errors:
            print(error)
