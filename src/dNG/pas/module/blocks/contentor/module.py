# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.module.blocks.contentor.Module
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;http;contentor

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasHttpContentorVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from dNG.pas.data.settings import Settings
from dNG.pas.data.translatable_exception import TranslatableException
from dNG.pas.database.connection import Connection
from dNG.pas.module.blocks.abstract_block import AbstractBlock

class Module(AbstractBlock):
#
	"""
Module for "contentor"

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: contentor
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self):
	#
		"""
Constructor __init__(Module)

:since: v0.1.00
		"""

		AbstractBlock.__init__(self)

		self.database = None
		"""
Database instance
		"""

		Settings.read_file("{0}/settings/pas_contentor.json".format(Settings.get("path_data")))
	#

	def execute(self):
	#
		"""
Execute the requested action.

:since: v0.1.00
		"""

		try: database = Connection.get_instance()
		except Exception as handled_exception:
		#
			if (self.log_handler != None): self.log_handler.error(handled_exception)
			raise TranslatableException("core_database_error", _exception = handled_exception)
		#

		with database: return AbstractBlock.execute(self)
	#
#

##j## EOF