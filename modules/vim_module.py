import subprocess

import os

import re

from error import ApplyError, ApplyWarning
from lib import cd
from .core import Module


class VimModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.dep_options = ['vim', 'gvim']
        self.plugin_manager = config['plugin_manager']
        self.plugin_repos = self.gen_list_from_dicts(config['plugins'])
        self.check_plugin_manager()
        self.vimrc = []

    def check_plugin_manager(self):
        if self.plugin_manager == 'pathogen':
            pass
        else:
            raise Exception('Invalid plugin manager `%s`' %
                            self.plugin_manager)

    def install_root_pathogen(self, logger):
        subprocess.check_call(['sudo', 'mkdir', '-p',
                               '/etc/skel/.vim/autoload',
                               '/etc/skel/.vim/bundle'])
        subprocess.check_call(['sudo', 'wget',
                               '-O', '/etc/skel/.vim/autoload/pathogen.vim',
                               ('https://raw.githubusercontent.com/'
                                'tpope/vim-pathogen/master/autoload/'
                                'pathogen.vim')])
        self.vimrc.append('execute pathogen#infect()')

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
        self.vimrc.append('execute pathogen#infect()')

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

    def install_root_pathogen_plugin(self, plugin_repo, logger):
        with cd('/etc/skel/.vim/bundle'):
            plugin_name = self.plugin_name_from_repo(plugin_repo)
            print(plugin_name)
            assert self.is_safe(plugin_name)
            if os.path.isdir(plugin_name):
                warn_text = ('Vim plugin `%s` already installed for root, '
                             'reinstalling' %
                             plugin_name)
                logger.log_error(ApplyWarning(warn_text))
                subprocess.check_call(['sudo', 'rm', '-rf',
                                       plugin_name])
            subprocess.check_call(['sudo', 'git', 'clone',
                                   plugin_repo])

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

    def do_root_setup(self, module_pool, logger):
        module_pool.broadcast('package_manager',
                              'install_dependency',
                              self.dep_options,
                              logger)
        self.install_plugin_manager('root', logger)
        for plugin_repo in self.plugin_repos:
            self.install_plugin(plugin_repo, 'root', logger)

    def do_user_setup(self, module_pool, logger):
        self.install_plugin_manager('user', logger)
        for plugin_repo in self.plugin_repos:
            self.install_plugin(plugin_repo, 'user', logger)
