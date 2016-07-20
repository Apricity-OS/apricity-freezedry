import subprocess

import os

from .core import Module


class ZshModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.roles = ['shell']
        self.zshrc = self.gen_list_from_dicts(config['zshrc'])
        self.deps = [['zsh']]

    def install_root_zshrc(self, logger):
        tmp_fnm = '/tmp/freezedry_zshrc'
        with open(tmp_fnm, 'w') as f:
            f.write('\n'.join(self.zshrc))
        subprocess.call(
            ['sudo', 'cp', tmp_fnm, '/root/.zshrc'])
        subprocess.call(
            ['sudo', 'cp', tmp_fnm, '/etc/skel/.zshrc'])

    def install_user_zshrc(self, logger):
        zshrc = '\n'.join(self.zshrc)
        with open(os.path.expanduser('~/.zshrc'), 'w') as f:
            f.write(zshrc)

    def do_root_setup(self, module_pool, logger, livecd=False):
        self.install_root_zshrc(logger)
        module_pool.broadcast('package_manager',
                              'install_deps',
                              self.deps,
                              logger)

    def do_user_setup(self, module_pool, logger, livecd=False):
        self.install_user_zshrc(logger)
