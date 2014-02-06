# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.database.instances.ContentorCategory
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

from sqlalchemy import BOOLEAN, CHAR, Column, ForeignKey, VARCHAR

from .data_linker import DataLinker
from .ownable_mixin import OwnableMixin

class ContentorCategory(DataLinker, OwnableMixin):
#
	"""
"ContentorCategory" represents a contentor entry.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: contentor
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;gpl
             GNU General Public License 2
	"""

	__tablename__ = "{0}_contentor_category".format(DataLinker.get_table_prefix())
	"""
SQLAlchemy table name
	"""
	db_instance_class = "dNG.pas.data.contentor.Category"
	"""
Encapsulating SQLAlchemy database instance class name
	"""

	id = Column(VARCHAR(32), ForeignKey(DataLinker.id_object), primary_key = True)
	"""
contentor_category.id
	"""
	owner_type = Column(CHAR(1), server_default = "u", nullable = False)
	"""
contentor_category.owner_type
	"""
	entry_type = Column(VARCHAR(255), server_default = "simple", nullable = False)
	"""
contentor_category.entry_type
	"""
	locked = Column(BOOLEAN, server_default = "0", nullable = False)
	"""
contentor_category.locked
	"""
	public_permission = Column(CHAR(1), server_default = "", nullable = False)
	"""
contentor_category.public_permission
	"""

	__mapper_args__ = { "polymorphic_identity": "ContentorCategory" }
	"""
sqlalchemy.org: Other options are passed to mapper() using the
                __mapper_args__ class variable.
	"""
#

##j## EOF