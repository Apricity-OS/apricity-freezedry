import subprocess

from freezedry.error import ApplyError
from freezedry.lib import any_in
from .core import Module


class PacmanModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.roles = ['package_manager']
        self.packages = self.gen_list_from_dicts(config['packages'])

    def get_installed_packages(self, logger):
        try:
            packages_str = subprocess.check_output(
                ['sudo', 'pacman', '-Qq'])
        except Exception as e:
            print(e)
            error_text = 'Failed to check installed packages'
            logger.log_error(ApplyError(error_text))
        packages = packages_str.splitlines()
        for i, package in enumerate(packages):
            packages[i] = package.decode('utf-8')
        return packages

    def install_dependency(self, dep_options, logger):
        installed_packages = self.get_installed_packages(logger)
        already_installed = any_in(installed_packages, dep_options)
        if not already_installed:
            self.install_packages([dep_options[0]], logger)

    def install_package(self, package, logger):
        command = ['/usr/bin/sudo', 'pacman', '-S', package, '--noconfirm']
        try:
            subprocess.check_call(command)
        except Exception as e:
            print(e)
            error_text = 'Installing package `%s` failed' % package
            logger.log_error(ApplyError(error_text))

    def install_packages(self, packages, logger):
        for package in packages:
            self.install_package(package, logger)

    def do_root_setup(self, module_pool, logger):
        self.install_packages(self.packages, logger)
