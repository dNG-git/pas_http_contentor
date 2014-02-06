# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.contentor.Index
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

from dNG.pas.data.ownable_mixin import OwnableMixin as OwnableInstance
from dNG.pas.data.contentor.category import Category
from dNG.pas.data.contentor.document import Document
from dNG.pas.data.http.translatable_exception import TranslatableException
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.xhtml.link import Link
from dNG.pas.runtime.value_exception import ValueException
from .module import Module

class Index(Module):
#
	"""
Service for "m=contentor;s=index"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: contentor
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def execute_index(self):
	#
		"""
Action for "index"

:since: v0.1.00
		"""

		if (self.request.is_dsd_set('cdid')): self.execute_view()
		elif (self.request.is_dsd_set('ccid')): self.execute_list()
	#

	def execute_list(self):
	#
		"""
Action for "list"

:since: v0.1.00
		"""

		cid = InputFilter.filter_file_path(self.request.get_dsd("ccid", ""))
		page = int(InputFilter.filter_int(self.request.get_dsd("page", 1)))

		L10n.init("pas_http_contentor")
		L10n.init("pas_http_datalinker")

		try: category = Category.load_id(cid)
		except ValueException as handled_exception: raise TranslatableException("pas_http_contentor_cid_invalid", 404, _exception = handled_exception)

		session = self.request.get_session()

		if (not Category.is_readable_for_session_user(category, session)):
		#
			if (session == None or session.get_user_profile() == None): raise TranslatableException("pas_http_contentor_cid_invalid", 404)
			else: raise TranslatableException("core_access_denied", 403)
		#

		if (Category.is_writable_for_session_user(category, session)):
		#
			Link.store_set(
				"servicemenu", (Link.TYPE_RELATIVE | Link.TYPE_JS_REQUIRED), L10n.get("pas_http_contentor_document_new"),
				{ "m": "contentor", "s": "document", "a": "new", "dsd": { "ccid": cid } },
				image = "mini_default_option", priority = 6
			)
		#

		if (OwnableInstance.is_manageable_for_session_user(category, session)):
		#
			Link.store_set(
				"servicemenu", (Link.TYPE_RELATIVE | Link.TYPE_JS_REQUIRED), L10n.get("pas_http_contentor_category_new"),
				{ "m": "contentor", "s": "category", "a": "new", "dsd": { "ccid": cid } },
				image = "mini_default_option", priority = 6
			)
		#

		category_data = category.data_get("id", "id_main", "title", "time_sortable", "objects", "entry_type")

		content = {
			"id": category_data['id'],
			"title": category_data['title'],
			"time": category_data['time_sortable']
		}

		if (category_data['objects'] > 0): content['objects'] = { "id": category_data['id'], "page": page }

		datalinker_parent = category.load_parent()
		datalinker_parent_data = (None if (datalinker_parent == None) else datalinker_parent.data_get("id", "id_main", "title"))

		if (datalinker_parent_data != None): content['parent'] = { "id": datalinker_parent_data['id'], "main_id": datalinker_parent_data['id_main'], "title": datalinker_parent_data['title'] }

		self.response.init()
		self.response.set_title(category_data['title'])
		self.response.add_oset_content("contentor.list_{0}".format(category_data['entry_type']), content)
	#

	def execute_view(self):
	#
		"""
Action for "view"

:since: v0.1.00
		"""

		did = InputFilter.filter_file_path(self.request.get_dsd("cdid", ""))

		L10n.init("pas_http_contentor")
		L10n.init("pas_http_datalinker")

		try: document = Document.load_id(did)
		except ValueException as handled_exception: raise TranslatableException("pas_http_contentor_did_invalid", 404, _exception = handled_exception)

		session = self.request.get_session()

		if (not Document.is_readable_for_session_user(document, session)):
		#
			if (session == None or session.get_user_profile() == None): raise TranslatableException("pas_http_contentor_did_invalid", 404)
			else: raise TranslatableException("core_access_denied", 403)
		#

		if (Document.is_writable_for_session_user(document, session)):
		#
			Link.store_set(
				"servicemenu", (Link.TYPE_RELATIVE | Link.TYPE_JS_REQUIRED), L10n.get("pas_http_contentor_document_edit"),
				{ "m": "contentor", "s": "document", "a": "edit", "dsd": { "cdid": did } },
				image = "mini_default_option", priority = 6
			)
		#

		category = document.load_parent()

		if (isinstance(category, OwnableInstance) and OwnableInstance.is_writable_for_session_user(category, session)):
		#
			category_data = category.data_get("id")

			Link.store_set(
				"servicemenu", (Link.TYPE_RELATIVE | Link.TYPE_JS_REQUIRED), L10n.get("pas_http_contentor_document_new"),
				{ "m": "contentor", "s": "document", "a": "new", "dsd": { "ccid": category_data['id'], "cdid": did } },
				image = "mini_default_option", priority = 6
			)

			if (OwnableInstance.is_manageable_for_session_user(category, session)):
			#
				Link.store_set(
					"servicemenu", (Link.TYPE_RELATIVE | Link.TYPE_JS_REQUIRED), L10n.get("pas_http_contentor_category_new"),
					{ "m": "contentor", "s": "category", "a": "new", "dsd": { "ccid": category_data['id'], "cdid": did } },
					image = "mini_default_option", priority = 6
				)
			#
		#

		document_data = document.data_get("id", "id_main", "title", "time_sortable", "objects", "objects_sub_type", "content", "author_id", "author_ip", "time_published", "entry_type")

		content = {
			"id": document_data['id'],
			"title": document_data['title'],
			"author": { "id": document_data['author_id'], "ip": document_data['author_ip'] },
			"content": { "content": document_data['content'], "main_id": document_data['id_main'] },
			"time_published": document_data['time_published']
		}

		if (document_data['time_published'] != document_data['time_sortable']): content['time_updated'] = document_data['time_sortable']

		datalinker_parent = document.load_parent()
		datalinker_parent_data = (None if (datalinker_parent == None) else datalinker_parent.data_get("id", "id_main", "title"))

		if (document_data['objects'] > 0 or datalinker_parent_data != None):
		#
			content['objects'] = { "type": document_data['objects_sub_type'], "id": document_data['id'] }

			if (datalinker_parent_data != None):
			#
				content['objects']['parent_id'] = datalinker_parent_data['id']
				content['objects']['parent_main_id'] = datalinker_parent_data['id_main']
				content['objects']['parent_title'] = datalinker_parent_data['title']
			#
		#

		self.response.init(True)
		self.response.set_title(document_data['title'])
		self.response.set_last_modified(document_data['time_sortable'])
		self.response.add_oset_content("contentor.view_{0}".format(document_data['entry_type']), content)
	#
#

##j## EOF