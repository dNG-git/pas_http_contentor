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
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasHttpContentorVersion)#
#echo(__FILEPATH__)#
"""

from time import time
import re

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.data_linker import DataLinker
from dNG.pas.data.ownable_mixin import OwnableMixin as OwnableInstance
from dNG.pas.data.settings import Settings
from dNG.pas.data.contentor.category import Category
from dNG.pas.data.contentor.document import Document as _Document
from dNG.pas.data.http.translatable_error import TranslatableError
from dNG.pas.data.http.translatable_exception import TranslatableException
from dNG.pas.data.tasks.database_proxy import DatabaseProxy as DatabaseTasks
from dNG.pas.data.text.input_filter import InputFilter
from dNG.pas.data.text.l10n import L10n
from dNG.pas.data.xhtml.form_tags import FormTags
from dNG.pas.data.xhtml.link import Link
from dNG.pas.data.xhtml.notification_store import NotificationStore
from dNG.pas.data.xhtml.form.form_tags_textarea_field import FormTagsTextareaField
from dNG.pas.data.xhtml.form.processor import Processor as FormProcessor
from dNG.pas.data.xhtml.form.text_field import TextField
from dNG.pas.database.nothing_matched_exception import NothingMatchedException
from dNG.pas.database.transaction_context import TransactionContext
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
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def _check_tag_unique(self, field, validator_context):
	#
		"""
Form validator that checks if the tag is unique if defined.

:param field: Form field
:param validator_context: Form validator context

:return: (str) Error message; None on success
:since:  v0.1.00
		"""

		_return = None

		value = field.get_value()

		if ((validator_context['form'] == "new" or value != validator_context['current_tag'])
		    and len(value) > 0
		    and (not validator_context['category'].is_tag_unique(value))
		   ): _return = L10n.get("pas_http_datalinker_form_error_tag_not_unique")

		return _return
	#

	def execute_edit(self, is_save_mode = False):
	#
		"""
Action for "edit"

:since: v0.1.00
		"""

		did = InputFilter.filter_file_path(self.request.get_dsd("cdid", ""))

		source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		source = source_iline
		if (source_iline == ""): source_iline = "m=contentor;dsd=cdid+{0}".format(Link.encode_query_value(did))

		target = target_iline
		if (target_iline == ""): target_iline = source_iline

		L10n.init("pas_http_contentor")

		try: document = _Document.load_id(did)
		except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_contentor_did_invalid", 404, _exception = handled_exception)

		session = self.request.get_session()
		if (session != None): document.set_permission_session(session)

		if (not document.is_writable()): raise TranslatableError("core_access_denied", 403)

		document_parent = document.load_parent()
		if (isinstance(document_parent, OwnableInstance) and (not document_parent.is_readable_for_session_user(session))): raise TranslatableError("core_access_denied", 403)

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               icon = "mini-default-back",
		               priority = 7
		              )

		if (not DatabaseTasks.is_available()): raise TranslatableException("pas_core_tasks_daemon_not_available")

		document_data = document.get_data_attributes("title", "tag", "content", "description")

		form_id = InputFilter.filter_control_chars(self.request.get_parameter("form_id"))

		form = FormProcessor(form_id)
		form.set_context({ "category": document_parent, "form": "edit", "current_tag": document_data['tag'] })

		document_title = document_data['title']
		document_tag = document_data['tag']
		document_description = document_data['description']
		document_content = document_data['content']

		if (is_save_mode): form.set_input_available()

		field = TextField("ctitle")
		field.set_title(L10n.get("pas_http_contentor_document_title"))
		field.set_value(document_title)
		field.set_required()
		field.set_size(TextField.SIZE_LARGE)
		field.set_limits(int(Settings.get("pas_http_contentor_document_title_min", 3)))
		form.add(field)

		field = TextField("ctag")
		field.set_title(L10n.get("pas_http_contentor_document_tag"))
		field.set_value(document_tag)
		field.set_size(TextField.SIZE_SMALL)
		field.set_limits(_max = 255)
		field.set_validators([ self._check_tag_unique ])
		form.add(field)

		field = FormTagsTextareaField("cdescription")
		field.set_title(L10n.get("pas_http_contentor_document_description"))
		field.set_value(document_description)
		field.set_size(FormTagsTextareaField.SIZE_SMALL)
		field.set_limits(_max = 255)
		form.add(field)

		field = FormTagsTextareaField("ccontent")
		field.set_title(L10n.get("pas_http_contentor_document_content"))
		field.set_value(document_content)
		field.set_required()
		field.set_size(FormTagsTextareaField.SIZE_LARGE)
		field.set_limits(int(Settings.get("pas_http_contentor_document_content_min", 6)))
		form.add(field)

		if (is_save_mode and form.check()):
		#
			document_title = InputFilter.filter_control_chars(form.get_value("ctitle"))
			document_tag = InputFilter.filter_control_chars(form.get_value("ctag"))
			document_description = InputFilter.filter_control_chars(form.get_value("cdescription"))
			document_content = InputFilter.filter_control_chars(form.get_value("ccontent"))

			document.set_data_attributes(time_sortable = time(),
			                             title = document_title,
			                             tag = document_tag,
			                             content = FormTags.encode(document_content),
			                             description = FormTags.encode(document_description)
			                            )

			document.save()

			cid = document_parent.get_id()

			DatabaseTasks.get_instance().add("dNG.pas.contentor.Document.onUpdated.{0}".format(did), "dNG.pas.contentor.Document.onUpdated", 1, category_id = cid, document_id = did)

			target_iline = target_iline.replace("__id_d__", "{0}".format(did))
			target_iline = re.sub("\\_\\w+\\_\\_", "", target_iline)

			NotificationStore.get_instance().add_completed_info(L10n.get("pas_http_contentor_done_document_edit"))

			Link.clear_store("servicemenu")

			redirect_request = PredefinedHttpRequest()
			redirect_request.set_iline(target_iline)
			self.request.redirect(redirect_request)
		#
		else:
		#
			content = { "title": L10n.get("pas_http_contentor_document_edit") }

			content['form'] = { "object": form,
			                    "url_parameters": { "__request__": True,
			                                        "a": "edit-save",
			                                        "dsd": { "source": source, "target": target }
			                                      },
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

		self.execute_edit(self.request.get_type() == "POST")
	#

	def execute_new(self, is_save_mode = False):
	#
		"""
Action for "new"

:since: v0.1.00
		"""

		# pylint: disable=star-args

		cid = InputFilter.filter_file_path(self.request.get_dsd("ccid", ""))
		oid = InputFilter.filter_file_path(self.request.get_dsd("coid", ""))

		source_iline = InputFilter.filter_control_chars(self.request.get_dsd("source", "")).strip()
		target_iline = InputFilter.filter_control_chars(self.request.get_dsd("target", "")).strip()

		source = source_iline

		if (source_iline == ""):
		#
			source_iline = ("m=contentor;dsd=cdid+{0}".format(Link.encode_query_value(oid))
			                if (cid == "") else
			                "m=contentor;dsd=ccid+{0}".format(Link.encode_query_value(cid))
			               )
		#

		target = target_iline
		if (target_iline == ""): target_iline = "m=contentor;dsd=cdid+__id_d__"

		L10n.init("pas_http_contentor")
		L10n.init("pas_http_datalinker")

		if (cid != ""): oid = cid

		try: category = Category.load_id(oid)
		except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_datalinker_oid_invalid", 404, _exception = handled_exception)

		session = self.request.get_session()
		if (isinstance(category, OwnableInstance) and (not category.is_writable_for_session_user(session))): raise TranslatableError("core_access_denied", 403)

		if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

		Link.set_store("servicemenu",
		               Link.TYPE_RELATIVE,
		               L10n.get("core_back"),
		               { "__query__": re.sub("\\_\\_\\w+\\_\\_", "", source_iline) },
		               icon = "mini-default-back",
		               priority = 7
		              )

		if (not DatabaseTasks.is_available()): raise TranslatableException("pas_core_tasks_daemon_not_available")

		form_id = InputFilter.filter_control_chars(self.request.get_parameter("form_id"))

		form = FormProcessor(form_id)
		form.set_context({ "category": category, "form": "new" })

		if (is_save_mode): form.set_input_available()

		field = TextField("ctitle")
		field.set_title(L10n.get("pas_http_contentor_document_title"))
		field.set_required()
		field.set_size(TextField.SIZE_LARGE)
		field.set_limits(int(Settings.get("pas_http_contentor_document_title_min", 3)))
		form.add(field)

		field = TextField("ctag")
		field.set_title(L10n.get("pas_http_contentor_document_tag"))
		field.set_size(TextField.SIZE_SMALL)
		field.set_limits(_max = 255)
		field.set_validators([ self._check_tag_unique ])
		form.add(field)

		field = FormTagsTextareaField("cdescription")
		field.set_title(L10n.get("pas_http_contentor_document_description"))
		field.set_size(FormTagsTextareaField.SIZE_SMALL)
		field.set_limits(_max = 255)
		form.add(field)

		field = FormTagsTextareaField("ccontent")
		field.set_title(L10n.get("pas_http_contentor_document_content"))
		field.set_required()
		field.set_size(FormTagsTextareaField.SIZE_LARGE)
		field.set_limits(int(Settings.get("pas_http_contentor_document_content_min", 6)))
		form.add(field)

		if (is_save_mode and form.check()):
		#
			document = _Document()
			did_d = None

			document_title = InputFilter.filter_control_chars(form.get_value("ctitle"))
			document_tag = InputFilter.filter_control_chars(form.get_value("ctag"))
			document_description = InputFilter.filter_control_chars(form.get_value("cdescription"))
			document_content = InputFilter.filter_control_chars(form.get_value("ccontent"))

			with TransactionContext():
			#
				document_data = { "time_sortable": time(),
				                  "title": document_title,
				                  "tag": document_tag,
				                  "author_ip": self.request.get_client_host(),
				                  "content": FormTags.encode(document_content),
				                  "description": FormTags.encode(document_description)
				                }

				user_profile = (None if (session == None) else session.get_user_profile())
				if (user_profile != None): document_data['author_id'] = user_profile.get_id()

				document.set_data_attributes(**document_data)

				if (isinstance(category, DataLinker)): category.add_entry(document)
				document.save()
			#

			did_d = document.get_id()

			DatabaseTasks.get_instance().add("dNG.pas.contentor.Document.onAdded.{0}".format(did_d), "dNG.pas.contentor.Document.onAdded", 1, category_id = oid, document_id = did_d)

			target_iline = target_iline.replace("__id_d__", "{0}".format(did_d))
			target_iline = re.sub("\\_\\_\\w+\\_\\_", "", target_iline)

			NotificationStore.get_instance().add_completed_info(L10n.get("pas_http_contentor_done_document_new"))

			Link.clear_store("servicemenu")

			redirect_request = PredefinedHttpRequest()
			redirect_request.set_iline(target_iline)
			self.request.redirect(redirect_request)
		#
		else:
		#
			content = { "title": L10n.get("pas_http_contentor_document_new") }

			content['form'] = { "object": form,
			                    "url_parameters": { "__request__": True,
			                                        "a": "new-save",
			                                        "dsd": { "source": source, "target": target }
			                                      },
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

		self.execute_new(self.request.get_type() == "POST")
	#
#

##j## EOF