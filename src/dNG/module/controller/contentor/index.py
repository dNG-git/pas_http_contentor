# -*- coding: utf-8 -*-

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

from dNG.data.contentor.category import Category
from dNG.data.contentor.document import Document
from dNG.data.http.translatable_error import TranslatableError
from dNG.data.ownable_mixin import OwnableMixin as OwnableInstance
from dNG.data.settings import Settings
from dNG.data.text.input_filter import InputFilter
from dNG.data.text.l10n import L10n
from dNG.data.xhtml.link import Link
from dNG.database.nothing_matched_exception import NothingMatchedException

from .module import Module

class Index(Module):
    """
Service for "m=contentor"

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: contentor
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def execute_index(self):
        """
Action for "index"

:since: v0.2.00
        """

        if (self.request.is_dsd_set("cdid")): self.execute_view()
        elif (self.request.is_dsd_set("ccid") or Settings.is_defined("pas_http_contentor_category_default")): self.execute_list()
    #

    def execute_list(self):
        """
Action for "list"

:since: v0.2.00
        """

        cid = InputFilter.filter_file_path(self.request.get_dsd("ccid", ""))
        page = InputFilter.filter_int(self.request.get_dsd("cpage", 1))

        if (cid == ""): cid = Settings.get("pas_http_contentor_category_default", "")

        L10n.init("pas_http_contentor")
        L10n.init("pas_http_datalinker")

        try: category = Category.load_id(cid)
        except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_contentor_cid_invalid", 404, _exception = handled_exception)

        session = (self.request.get_session() if (self.request.is_supported("session")) else None)
        if (session is not None): category.set_permission_session(session)

        if (not category.is_readable()):
            if (session is None or session.get_user_profile() is None): raise TranslatableError("pas_http_contentor_cid_invalid", 404)
            else: raise TranslatableError("core_access_denied", 403)
        #

        if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

        if (category.is_writable()):
            Link.set_store("servicemenu",
                           (Link.TYPE_RELATIVE_URL | Link.TYPE_JS_REQUIRED),
                           L10n.get("pas_http_contentor_document_new"),
                           { "m": "contentor", "s": "document", "a": "new", "dsd": { "ccid": cid } },
                           icon = "mini-default-option",
                           priority = 3
                          )
        #

        if (category.is_manageable()):
            Link.set_store("servicemenu",
                           (Link.TYPE_RELATIVE_URL | Link.TYPE_JS_REQUIRED),
                           L10n.get("pas_http_contentor_category_manage"),
                           { "m": "contentor", "s": "category", "a": "manage", "dsd": { "ccid": cid } },
                           icon = "mini-default-option",
                           priority = 3
                          )
        #

        category_data = category.get_data_attributes("id", "id_main", "title", "time_sortable", "sub_entries", "entry_type")

        content = { "id": category_data['id'],
                    "title": category_data['title'],
                    "time": category_data['time_sortable'],
                    "sub_entries_count": category_data['sub_entries']
                  }

        if (category_data['sub_entries'] > 0): content['sub_entries'] = { "id": category_data['id'], "page": page }

        category_parent = category.load_parent()

        if (category_parent is not None
            and ((not isinstance(category_parent, OwnableInstance))
                 or category_parent.is_readable_for_session_user(session)
                )
           ):
            category_parent_data = category_parent.get_data_attributes("id", "id_main", "title")

            if (category_parent_data['id'] != cid):
                content['parent'] = { "id": category_parent_data['id'],
                                      "main_id": category_parent_data['id_main'],
                                      "title": category_parent_data['title']
                                    }
            #
        #

        self.response.init(True)
        self.response.set_expires_relative(+15)
        self.response.set_title(category_data['title'])
        self.response.add_oset_content("contentor.{0}_list".format(category_data['entry_type']), content)

        if (self.response.is_supported("html_canonical_url")):
            link_parameters = { "__virtual__": "/contentor/view",
                                "dsd": { "ccid": cid, "cpage": page }
                              }

            self.response.set_html_canonical_url(Link().build_url(Link.TYPE_VIRTUAL_PATH, link_parameters))
        #
    #

    def execute_view(self):
        """
Action for "view"

:since: v0.2.00
        """

        did = InputFilter.filter_file_path(self.request.get_dsd("cdid", ""))

        L10n.init("pas_http_contentor")
        L10n.init("pas_http_datalinker")

        try: document = Document.load_id(did)
        except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_contentor_did_invalid", 404, _exception = handled_exception)

        session = (self.request.get_session() if (self.request.is_supported("session")) else None)
        if (session is not None): document.set_permission_session(session)

        if (not document.is_readable()):
            if (session is None or session.get_user_profile() is None): raise TranslatableError("pas_http_contentor_did_invalid", 404)
            else: raise TranslatableError("core_access_denied", 403)
        #

        if (self.response.is_supported("html_css_files")): self.response.add_theme_css_file("mini_default_sprite.min.css")

        if (document.is_manageable()):
            Link.set_store("servicemenu",
                           (Link.TYPE_RELATIVE_URL | Link.TYPE_JS_REQUIRED),
                           L10n.get("pas_http_contentor_document_edit"),
                           { "m": "contentor", "s": "document", "a": "edit", "dsd": { "cdid": did } },
                           icon = "mini-default-option",
                           priority = 3
                          )
        #

        document_parent = document.load_parent()
        if (document_parent is None and document.is_main_entry()): document_parent = document
        is_category = isinstance(document_parent, Category)

        if (isinstance(document_parent, OwnableInstance)):
            if (not document_parent.is_readable_for_session_user(session)): raise TranslatableError("core_access_denied", 403)

            if (document_parent.is_writable_for_session_user(session)):
                document_parent_id = document_parent.get_id()

                dsd_parameters = ({ "ccid": document_parent_id }
                                  if (is_category) else
                                  { "coid": did }
                                 )

                Link.set_store("servicemenu",
                               (Link.TYPE_RELATIVE_URL | Link.TYPE_JS_REQUIRED),
                               L10n.get("pas_http_contentor_document_new"),
                               { "m": "contentor", "s": "document", "a": "new", "dsd": dsd_parameters },
                               icon = "mini-default-option",
                               priority = 3
                              )
            #

            if (is_category and document_parent.is_manageable_for_session_user(session)):
                Link.set_store("servicemenu",
                               (Link.TYPE_RELATIVE_URL | Link.TYPE_JS_REQUIRED),
                               L10n.get("pas_http_contentor_category_manage"),
                               { "m": "contentor", "s": "category", "a": "manage", "dsd": { "ccid": document_parent_id } },
                               icon = "mini-default-option",
                               priority = 3
                              )
            #
        #

        document_data = document.get_data_attributes("id",
                                                     "id_main",
                                                     "title",
                                                     "time_sortable",
                                                     "sub_entries",
                                                     "sub_entries_type",
                                                     "content",
                                                     "author_id",
                                                     "author_ip",
                                                     "time_published",
                                                     "entry_type",
                                                     "description"
                                                    )

        content = { "id": document_data['id'],
                    "title": document_data['title'],
                    "sub_entries_count": document_data['sub_entries'],
                    "author": { "id": document_data['author_id'], "ip": document_data['author_ip'] },
                    "content": { "content": document_data['content'], "main_id": document_data['id_main'] },
                    "time_published": document_data['time_published']
                  }

        if (document_data['time_published'] != document_data['time_sortable']): content['time_updated'] = document_data['time_sortable']

        document_parent_data = None

        if (document_parent is not None
            and ((not isinstance(document_parent, OwnableInstance))
                 or document_parent.is_readable_for_session_user(session)
                )
           ): document_parent_data = document_parent.get_data_attributes("id", "id_main", "title")

        if (document_data['sub_entries'] > 0 or document_parent_data is not None):
            content['sub_entries'] = { "type": document_data['sub_entries_type'], "id": document_data['id'] }

            if (document_parent_data is not None):
                content['sub_entries']['parent_id'] = document_parent_data['id']
                content['sub_entries']['parent_main_id'] = document_parent_data['id_main']
                content['sub_entries']['parent_title'] = document_parent_data['title']
            #
        #

        self.response.init(True)
        self.response.set_title(document_data['title'])
        self.response.set_expires_relative(+30)
        self.response.set_last_modified(document_data['time_sortable'])
        self.response.add_oset_content("contentor.{0}_document".format(document_data['entry_type']), content)

        if (self.response.is_supported("html_canonical_url")):
            link_parameters = { "__virtual__": "/contentor/view",
                                "dsd": { "cdid": did }
                              }

            self.response.set_html_canonical_url(Link().build_url(Link.TYPE_VIRTUAL_PATH, link_parameters))
        #

        if (self.response.is_supported("html_page_description")
            and document_data['description'] != ""
           ): self.response.set_html_page_description(document_data['description'])
    #
#
