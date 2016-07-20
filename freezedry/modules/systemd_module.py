import subprocess

from freezedry.error import ApplyError
from .core import Module


class SystemdModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.roles = ['service_manager']
        self.services = self.gen_list_from_dicts(config['services'])

    def enable_service(self, service, logger):
        enable = ['/usr/bin/sudo', 'systemctl', 'enable', service]
        start = ['/usr/bin/sudo', 'systemctl', 'start', service]
        try:
            subprocess.check_call(enable)
            subprocess.check_call(start)
        except Exception as e:
            print(e)
            error_text = 'Enabling service `%s` failed' % service
            logger.log_error(ApplyError(error_text))

    def do_root_setup(self, module_pool, logger, livecd=False):
        for service in self.services:
            self.enable_service(service, logger)

    def enable_services(self, services, logger):
        for service in services:
            self.enable_service(service, logger)
