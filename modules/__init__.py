from .pacman_module import *
from .systemd_module import *
from .vim_module import *
from .core import ModulePool

reserved_words = ['inherits']

all_modules = {'pacman': PacmanModule,
               'systemd': SystemdModule,
               'vim': VimModule}
