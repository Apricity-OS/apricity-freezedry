import subprocess

from .core import Module


class GdmModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.roles = ['display_manager']
        self.load_default_xsession()
        self.xsettings_extra = []

    def load_default_xsession(self):
        with open('/etc/freezedry/gdm-xsession-format.sh', 'r') as f:
            self.xsession_format = f.read()

    def append_xsettings(self, xsettings, logger):
        self.xsettings_extra.append(xsettings)
        xsettings = self.xsession_format % '\n'.join(self.xsettings_extra)
        temp_fnm = '/tmp/xsettings_append.txt'
        with open(temp_fnm, 'w') as f:
            f.write(xsettings)
        try:
            subprocess.check_call('su -c \'cat %s > /etc/gdm/Xsession\'' %
                                  temp_fnm, shell=True)
        except Exception as e:
            print(e)
