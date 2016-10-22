import subprocess
from glob import glob
import os.path

from .core import Module


class GdmModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.roles = ['display_manager']
        self.load_default_xsession()
        self.load_default_de()
        self.xsettings_extra = []
        self.deps = [['gdm']]
        self.services = ['gdm']

    def load_default_de(self):
        with open('/etc/freezedry/gdm-custom-format.conf', 'r') as f:
            self.gdm_custom_format = f.read()
        with open('/etc/freezedry/gdm-custom-live-format.conf', 'r') as f:
            self.gdm_custom_live_format = f.read()
        with open('/etc/freezedry/gdm-account-format.conf', 'r') as f:
            self.gdm_account_format = f.read()

    def set_desktop_environment(self, desktop_environment, logger, live=False):
        account_format = self.gdm_account_format % desktop_environment
        tmp_fnm = '/tmp/gdm_account.conf'
        with open(tmp_fnm, 'w') as f:
            f.write(account_format)
        subprocess.check_call(['sudo', 'mkdir', '-p',
                               '/var/lib/AccountsService/users'])
        for f in glob('/home/*'):
            username = os.path.basename(f)
            subprocess.check_call(
                'su -c \'cat %s > /var/lib/AccountsService/users/%s\'' %
                (tmp_fnm, username), shell=True)
            subprocess.call(['sudo', 'rm',
                             '/home/%s/.firstrun.ran' % username])
        tmp_fnm = '/tmp/gdm_custom.conf'
        if live:
            custom_conf = self.gdm_custom_live_format
        else:
            custom_conf = self.gdm_custom_format
        with open(tmp_fnm, 'w') as f:
            f.write(custom_conf)
        print('Writing custom.conf')
        subprocess.check_call(['sudo', 'cp', '-f', tmp_fnm,
                               '/etc/gdm/custom.conf'])
        # subprocess.check_call([
        #     'sudo', 'sed', '-i', 's/gnome/%s/g' % desktop_environment,
        #     '/var/lib/AccountsService/users/%s' % os.environ['USER']])

    def load_default_xsession(self):
        with open('/etc/freezedry/gdm-xsession-format.sh', 'r') as f:
            self.xsession_format = f.read()

    def clear_xsettings(self, logger):
        self.xsettings_extra = []
        self.append_xsettings('', logger)

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
                              logger, livecd)

        module_pool.broadcast('service_manager',
                              'enable_services',
                              self.services,
                              logger)
