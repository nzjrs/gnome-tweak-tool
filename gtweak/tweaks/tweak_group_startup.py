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

from __future__ import print_function

from gi.repository import Gtk, GLib, Gio

from gtweak.tweakmodel import Tweak
from gtweak.widgets import ListBoxTweakGroup, UI_BOX_SPACING
from gtweak.utils import AutostartManager

class _StartupTweak(Gtk.ListBoxRow, Tweak):
    def __init__(self, filename, **options):
        df = Gio.DesktopAppInfo.new_from_filename(filename)

        Gtk.ListBoxRow.__init__(self)
        Tweak.__init__(self, 
                        df.get_name(),
                        df.get_description(),
                        **options)
        
        grid = Gtk.Grid(column_spacing=10)

        img = Gtk.Image.new_from_gicon(df.get_icon(),Gtk.IconSize.DIALOG)
        grid.attach(img, 0, 0, 1, 1)

        lbl = Gtk.Label(df.get_name(), xalign=0.0)
        grid.attach_next_to(lbl,img,Gtk.PositionType.RIGHT,1,1)
        lbl.props.hexpand = True
        lbl.props.halign = Gtk.Align.START

        btn = Gtk.Button("Remove")
        grid.attach_next_to(btn,lbl,Gtk.PositionType.RIGHT,1,1)
        btn.props.vexpand = False
        btn.props.valign = Gtk.Align.CENTER

        self.add(grid)

        self.props.margin = 5
        self.get_style_context().add_class('tweak-white')
    
class AutostartListBoxTweakGroup(ListBoxTweakGroup):
    def __init__(self):
        tweaks = []

        files = AutostartManager.get_user_autostart_files()
        for f in files:
            tweaks.append( _StartupTweak(f) )


        ListBoxTweakGroup.__init__(self,
            "Startup Applications",
            *tweaks,
            css_class='tweak-group-white')
        self.set_header_func(self._list_header_func, None)
        
        btn = Gtk.Button("")
        btn.get_style_context().remove_class("button")
        img = Gtk.Image()
        img.set_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        btn.set_image(img)
        btn.props.always_show_image = True
        btn.connect("clicked", self._on_add_clicked)
        #b.props.hexpand = True
        #b.props.vexpand = True
        self.add(btn)

    def _on_add_clicked(self, btn):
        print("234")

    def _list_header_func(self, row, before, user_data):
        if before and not row.get_header():
            row.set_header (Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))


TWEAK_GROUPS = [
    AutostartListBoxTweakGroup(),
]
