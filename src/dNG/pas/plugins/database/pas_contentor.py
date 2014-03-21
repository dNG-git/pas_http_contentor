# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.plugins.database.pas_contentor
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;http;contentor

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;gpl
----------------------------------------------------------------------------
#echo(pasHttpContentorVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

# pylint: disable=unused-argument

from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.plugins.hooks import Hooks

def plugin_db_load_all(params = None, last_return = None):
#
	"""
Load and register all SQLAlchemy objects to generate database tables.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.1.00
	"""

	NamedLoader.get_instance("dNG.pas.database.instances.ContentorCategory")
	NamedLoader.get_instance("dNG.pas.database.instances.ContentorDocument")

	return last_return
#

def plugin_deregistration():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hooks.unregister("dNG.pas.Database.loadAll", plugin_db_load_all)
#

def plugin_registration():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hooks.register("dNG.pas.Database.loadAll", plugin_db_load_all)
#

##j## EOF