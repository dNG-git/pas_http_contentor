# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;http;contentor

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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasHttpContentorVersion)#
#echo(__FILEPATH__)#
"""

from math import ceil

from dNG.data.contentor.category import Category as _Category
from dNG.data.hookable_settings import HookableSettings
from dNG.data.http.translatable_error import TranslatableError
from dNG.data.ownable_mixin import OwnableMixin as OwnableInstance
from dNG.data.settings import Settings
from dNG.data.text.input_filter import InputFilter
from dNG.data.text.l10n import L10n
from dNG.data.xhtml.link import Link
from dNG.data.xhtml.table.data_linker import DataLinker as DataLinkerTable
from dNG.database.nothing_matched_exception import NothingMatchedException

from .module import Module

class Category(Module):
#
	"""
Service for "m=contentor;s=category"

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: contentor
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def execute_latest_sub_documents(self):
	#
		"""
Action for "latest_sub_documents"

:since: v0.2.00
		"""

		cid = InputFilter.filter_file_path(self.request.get_dsd("ccid", ""))

		source = "m=contentor;s=category;a=latest_sub_documents;dsd=ccid+{0}".format(Link.encode_query_value(cid))

		if (cid == ""): cid = Settings.get("pas_http_contentor_category_default", "")

		L10n.init("pas_http_contentor")
		L10n.init("pas_http_datalinker")

		try: category = _Category.load_id(cid)
		except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_contentor_cid_invalid", 404, _exception = handled_exception)

		session = (self.request.get_session() if (self.request.is_supported("session")) else None)
		if (session is not None): category.set_permission_session(session)

		if (not category.is_readable()):
		#
			if (session is None or session.get_user_profile() is None): raise TranslatableError("pas_http_contentor_cid_invalid", 404)
			else: raise TranslatableError("core_access_denied", 403)
		#

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		if (category.is_manageable()):
		#
			Link.set_store("servicemenu",
			               (Link.TYPE_RELATIVE_URL | Link.TYPE_JS_REQUIRED),
			               L10n.get("pas_http_contentor_category_manage"),
			               { "m": "contentor", "s": "category", "a": "manage", "dsd": { "ccid": cid, "source": source } },
			               icon = "mini-default-option",
			               priority = 3
			              )
		#

		category_data = category.get_data_attributes("id", "id_main", "title", "time_sortable", "categories", "entry_type")

		title = "{0}{1}{2}".format(L10n.get("pas_http_contentor_latest_sub_documents_1"),
		                           category_data['title'],
		                           L10n.get("pas_http_contentor_latest_sub_documents_2")
		                          )

		content = { "id": category_data['id'],
		            "title": title,
		            "time": category_data['time_sortable'],
		            "categories_count": category_data['categories']
		          }

		if (category_data['categories'] > 0):
		#
			content['categories_list'] = [ ]

			hookable_settings = HookableSettings("dNG.pas.http.contentor.DocumentList.getLimit",
			                                     id = cid,
			                                     type = category_data['entry_type']
			                                    )

			limit = hookable_settings.get("pas_http_contentor_list_{0}_document_limit".format(category_data['entry_type']),
			                              20
			                             )

			limit = ceil(limit / category_data['categories'])

			title_renderer_attributes = { "type": DataLinkerTable.COLUMN_RENDERER_CALLBACK_OSET,
			                              "callback": self._get_title_cell_content,
			                              "oset_template_name": "contentor.title_column",
			                              "oset_row_attributes": [ "id", "title" ]
			                            }

			time_sortable_renderer_attributes = { "type": DataLinkerTable.COLUMN_RENDERER_OSET,
			                                      "oset_template_name": "contentor.time_sortable_column",
			                                      "oset_row_attributes": [ "time_sortable", "time_published" ]
			                                    }

			description_renderer_attributes = { "type": DataLinkerTable.COLUMN_RENDERER_OSET,
			                                    "oset_template_name": "contentor.description_column"
			                                  }

			for sub_category in category.get_categories():
			#
				if (sub_category.is_readable_for_session_user(session)):
				#
					sub_category_data = sub_category.get_data_attributes("id", "title", "sub_entries")

					table = DataLinkerTable(sub_category)
					table.add_column("title", L10n.get("pas_http_contentor_document_title"), 35, renderer = title_renderer_attributes)
					table.add_column("time_sortable", L10n.get("pas_http_contentor_document_published"), 15, renderer = time_sortable_renderer_attributes)
					table.add_column("description", L10n.get("pas_http_contentor_document_description"), 50, renderer = description_renderer_attributes)

					table.add_sort_definition("time_sortable", DataLinkerTable.SORT_DESCENDING)
					table.disable_sort("description")
					table.set_limit(limit)

					link = { "m": "contentor", "dsd": { "ccid": sub_category_data['id'] } }

					content['categories_list'].append({ "id": sub_category_data['id'],
					                                    "title": sub_category_data['title'],
					                                    "link": Link().build_url(Link.TYPE_RELATIVE_URL, link),
					                                    "sub_entries_count": sub_category_data['sub_entries'],
					                                    "object": table
					                                  })
				#
			#
		#

		category_parent = category.load_parent()

		if (category_parent is not None
		    and ((not isinstance(category_parent, OwnableInstance))
		         or category_parent.is_readable_for_session_user(session)
		        )
		   ):
		#
			category_parent_data = category_parent.get_data_attributes("id", "id_main", "title")

			if (category_parent_data['id'] != cid):
			#
				content['parent'] = { "id": category_parent_data['id'],
				                      "main_id": category_parent_data['id_main'],
				                      "title": category_parent_data['title']
				                    }
		#

		self.response.init(True)
		self.response.set_expires_relative(+15)
		self.response.set_title(title)
		self.response.add_oset_content("contentor.latest_sub_documents_list".format(category_data['entry_type']), content)
	#

	def _get_title_cell_content(self, content, column_definition):
	#
		"""
Returns content used for title cell rendering.

:param content: Content already defined
:param column_definition: Column definition for the cell

:return: (dict) Content used for rendering
:since:  v0.2.00
		"""

		_return = content

		link = { "m": "contentor", "dsd": { "cdid": content['id'] } }
		_return['link'] = Link().build_url(Link.TYPE_RELATIVE_URL, link)

		return _return
	#
#

##j## EOF