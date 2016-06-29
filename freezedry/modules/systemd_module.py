import subprocess

from freezedry.error import ApplyError
from .core import Module


class SystemdModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.roles = ['service_manager']
        self.services = self.gen_list_from_dicts(config['services'])

    def do_root_setup(self, module_pool, logger):
        for service in self.services:
            command = ['/usr/bin/sudo', 'systemctl', 'enable', service]
            try:
                subprocess.check_call(command)
            except Exception as e:
                print(e)
                error_text = 'Enabling service `%s` failed' % service
                logger.log_error(ApplyError(error_text))
