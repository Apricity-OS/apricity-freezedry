import subprocess

from freezedry.error import ApplyError
from freezedry.lib import any_in
from .core import Module


class PacmanModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.roles = ['package_manager']
        self.packages = self.gen_list_from_dicts(
            self.resolve_attr(config, 'packages'))
        self.keyrings = self.resolve_attr(config, 'keyrings')
        self.pacman_setup = False

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

    def install_deps(self, deps, logger, livecd=False):
        if not self.pacman_setup:
            self.setup_pacman(logger)
        for dep_options in deps:
            installed_packages = self.get_installed_packages(logger)
            already_installed = any_in(installed_packages, dep_options)
            if not already_installed:
                self.install_packages([dep_options[0]], logger, livecd)

    def install_package(self, package, logger, live=False):
        command = ['yaourt', '-S', package,
                   '--noconfirm', '--needed']
        try:
            subprocess.check_call(command)
        except Exception as e:
            if live:
                print(e)
                error_text = 'Installing package `%s` failed' % package
                logger.log_error(ApplyError(error_text))
            else:
                try:
                    subprocess.check_call(['yaourt', '-S',
                                           package, '--needed'])
                except Exception as e:
                    print(e)
                    error_text = 'Installing package `%s` failed' % package
                    logger.log_error(ApplyError(error_text))

    def install_packages(self, packages, logger, livecd=False):
        for package in packages:
            self.install_package(package, logger, livecd)

    def setup_pacman(self, logger):
        if self.keyrings:
            for keyring in self.keyrings:
                for attempt in range(4):
                    subprocess.call(
                        ['sudo', 'pacman-key', '--init', keyring])
                    subprocess.call(
                        ['sudo', 'pacman-key', '--populate', keyring])
        subprocess.call(['sudo', 'pacman', '-Syy'])
        subprocess.call(['sudo', 'pacman', '-S', 'yaourt-git', '--noconfirm'])
        self.pacman_setup = True

    def do_root_setup(self, module_pool, logger, livecd=False):
        if not self.pacman_setup:
            self.setup_pacman(logger)
        self.install_packages(self.packages, logger, livecd)
