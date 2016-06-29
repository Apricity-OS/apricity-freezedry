import subprocess

from freezedry.error import ApplyError
from .core import Module


class GnomeModule(Module):
    def __init__(self, config, **kwargs):
        Module.__init__(self, config, **kwargs)

        self.gtk_theme = config['gtk_theme']
        self.shell_theme = config['shell_theme']
        self.icon_theme = config['icon_theme']

        self.extensions = self.gen_list_from_dicts(config['extensions'])
        self.favorite_apps = self.gen_list_from_dicts(config['favorite_apps'])

        self.wallpaper_fnm = config['wallpaper']
        self.lock_back_fnm = config['lock_background']

        self.nautilus_zoom = config['nautilus']['default_zoom']
        self.button_layout = config['gtk_button_layout']
        self.dynamic_workspaces = config['dynamic_workspaces']
        self.desktop_icons = config['desktop_icons']

    def set_gtk_theme(self, logger):
        try:
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.desktop.interface',
                'gtk-theme', '"%s"' % self.gtk_theme])
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.desktop.wm.preferences',
                'theme', '"%s"' % self.gtk_theme])
        except Exception as e:
            print(e)
            error_text = 'Failed to enable gtk theme %s' % self.gtk_theme
            logger.log_error(ApplyError(error_text))

    def set_shell_theme(self, logger):
        try:
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.shell.extensions.user-theme',
                'name', '"%s"' % self.shell_theme])
        except Exception as e:
            print(e)
            error_text = 'Failed to enable shell theme %s' % self.shell_theme
            logger.log_error(ApplyError(error_text))

    def set_icon_theme(self, logger):
        try:
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.desktop.interface',
                'icon-theme', '"%s"' % self.icon_theme])
        except Exception as e:
            print(e)
            error_text = 'Failed to enable icon theme %s' % self.icon_theme
            logger.log_error(ApplyError(error_text))

    def enable_extensions(self, logger):
        try:
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.shell',
                'enabled-extensions', '%s' % str(self.extensions)])
        except Exception as e:
            print(e)
            error_text = 'Failed to enable gnome shell extensions'
            logger.log_error(ApplyError(error_text))

    def set_favorite_apps(self, logger):
        try:
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.shell',
                'favorite-apps', '%s' % str(self.favorite_apps)])
        except Exception as e:
            print(e)
            error_text = 'Failed to set favorite apps'
            logger.log_error(ApplyError(error_text))

    def set_wallpaper(self, logger):
        try:
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.desktop.background',
                'picture-uri', '"%s"' % self.wallpaper_fnm])
        except Exception as e:
            print(e)
            error_text = 'Failed to set wallpaper %s' % self.wallpaper_fnm
            logger.log_error(ApplyError(error_text))

    def set_lock_back(self, logger):
        try:
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.desktop.screensaver',
                'picture-uri', '"%s"' % self.lock_back_fnm])
        except Exception as e:
            print(e)
            error_text = 'Failed to set lock screen background %s' % \
                self.lock_back_fnm
            logger.log_error(ApplyError(error_text))

    def set_misc_gnome(self, logger):
        try:
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.nautilus.icon-view',
                'default-zoom-level', '"%s"' % self.nautilus_zoom])
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.desktop.wm.preferences',
                'button-layout', '"%s"' % self.button_layout])
            subprocess.check_call([
                'gsettings', 'set',
                'org.gnome.settings-daemon.plugins.xsettings',
                'overrides', '{\'Gtk/DecorationLayout\': <\'%s\'>}' %
                self.button_layout])
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.shell.overrides',
                'dynamic-workspaces', str(self.dynamic_workspaces).lower()])
            subprocess.check_call([
                'gsettings', 'set', 'org.gnome.desktop.background',
                'show-desktop-icons', str(self.desktop_icons).lower()])
        except Exception as e:
            print(e)
            error_text = 'Failed to set misc gnome settings'
            logger.log_error(ApplyError(error_text))

    def do_user_setup(self, module_pool, logger):
        self.set_gtk_theme(logger)
        self.set_shell_theme(logger)
        self.set_icon_theme(logger)
        self.enable_extensions(logger)
        self.set_favorite_apps(logger)
        self.set_wallpaper(logger)
        self.set_lock_back(logger)
        self.set_misc_gnome(logger)
