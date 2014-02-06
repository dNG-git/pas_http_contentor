# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.contentor.DocumentList
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

from dNG.pas.data.contentor.category import Category
from dNG.pas.data.hookable_settings import HookableSettings
from dNG.pas.data.http.translatable_exception import TranslatableException
from .module import Module

class DocumentList(Module):
#
	"""
"DocumentList" creates a list of documents of different types.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: contentor
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def execute_render_simple(self):
	#
		"""
Action for "render_simple"

:since: v0.1.00
		"""

		if ("id" in self.context): self._render(self.context['id'])
		else: raise TranslatableException("core_unknown_error", "Missing service list to render")
	#

	def _render(self, _id):
	#
		"""
List renderer

:since: v0.1.00
		"""

		category = Category.load_id(_id)
		category_data = category.data_get("objects", "entry_type")

		page = (self.context['page'] if ("page" in self.context) else 1)

		if (category_data['entry_type'] == "simple"): limit_default = 20
		else: limit_default = 20

		limit = HookableSettings(
			"dNG.pas.http.contentor.DocumentList.get_limit",
			id = _id,
			type = category_data['entry_type']
		).get("pas_http_contentor_document_list_{0}_limit".format(category_data['entry_type']), limit_default)

		offset = (0 if (page < 1 or (page * limit) > category_data['objects']) else (page - 1) * limit)

		self.set_action_result("data")
	#
#

##j## EOF