class ApplyWarning(object):
    def __init__(self, text):
        self.text = text
        self.level = 1

    def __repr__(self):
        return 'WARNING: %s' % self.text


class ApplyError(object):
    def __init__(self, text):
        self.text = text
        self.level = 2

    def __repr__(self):
        return 'ERROR: %s' % self.text
