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

import glob
import logging
import os.path
import xml.dom.minidom
import ConfigParser

import gtweak

from gi.repository import Gio, GLib

def fsingleton(cls):
    """
    Singleton decorator that works with GObject derived types. The 'recommended'
    python one - http://wiki.python.org/moin/PythonDecoratorLibrary#Singleton
    does not (interacts badly with GObjectMeta
    """
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@fsingleton
class _GSettingsOverrides:
    def __init__(self):
        logging.debug("Building gsettings override cache")
        self._conf = ConfigParser.RawConfigParser()
        parsed = self._conf.read(
                    glob.glob(os.path.join(gtweak.GSETTINGS_SCHEMA_DIR,"*.override")))

    def override_get_default(self, schema_name, key, default):
        try:
            return self._conf.get(schema_name, key).strip('"')
        except ConfigParser.NoSectionError:
            return default
        except ConfigParser.NoOptionError:
            return default
        except:
            logging.critical("Error parsing gsettings override: %s:%s", schema_name, key)
            return default

class _GSettingsSchema:
    def __init__(self, schema_name, schema_filename=None, **options):
        if not schema_filename:
            schema_filename = schema_name + ".gschema.xml"

        schema_path = os.path.join(gtweak.GSETTINGS_SCHEMA_DIR, schema_filename)
        assert(os.path.exists(schema_path))

        self._schema_name = schema_name
        self._schema = {}

        try:
            dom = xml.dom.minidom.parse(schema_path)
            for schema in dom.getElementsByTagName("schema"):
                if schema_name == schema.getAttribute("id"):
                    for key in schema.getElementsByTagName("key"):
                        #summary is compulsory
                        self._schema[key.getAttribute("name")] = {
                            "summary" : key.getElementsByTagName("summary")[0].childNodes[0].data
                        }

                        #description is optional
                        try:
                            description = {"description" : key.getElementsByTagName("description")[0].childNodes[0].data}
                        except:
                            description = {}

                        #default is optional
                        try:
                            default = {"default" : key.getElementsByTagName("default")[0].childNodes[0].data.strip("'")}
                        except:
                            default = {}

                        self._schema[key.getAttribute("name")].update(description)
                        self._schema[key.getAttribute("name")].update(default)

        except:
            logging.critical("Error parsing schema %s (%s)" % (schema_name, schema_path), exc_info=True)

    def __repr__(self):
        return "<gtweak.gsettings._GSettingsSchema: %s>" % self._schema_name

_SCHEMA_CACHE = {}

class GSettingsSetting(Gio.Settings):
    def __init__(self, schema_name, **options):
        Gio.Settings.__init__(self, schema_name)
        if schema_name not in _SCHEMA_CACHE:
            _SCHEMA_CACHE[schema_name] = _GSettingsSchema(schema_name, **options)
            logging.debug("Caching gsettings: %s" % _SCHEMA_CACHE[schema_name])

        self._schema = _SCHEMA_CACHE[schema_name]

        if gtweak.VERBOSE:
            self.connect("changed", self._on_changed)

    def _on_changed(self, settings, key_name):
        print "Change: %s %s -> %s" % (self.props.schema, key_name, self[key_name])

    def _setting_check_is_list(self, key):
        variant = Gio.Settings.get_value(self, key)
        return variant.get_type_string() == "as"

    def schema_get_summary(self, key):
        return self._schema._schema[key]["summary"]
        
    def schema_get_description(self, key):
        return self._schema._schema[key]["description"]

    def schema_get_default(self, key):
        return self._schema._schema[key].get("default")

    def schema_get_all(self, key):
        return self._schema._schema[key]

    def setting_add_to_list(self, key, value):
        """ helper function, ensures value is present in the GSettingsList at key """
        assert self._setting_check_is_list(key)

        vals = self[key]
        if value not in vals:
            vals.append(value)
            self[key] = vals
            return True

    def setting_remove_from_list(self, key, value):
        """ helper function, removes value in the GSettingsList at key (if present)"""
        assert self._setting_check_is_list(key)

        vals = self[key]
        try:
            vals.remove(value)
            self[key] = vals
            return True
        except ValueError:
            #not present
            pass

    def setting_is_in_list(self, key, value):
        assert self._setting_check_is_list(key)
        return value in self[key]

if __name__ == "__main__":
    gtweak.GSETTINGS_SCHEMA_DIR = "/usr/share/glib-2.0/schemas/"

    logging.basicConfig(level=logging.DEBUG)

    o = _GSettingsOverrides()
    print o.override_get_default("org.gnome.desktop.interface","gtk-theme",None)

    key = "draw-background"
    s = GSettingsSetting("org.gnome.desktop.background")
    print s.schema_get_summary(key), s.schema_get_description(key)

    key = "disabled-extensions"
    s = GSettingsSetting("org.gnome.shell")
    assert s.setting_add_to_list(key, "foo")
    assert s.setting_remove_from_list(key, "foo")
    assert not s.setting_remove_from_list(key, "foo")
