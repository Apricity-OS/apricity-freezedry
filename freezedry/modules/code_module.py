import subprocess

from freezedry.error import ApplyError
from .core import Module


class CodeModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)
        self.user_code = self.gen_list_from_dicts(config['user'])
        self.root_code = self.gen_list_from_dicts(config['root'])

    def do_root_setup(self, module_pool, logger, livecd=False):
        for line in self.root_code:
            try:
                subprocess.check_call('sudo ' + line, shell=True)
            except Exception as e:
                print(e)
                error_text = 'Failed to run line `%s` of root code' % line
                logger.log_error(ApplyError(error_text))

    def do_user_setup(self, module_pool, logger, livecd=False):
        for line in self.root_code:
            try:
                subprocess.check_call(line, shell=True)
            except Exception as e:
                print(e)
                error_text = 'Failed to run line `%s` of user code' % line
                logger.log_error(ApplyError(error_text))
