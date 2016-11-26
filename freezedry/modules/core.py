import subprocess
import os.path


class Module(object):
    def __init__(self, config):
        self.config = config
        self.roles = []

    def gen_list_from_dicts(self, dictionary):
        items = []
        if dictionary is not None:
            for package_list_name in dictionary:
                current_list = dictionary[package_list_name]
                items += current_list
        return items

    def resolve_and_download(self, uri, dest, processor=None):
        type = uri.split(':')[0]
        if type == 'http' or type == 'https':
            fnm = dest % uri.split('/')[-1]
            subprocess.check_call(['sudo', 'wget', uri, '-O', fnm])
            if processor is not None:
                fnm = processor(fnm)
        else:
            fnm = uri
        return fnm

    def sudo_unzip(self, fnm):
        subprocess.check_call(['sudo', 'unzip', '-o', fnm,
                               '-d', os.path.splitext(fnm)[0]])
        return os.path.splitext(fnm)[0]

    def resolve_attr(self, config, key):
        if key in config.keys():
            return config[key]
        else:
            return None

    def do_root_setup(self, module_pool, logger, livecd=False):
        pass

    def do_user_setup(self, module_pool, logger, livecd=False):
        pass

    def __repr__(self):
        return str(self.config)


class ModulePool(object):
    def __init__(self, modules):
        self.modules = modules

    def __repr__(self):
        return str(self.modules)

    def do_root_setup(self, logger, livecd=False, disable=[]):
        for module in self.modules:
            if module.name not in disable:
                module.do_root_setup(self, logger, livecd)

    def do_user_setup(self, logger, livecd=False, disable=[]):
        for module in self.modules:
            if module.name not in disable:
                module.do_user_setup(self, logger, livecd)

    def broadcast(self, role, action, *args, **kwargs):
        for module in self.modules:
            if role in module.roles:
                getattr(module, action)(*args, **kwargs)
