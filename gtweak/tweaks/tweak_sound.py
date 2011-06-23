# This file is part of gnome-tweak-tool.
#
# Copyright (c) 2011 John Stowers
#
# gnome-tweak-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gnome-tweak-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gnome-tweak-tool.  If not, see <http://www.gnu.org/licenses/>.

import os.path

from gi.repository import GLib, Gtk, Gio

from gtweak.utils import walk_directories, make_combo_list_with_default
from gtweak.tweakmodel import Tweak, TweakGroup
from gtweak.gsettings import GSettingsSetting
from gtweak.widgets import GSettingsSwitchTweak, build_label_beside_widget, build_horizontal_sizegroup, build_combo_box_text

class SoundThemeSwitcher(Tweak):

    def __init__(self, **options):
        Tweak.__init__(self, "Sound Theme", "", **options)

        self._settings = GSettingsSetting("org.gnome.desktop.sound")

        dirs = [os.path.join(d, "sounds") for d in 
                    GLib.get_system_data_dirs() + [GLib.get_user_data_dir()]]
        valid = walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "index.theme")) and \
                    True)

        cb = build_combo_box_text(
                self._settings.get_string("theme-name"),
                *make_combo_list_with_default(
                    valid,
                    "freedesktop"))

        play = Gtk.Button()
        play.set_image(
                    Gtk.Image.new_from_icon_name(
                            "media-playback-start-symbolic", Gtk.IconSize.BUTTON))
        play.connect("clicked", self._play_sound, cb)

        self.widget = build_label_beside_widget(self.name, play, cb)
        self.widget_for_size_group = cb

    def _play_sound(self, btn, cb):
        uri = "file:///usr/share/sounds/freedesktop/stereo/message.oga"

        #FIXME: GLib.spawn_async is preferred, but broken
        Gio.app_info_create_from_commandline(
                'gst-launch-0.10 -q playbin uri=%s' % uri, None, 0).launch([], None)

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = (
        TweakGroup(
            _("Sound"),
            GSettingsSwitchTweak("org.gnome.desktop.sound", "event-sounds"),
            SoundThemeSwitcher(size_group=sg)),
)
