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

import json
import logging

from gi.repository import GObject
from gi.repository import Soup, SoupGNOME

class ExtensionsDotGnomeDotOrg(GObject.GObject):

    __gsignals__ = {
      "got-extensions": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
            (GObject.TYPE_PYOBJECT,)),
      "got-extension-info": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
            (GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        self._session = Soup.SessionAsync.new()
        self._session.add_feature_by_type(SoupGNOME.ProxyResolverGNOME)

    def _query_extensions_finished(self, msg):
        if msg.status_code == 200:
            #server returns a list of extensions which may contain duplicates
            extensions = {}
            for e in json.loads(msg.response_body.data):
                extensions[e["uuid"]] = e
            self.emit("got-extensions", extensions)

    def _query_extension_info_finished(self, msg):
        if msg.status_code == 200:
            self.emit("got-extension-info", json.loads(msg.response_body.data))

    def query_extensions(self, shell_version_tuple):
        url = "https://extensions.gnome.org/extension-query/?"

        if shell_version_tuple[1] % 2:
            #if this is a development version (odd) then query the full version
            url += "shell_version=%d.%d.%d" % shell_version_tuple
        else:
            #else query in point releases up to the current version, and filter duplicates
            #from the reply
            url += "shell_version=%d.%d&" % (shell_version_tuple[0],shell_version_tuple[1])
            for i in range(1,shell_version_tuple[2]+1):
                url += "shell_version=%d.%d.%d&" % (shell_version_tuple[0],shell_version_tuple[1], i)

        logging.debug("Query URL: %s" % url)

        message = Soup.Message.new('GET', url)
        message.connect("finished", self._query_extensions_finished)
        self._session.queue_message(message, None, None)

    def query_extension_info(self, extension_uuid):
        url = "https://extensions.gnome.org/extension-info/?uuid=%s" % extension_uuid

        logging.debug("Query URL: %s" % url)

        message = Soup.Message.new('GET', url)
        message.connect("finished", self._query_extension_info_finished)
        self._session.queue_message(message, None, None)


if __name__ == "__main__":
    import pprint
    from gi.repository import Gtk

    def _got_ext(ego, extensions, i):
        print "="*80
        pprint.pprint(extensions.values())
        i[0] -= 1
        if i[0] == 0:
            Gtk.main_quit()

    logging.basicConfig(format="%(levelname)-8s: %(message)s", level=logging.DEBUG)

    e = ExtensionsDotGnomeDotOrg()

    i = [4]
    e.connect("got-extensions", _got_ext, i)
    e.connect("got-extension-info", _got_ext, i)

    e.query_extensions((3,2,0))
    e.query_extensions((3,2,2))
    e.query_extensions((3,3,2))
    e.query_extension_info("user-theme@gnome-shell-extensions.gcampax.github.com")

    Gtk.main()
