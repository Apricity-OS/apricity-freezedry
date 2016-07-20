import subprocess


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

    def resolve_and_download(self, uri, dest):
        type = self.wallpaper_uri.split(':')[0]
        if type == 'http' or type == 'https':
            file = uri.split('/')[-1]
            fnm = dest % file
            subprocess.check_call(['sudo', 'wget', uri, '-O', fnm])
        else:
            fnm = uri
        return fnm

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

    def do_root_setup(self, logger, livecd=False):
        for module in self.modules:
            module.do_root_setup(self, logger, livecd)

    def do_user_setup(self, logger, livecd=False):
        for module in self.modules:
            module.do_user_setup(self, logger, livecd)

    def broadcast(self, role, action, *args, **kwargs):
        for module in self.modules:
            if role in module.roles:
                getattr(module, action)(*args, **kwargs)
