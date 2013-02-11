# -*- coding: utf-8 -*-
"""
    sphinx.domains.plsql
    ~~~~~~~~~~~~~~~~~~~~

    The PL/SQL domain.

    :copyright: Copyright 2013 by Felipe Zorzo
    :license: BSD, see LICENSE for details.
"""

import re

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from sphinx.util.compat import Directive
from sphinx.util.docfields import Field, GroupedField, TypedField

plsql_sig_re = re.compile(
    r'''^ ([\w.]*\.)?              # package name(s)
          (\$?\w+)  \s*            # method name
          (?: \((.*)\)             # optional: arguments
          (?:\s* return \s* (.*))? # return annotation
          )? $                     # and nothing more
          ''', re.VERBOSE | re.IGNORECASE)

class PlSqlObject(ObjectDescription):
    """
    Description of a general PL/SQL object.
    """
    option_spec = {
        'noindex': directives.flag,
        'module': directives.unchanged,
    }

    doc_field_types = [
        TypedField('parameter', label=l_('Parameters'),
                   names=('param', 'parameter', 'arg', 'argument'),
                   typerolename='obj', typenames=('paramtype', 'type')),
        Field('returnvalue', label=l_('Returns'), has_arg=False,
              names=('returns', 'return')),
        Field('returntype', label=l_('Return type'), has_arg=False,
              names=('rtype', 'returntype')),
    ]

    def handle_signature(self, sig, signode):
        m = plsql_sig_re.match(sig)
        if m is None:
            raise ValueError
            
        name_prefix, name, arglist, retann = m.groups()
    
        if not name_prefix:
            name_prefix = ""
        
        sig_prefix = self.get_signature_prefix(sig)
        
        if sig_prefix:
            signode += addnodes.desc_annotation(sig_prefix, sig_prefix)
     
        signode += addnodes.desc_name(name, name)
        return name, name_prefix

class PlSqlPackage(PlSqlObject):
    """
    Description of a package object.
    """

    def get_signature_prefix(self, sig):
        return self.objtype + ' '

class PlSqlDomain(Domain):
    """PL/SQL language domain."""
    name = 'plsql'
    label = 'PL/SQL'
    object_types = {
        'package': ObjType(l_('package'), 'package', 'obj')
    }

    directives = {
        'package': PlSqlPackage,
    }


def setup(app):
    app.add_domain(PlSqlDomain)
