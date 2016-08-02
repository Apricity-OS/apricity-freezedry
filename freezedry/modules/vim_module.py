import subprocess

import os

import re

from freezedry.error import ApplyError, ApplyWarning
from freezedry.lib import cd
from .core import Module


class VimModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.deps = [['vim', 'gvim']]
        self.plugin_manager = self.resolve_attr(config, 'plugin_manager')
        self.plugin_repos = self.gen_list_from_dicts(
            self.resolve_attr(config, 'plugins'))
        self.vimrc = self.gen_list_from_dicts(
            self.resolve_attr(config, 'vimrc'))
        self.check_plugin_manager()

    def check_plugin_manager(self):
        if self.plugin_manager:
            if self.plugin_manager == 'pathogen':
                self.vimrc.insert(0, 'execute pathogen#infect()')
            else:
                raise Exception('Invalid plugin manager `%s`' %
                                self.plugin_manager)

    def install_root_pathogen_at(self, base_dir, logger):
        subprocess.check_call(['sudo', 'mkdir', '-p',
                               os.path.join(base_dir, '.vim/autoload'),
                               os.path.join(base_dir, '.vim/bundle')])
        subprocess.check_call(['sudo', 'wget',
                               '-O', os.path.join(
                                   base_dir, '.vim/autoload/pathogen.vim'),
                               ('https://raw.githubusercontent.com/'
                                'tpope/vim-pathogen/master/autoload/'
                                'pathogen.vim')])

    def install_root_pathogen(self, logger):
        self.install_root_pathogen_at('/etc/skel', logger)
        self.install_root_pathogen_at('/root', logger)

    def install_user_pathogen(self, logger):
        print('-' * 50)
        subprocess.check_call(['mkdir', '-p',
                               os.path.expanduser('~/.vim/autoload'),
                               os.path.expanduser('~/.vim/bundle')])
        subprocess.check_call(['wget',
                               '-O', os.path.expanduser(
                                   '~/.vim/autoload/pathogen.vim'),
                               ('https://raw.githubusercontent.com/'
                                'tpope/vim-pathogen/master/autoload/'
                                'pathogen.vim')])

    def install_plugin_manager(self, mode, logger):
        if self.plugin_manager == 'pathogen':
            assert mode in ['root', 'user']
            try:
                if mode == 'root':
                    self.install_root_pathogen(logger)
                elif mode == 'user':
                    self.install_user_pathogen(logger)
            except Exception as e:
                print(e)
                error_text = 'Failed to install vim plugin manager pathogen'
                logger.log_error(ApplyError(error_text))

    def plugin_name_from_repo(self, plugin_repo):
        if plugin_repo[-1] == '/':
            plugin_repo = plugin_repo[:-1]
        if plugin_repo[-4:] == '.git':
            plugin_repo = plugin_repo[:-4]
        rest, plugin_name = os.path.split(plugin_repo)
        return plugin_name

    def is_safe(self, plugin_name):
        match = re.match(r'[a-zA-Z_\-]+', plugin_name)
        if match is not None:
            return True
        return False

    def install_root_pathogen_plugin_at(self, base_dir, plugin_repo, logger):
        tmp_path = '/tmp/.vim-root/bundle'
        subprocess.check_call(['sudo', 'rm', '-rf', tmp_path])
        subprocess.check_call(['mkdir', '-p', tmp_path])
        with cd(tmp_path):
            plugin_name = self.plugin_name_from_repo(plugin_repo)
            print(plugin_name)
            assert self.is_safe(plugin_name)
            if os.path.isdir(
                    os.path.join(base_dir, '.vim/bundle', plugin_name)):
                warn_text = ('Vim plugin `%s` already installed at %s, '
                             'reinstalling' %
                             (plugin_name, base_dir))
                logger.log_error(ApplyWarning(warn_text))
            subprocess.check_call(['sudo', 'git', 'clone',
                                   plugin_repo])
        subprocess.check_call(['sudo', 'cp', '-rf',
                               os.path.join(tmp_path, plugin_name),
                               os.path.join(base_dir, '.vim/bundle')])

    def install_root_pathogen_plugin(self, plugin_repo, logger):
        self.install_root_pathogen_plugin_at('/etc/skel', plugin_repo, logger)
        self.install_root_pathogen_plugin_at('/root', plugin_repo, logger)

    def install_user_pathogen_plugin(self, plugin_repo, logger):
        with cd(os.path.expanduser('~/.vim/bundle')):
            plugin_name = self.plugin_name_from_repo(plugin_repo)
            if os.path.isdir(plugin_name):
                warn_text = ('Vim plugin `%s` already installed for current '
                             'user, reinstalling' %
                             plugin_name)
                logger.log_error(ApplyWarning(warn_text))
                subprocess.check_call(['rm', '-rf', plugin_name])
            subprocess.check_call(['git', 'clone',
                                   plugin_repo])

    def install_plugin(self, plugin_repo, mode, logger):
        if self.plugin_manager == 'pathogen':
            assert mode in ['root', 'user']
            try:
                if mode == 'root':
                    self.install_root_pathogen_plugin(plugin_repo, logger)
                elif mode == 'user':
                    self.install_user_pathogen_plugin(plugin_repo, logger)
            except Exception as e:
                print(e)
                error_text = ('Failed to install vim plugin from repo'
                              '`%s` for %s' %
                              (plugin_repo, mode))
                logger.log_error(ApplyError(error_text))

    def install_root_vimrc_at(self, base_dir, vimrc, logger):
        tmp_fnm = '/tmp/.vimrc_temp'
        with open(tmp_fnm, 'w') as f:
            f.write(vimrc)
        try:
            subprocess.check_call([
                'sudo', 'cp', '-f',
                tmp_fnm,
                os.path.join(base_dir, '.vimrc')])
        except Exception as e:
            print(e)
            error_text = 'Failed to install vimrc at %s' % base_dir
            logger.log_error(ApplyError(error_text))

    def install_root_vimrc(self, logger):
        vimrc = '\n'.join(self.vimrc)
        self.install_root_vimrc_at('/etc/skel', vimrc, logger)
        self.install_root_vimrc_at('/root', vimrc, logger)

    def install_user_vimrc(self, logger):
        vimrc = '\n'.join(self.vimrc)
        try:
            with open(os.path.expanduser('~/.vimrc'), 'w') as f:
                f.write(vimrc)
        except Exception as e:
            print(e)
            error_text = 'Failed to install user vimrc'
            logger.log_error(ApplyError(error_text))

    def do_root_setup(self, module_pool, logger, livecd=False):
        module_pool.broadcast('package_manager',
                              'install_deps',
                              self.deps,
                              logger, livecd)
        if self.plugin_manager:
            self.install_plugin_manager('root', logger)
            for plugin_repo in self.plugin_repos:
                self.install_plugin(plugin_repo, 'root', logger)
            self.install_root_vimrc(logger)

    def do_user_setup(self, module_pool, logger, livecd=False):
        if self.plugin_manager:
            self.install_plugin_manager('user', logger)
            for plugin_repo in self.plugin_repos:
                self.install_plugin(plugin_repo, 'user', logger)
            self.install_user_vimrc(logger)
