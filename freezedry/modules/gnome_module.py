import subprocess

import os

from freezedry.error import ApplyError
from .core import Module


class GnomeModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)

        self.gtk_theme = self.resolve_attr(config, 'gtk_theme')
        self.shell_theme = self.resolve_attr(config, 'shell_theme')
        self.icon_theme = self.resolve_attr(config, 'icon_theme')

        self.extensions = self.gen_list_from_dicts(
            self.resolve_attr(config, 'extensions'))
        self.favorite_apps = self.gen_list_from_dicts(
            self.resolve_attr(config, 'favorite_apps'))

        self.wallpaper_uri = self.resolve_attr(config, 'wallpaper')
        self.lock_back_uri = self.resolve_attr(config, 'lock_background')

        self.nautilus = self.resolve_attr(config, 'nautilus')
        if self.nautilus:
            self.nautilus_zoom = self.resolve_attr(self.nautilus,
                                                   'default_zoom')
        self.button_layout = self.resolve_attr(config, 'gtk_button_layout')
        self.dynamic_workspaces = self.resolve_attr(config,
                                                    'dynamic_workspaces')
        self.desktop_icons = self.resolve_attr(config, 'desktop_icons')

        self.deps = [['gnome-shell'],
                     ['gnome-session'],
                     ['mutter'],
                     ['gnome-settings-daemon'],
                     ['gnome-themes-standard']]

    def run_cmd(self, cmd):
        subprocess.check_call(cmd)
        self.cmds.append(cmd)

    def set_gtk_theme(self, logger):
        try:
            fnm = self.resolve_and_download(self.gtk_theme,
                                            '/usr/share/themes/%s',
                                            processor=self.sudo_unzip)
            gtk_theme = os.path.basename(fnm)
            self.run_cmd([
                'gsettings', 'set', 'org.gnome.desktop.interface',
                'gtk-theme', '"%s"' % gtk_theme])
            self.run_cmd([
                'gsettings', 'set', 'org.gnome.desktop.wm.preferences',
                'theme', '"%s"' % gtk_theme])
        except Exception as e:
            print(e)
            error_text = 'Failed to enable gtk theme %s' % self.gtk_theme
            logger.log_error(ApplyError(error_text))

    def set_shell_theme(self, logger):
        try:
            fnm = self.resolve_and_download(self.shell_theme,
                                            '/usr/share/themes/%s',
                                            processor=self.sudo_unzip)
            shell_theme = os.path.basename(fnm)
            self.run_cmd([
                'gsettings', 'set', 'org.gnome.shell.extensions.user-theme',
                'name', '"%s"' % shell_theme])
        except Exception as e:
            print(e)
            error_text = 'Failed to enable shell theme %s' % self.shell_theme
            logger.log_error(ApplyError(error_text))

    def set_icon_theme(self, logger):
        try:
            fnm = self.resolve_and_download(self.icon_theme,
                                            '/usr/share/icons/%s',
                                            processor=self.sudo_unzip)
            icon_theme = os.path.basename(fnm)
            self.run_cmd([
                'gsettings', 'set', 'org.gnome.desktop.interface',
                'icon-theme', '"%s"' % icon_theme])
        except Exception as e:
            print(e)
            error_text = 'Failed to enable icon theme %s' % self.icon_theme
            logger.log_error(ApplyError(error_text))

    def enable_extensions(self, logger):
        try:
            cmd = [
                'gsettings', 'set', 'org.gnome.shell',
                'enabled-extensions', '%s' % str(self.extensions)]
            subprocess.check_call(cmd)
            xcmd = [
                'gsettings', 'set', 'org.gnome.shell',
                'enabled-extensions', '"%s"' % str(self.extensions)]
            self.cmds.append(xcmd)
        except Exception as e:
            print(e)
            error_text = 'Failed to enable gnome shell extensions'
            logger.log_error(ApplyError(error_text))

    def set_favorite_apps(self, logger):
        try:
            cmd = [
                'gsettings', 'set', 'org.gnome.shell',
                'favorite-apps', '%s' % str(self.favorite_apps)]
            subprocess.check_call(cmd)
            xcmd = [
                'gsettings', 'set', 'org.gnome.shell',
                'favorite-apps', '"%s"' % str(self.favorite_apps)]
            self.cmds.append(xcmd)
        except Exception as e:
            print(e)
            error_text = 'Failed to set favorite apps'
            logger.log_error(ApplyError(error_text))

    def set_wallpaper(self, logger):
        try:
            fnm = self.resolve_and_download(self.wallpaper_uri,
                                            '/usr/share/backgrounds/gnome/%s')
            self.run_cmd([
                'gsettings', 'set', 'org.gnome.desktop.background',
                'picture-uri', '"%s"' % fnm])
        except Exception as e:
            print(e)
            error_text = 'Failed to set wallpaper %s' % self.wallpaper_uri
            logger.log_error(ApplyError(error_text))

    def set_lock_back(self, logger):
        try:
            fnm = self.resolve_and_download(self.wallpaper_uri,
                                            '/usr/share/backgrounds/gnome/%s')
            self.run_cmd([
                'gsettings', 'set', 'org.gnome.desktop.screensaver',
                'picture-uri', '"%s"' % fnm])
        except Exception as e:
            print(e)
            error_text = 'Failed to set lock screen background %s' % \
                self.lock_back_uri
            logger.log_error(ApplyError(error_text))

    def set_misc_gnome(self, logger):
        try:
            if self.nautilus and self.nautilus_zoom:
                self.run_cmd([
                    'gsettings', 'set', 'org.gnome.nautilus.icon-view',
                    'default-zoom-level', '"%s"' % self.nautilus_zoom])
            if self.button_layout:
                self.run_cmd([
                    'gsettings', 'set', 'org.gnome.desktop.wm.preferences',
                    'button-layout', '"%s"' % self.button_layout])
                self.run_cmd([
                    'gsettings', 'set',
                    'org.gnome.settings-daemon.plugins.xsettings',
                    'overrides', '{\'Gtk/DecorationLayout\': <\'%s\'>}' %
                    self.button_layout])
            if self.dynamic_workspaces:
                self.run_cmd([
                    'gsettings', 'set', 'org.gnome.shell.overrides',
                    'dynamic-workspaces',
                    str(self.dynamic_workspaces).lower()])
            if self.desktop_icons:
                self.run_cmd([
                    'gsettings', 'set', 'org.gnome.desktop.background',
                    'show-desktop-icons', str(self.desktop_icons).lower()])
        except Exception as e:
            print(e)
            error_text = 'Failed to set misc gnome settings'
            logger.log_error(ApplyError(error_text))

    def set_xsettings(self, module_pool, logger):
        if len(self.cmds):
            xsettings = '\n'.join(' '.join(cmd) for cmd in self.cmds)
            module_pool.broadcast('display_manager',
                                  'append_xsettings',
                                  xsettings, logger)

    def clear_xsettings(self, module_pool, logger):
        module_pool.broadcast('display_manager',
                              'clear_xsettings',
                              logger)

    def set_user_qt5ct(self, logger):
        conf = '''[Appearance]
            color_scheme_path=
            custom_palette=false
            style=gtk2'''
        try:
            os.mkdir(os.path.expanduser('~/.config/qt5ct'))
        except OSError:
            pass
        with open(os.path.expanduser('~/.config/qt5ct/qt5ct.conf'), 'w') as f:
            f.write(conf)

    def set_desktop_environment(self, module_pool, logger, live=False):
        module_pool.broadcast('display_manager',
                              'set_desktop_environment',
                              'gnome',
                              logger,
                              live=live)

    def set_root_qt5ct(self, logger):
        conf = '''[Appearance]
            color_scheme_path=
            custom_palette=false
            style=gtk2'''
        tmp_fnm = '/tmp/freezedry_root_qt5ct.conf'
        with open(tmp_fnm, 'w') as f:
            f.write(conf)
        subprocess.call(
            ['sudo', 'mkdir', '-p', '/root/.config/qt5ct'])
        subprocess.call(
            ['sudo', 'cp', tmp_fnm, '/root/.config/qt5ct/qt5ct.conf'])

    def do_user_setup(self, module_pool, logger, livecd=False):
        self.cmds = []
        if self.gtk_theme:
            self.set_gtk_theme(logger)
        if self.shell_theme:
            self.set_shell_theme(logger)
        if self.icon_theme:
            self.set_icon_theme(logger)
        if self.extensions:
            self.enable_extensions(logger)
        if self.favorite_apps:
            self.set_favorite_apps(logger)
        if self.wallpaper_uri:
            self.set_wallpaper(logger)
        if self.lock_back_uri:
            self.set_lock_back(logger)
        self.set_misc_gnome(logger)
        if livecd:
            self.set_xsettings(module_pool, logger)
        # else:
        #     self.clear_xsettings(module_pool, logger)
        self.set_user_qt5ct(logger)

    def do_root_setup(self, module_pool, logger, livecd=False):
        module_pool.broadcast('package_manager',
                              'install_deps',
                              self.deps,
                              logger, livecd)
        self.set_root_qt5ct(logger)
        self.set_desktop_environment(module_pool, logger,
                                     live=livecd)
        # if not livecd:
        #     self.clear_xsettings(module_pool, logger)
