import subprocess

from .core import Module


class GdmModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.roles = ['display_manager']
        self.load_default_xsession()
        self.xsettings_extra = []
        self.deps = [['gdm']]
        self.services = ['gdm']

    def load_default_xsession(self):
        with open('/etc/freezedry/gdm-xsession-format.sh', 'r') as f:
            self.xsession_format = f.read()

    def clear_xsettings(self, logger):
        self.xsettings_extra = []
        self.append_xsettings([], logger)

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

    def do_root_setup(self, module_pool, logger, livecd=False):
        module_pool.broadcast('package_manager',
                              'install_deps',
                              self.deps,
                              logger)

        module_pool.broadcast('service_manager',
                              'enable_services',
                              self.services,
                              logger)
