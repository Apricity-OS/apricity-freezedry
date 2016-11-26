import collections

import toml

import os

from freezedry.modules import all_modules, reserved_words
from freezedry.modules import ModulePool

from freezedry.logger import Logger


def update_recursively(parent_dict, child_dict):
    for key in child_dict.keys():
        if isinstance(child_dict[key], collections.Mapping) and \
                key in parent_dict.keys():
            parent_dict[key] = update_recursively(
                parent_dict[key], child_dict[key])
        else:
            parent_dict[key] = child_dict[key]
    return parent_dict


def build_inheritance(current_fnm):
    with open(current_fnm) as f:
        current_dict = toml.loads(f.read())
    if 'inherits' in current_dict.keys():
        config_dir = os.path.dirname(current_fnm)
        inherits_fnm = os.path.join(config_dir, current_dict['inherits'])
        parent_dict = build_inheritance(inherits_fnm)
        current_dict = update_recursively(parent_dict, current_dict)
    return current_dict


def get_conf_dict(config_fnm):
    return build_inheritance(config_fnm)


def init_modules(conf_dict):
    modules = []
    for module_name in sorted(conf_dict.keys()):
        if module_name in all_modules.keys():
            modules.append(all_modules[module_name](conf_dict[module_name]))
            modules[-1].name = module_name
        elif module_name not in reserved_words:
            raise Exception('Section `%s` not a module or a reserved word' %
                            module_name)
    return modules


def load_config(config_fnm, mode=['user', 'root'], livecd=False, disable=[]):
    conf_dict = get_conf_dict(config_fnm)
    modules = init_modules(conf_dict)
    module_pool = ModulePool(modules)
    logger = Logger()
    if 'root' in mode:
        module_pool.do_root_setup(logger, livecd, disable=disable)
    if 'user' in mode:
        module_pool.do_user_setup(logger, livecd, disable=disable)
    logger.display_errors()


def get_config_fnm():
    return 'apricity.toml'


if __name__ == '__main__':
    config_fnm = get_config_fnm()
    load_config(config_fnm)
