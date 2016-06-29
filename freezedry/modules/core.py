class Module(object):
    def __init__(self, config):
        self.config = config
        self.roles = []

    def gen_list_from_dicts(self, dictionary):
        items = []
        for package_list_name in dictionary:
            current_list = dictionary[package_list_name]
            items += current_list
        return items

    def do_root_setup(self, module_pool, logger):
        pass

    def do_user_setup(self, module_pool, logger):
        pass

    def __repr__(self):
        return str(self.config)


class ModulePool(object):

    def __init__(self, modules):
        self.modules = modules

    def __repr__(self):
        return str(self.modules)

    def do_root_setup(self, logger):
        for module in self.modules:
            module.do_root_setup(self, logger)

    def do_user_setup(self, logger):
        for module in self.modules:
            module.do_user_setup(self, logger)

    def broadcast(self, role, action, *args, **kwargs):
        for module in self.modules:
            if role in module.roles:
                getattr(module, action)(*args, **kwargs)
