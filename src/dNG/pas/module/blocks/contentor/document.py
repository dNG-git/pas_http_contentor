# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.contentor.Document
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

from time import time
import re

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.data_linker import DataLinker
from dNG.pas.data.ownable_mixin import OwnableMixin as OwnableInstance
from dNG.pas.data.settings import Settings
from dNG.pas.data.contentor.category import Category
from dNG.pas.data.contentor.document import Document as _Document
from dNG.pas.data.http.translatable_exception import TranslatableException
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.xhtml.form_tags import FormTags
from dNG.pas.data.xhtml.link import Link
from dNG.pas.data.xhtml.notification_store import NotificationStore
from dNG.pas.database.transaction_context import TransactionContext
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.runtime.value_exception import ValueException
from .module import Module

class Document(Module):
#
	"""
Service for "m=contentor;s=document"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: contentor
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def execute_edit(self, is_save_mode = False):
	#
		"""
Action for "edit"

:since: v0.1.00
		"""

		did = InputFilter.filter_file_path(self.request.get_dsd("cdid", ""))

		source = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		source_iline = (Link.query_param_decode(source) if (source != "") else "m=contentor;dsd=cdid+{0}".format(did))

		if (target != ""): target_iline = Link.query_param_decode(target)
		else:
		#
			target = source
			target_iline = source_iline
		#

		L10n.init("pas_http_contentor")

		try: document = _Document.load_id(did)
		except ValueException as handled_exception: raise TranslatableException("pas_http_contentor_did_invalid", 404, _exception = handled_exception)

		session = self.request.get_session()
		if (not _Document.is_writable_for_session_user(document, session)): raise TranslatableException("core_access_denied", 403)

		Link.store_set("servicemenu", Link.TYPE_RELATIVE, L10n.get("core_back"), { "__query__": re.sub("\\[\\w+\\]", "", source_iline) }, image = "mini_default_back", priority = 2)

		form = NamedLoader.get_instance("dNG.pas.data.xhtml.form.Input", True)

		document_data = document.data_get("title", "tag", "content")

		document_title = None
		document_tag = None
		document_content = None

		if (is_save_mode):
		#
			form.set_input_available()
		#
		else:
		#
			document_title = document_data['title']
			document_tag = document_data['tag']
			document_content = document_data['content']
		#

		form.entry_add_text({
			"name": "ctitle",
			"title": L10n.get("pas_http_contentor_document_title"),
			"content": document_title,
			"required": True,
			"size": "l",
			"min": int(Settings.get("pas_core_username_min", 3))
		})

		form.entry_add_text({
			"name": "ctag",
			"title": L10n.get("pas_http_contentor_document_tag"),
			"content": document_tag,
			"required": True,
			"size": "s",
			"max": 255
		})

		form.entry_add_textarea({
			"name": "ccontent",
			"title": L10n.get("pas_http_contentor_document_content"),
			"content": document_content,
			"required": True,
			"size": "l",
			"min": int(Settings.get("pas_http_user_profile_password_min", 6))
		})

		if (is_save_mode and form.check()):
		#
			document_title = InputFilter.filter_control_chars(form.get_value("ctitle"))
			document_tag = InputFilter.filter_control_chars(form.get_value("ctag"))
			document_content = InputFilter.filter_control_chars(form.get_value("ccontent"))

			document.data_set(
				time_sortable = time(),
				title = FormTags.encode(document_title),
				tag = document_tag,
				content = FormTags.encode(document_content)
			)

			document.save()

			target_iline = target_iline.replace("[id_d]", "{0}".format(did))
			target_iline = re.sub("\\[\\w+\\]", "", target_iline)

			NotificationStore.get_instance().add_completed_info(L10n.get("pas_http_contentor_done_document_edit"))

			Link.store_clear("servicemenu")

			redirect_request = PredefinedHttpRequest()
			redirect_request.set_iline(target_iline)
			self.request.redirect(redirect_request)
		#
		else:
		#
			content = { "title": L10n.get("pas_http_contentor_document_edit") }

			content['form'] = {
				"object": form,
				"url_parameters": { "__request__": True, "a": "edit-save", "dsd": { "source": source, "target": target } },
				"button_title": "pas_http_core_edit"
			}

			self.response.init()
			self.response.set_title(L10n.get("pas_http_contentor_document_edit"))
			self.response.add_oset_content("core.form", content)
		#
	#

	def execute_edit_save(self):
	#
		"""
Action for "edit-save"

:since: v0.1.00
		"""

		self.execute_edit(True)
	#

	def execute_new(self, is_save_mode = False):
	#
		"""
Action for "new"

:since: v0.1.00
		"""

		cid = InputFilter.filter_file_path(self.request.get_dsd("ccid", ""))
		did = InputFilter.filter_file_path(self.request.get_dsd("cdid", ""))

		source = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		if (source != ""): source_iline = Link.query_param_decode(source)
		elif (did != ""): source_iline = "m=contentor;dsd=cdid+{0}".format(did)
		else: source_iline = "m=contentor;a=list;dsd=ccid+{0}".format(cid)

		target_iline = ("m=contentor;dsd=cdid+[id_d]" if (target == "") else Link.query_param_decode(target))

		L10n.init("pas_http_contentor")

		oid = (cid if (did == "") else did)

		try: category = Category.load_id(oid)
		except ValueException as handled_exception: raise TranslatableException("pas_http_contentor_cid_invalid", 404, _exception = handled_exception)

		session = self.request.get_session()
		if ((not isinstance(category, OwnableInstance)) or (not OwnableInstance.is_writable_for_session_user(category, session))): raise TranslatableException("core_access_denied", 403)

		Link.store_set("servicemenu", Link.TYPE_RELATIVE, L10n.get("core_back"), { "__query__": re.sub("\\[\\w+\\]", "", source_iline) }, image = "mini_default_back", priority = 2)

		form = NamedLoader.get_instance("dNG.pas.data.xhtml.form.Input", True)

		if (is_save_mode):
		#
			form.set_input_available()
		#
		else:
		#
			pass
		#

		form.entry_add_text({
			"name": "ctitle",
			"title": L10n.get("pas_http_contentor_document_title"),
			"required": True,
			"size": "l",
			"min": int(Settings.get("pas_core_username_min", 3))
		})

		form.entry_add_text({
			"name": "ctag",
			"title": L10n.get("pas_http_contentor_document_tag"),
			"required": True,
			"size": "s",
			"max": 255
		})

		form.entry_add_textarea({
			"name": "ccontent",
			"title": L10n.get("pas_http_contentor_document_content"),
			"required": True,
			"size": "l",
			"min": int(Settings.get("pas_http_user_profile_password_min", 6))
		})

		if (is_save_mode and form.check()):
		#
			document = _Document()
			did_d = None

			with TransactionContext():
			#
				document_title = InputFilter.filter_control_chars(form.get_value("ctitle"))
				document_tag = InputFilter.filter_control_chars(form.get_value("ctag"))
				document_content = InputFilter.filter_control_chars(form.get_value("ccontent"))

				document_data = {
					"time_sortable": time(),
					"title": FormTags.encode(document_title),
					"tag": document_tag,
					"author_ip": self.request.get_client_host(),
					"content": FormTags.encode(document_content)
				}

				user_profile = (None if (session == None) else session.get_user_profile())
				if (user_profile != None): document_data['author_id'] = user_profile.get_id()

				document.data_set(**document_data)
				if (isinstance(category, DataLinker)): category.object_add(document)

				document.save()

				document_data = document.data_get("id")
				did_d = document_data['id']
			#

			target_iline = target_iline.replace("[id_d]", "{0}".format(did_d))
			target_iline = re.sub("\\[\\w+\\]", "", target_iline)

			NotificationStore.get_instance().add_completed_info(L10n.get("pas_http_contentor_done_document_new"))

			Link.store_clear("servicemenu")

			redirect_request = PredefinedHttpRequest()
			redirect_request.set_iline(target_iline)
			self.request.redirect(redirect_request)
		#
		else:
		#
			content = { "title": L10n.get("pas_http_contentor_document_new") }

			content['form'] = {
				"object": form,
				"url_parameters": { "__request__": True, "a": "new-save", "dsd": { "source": source, "target": target } },
				"button_title": "pas_core_save"
			}

			self.response.init()
			self.response.set_title(L10n.get("pas_http_contentor_document_new"))
			self.response.add_oset_content("core.form", content)
		#
	#

	def execute_new_save(self):
	#
		"""
Action for "new-save"

:since: v0.1.00
		"""

		self.execute_new(True)
	#
#

##j## EOF