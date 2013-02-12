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
          (?: (?:\((.*)\))?        # optional: arguments
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
            name_prefix = ''

        if self.env.temp_data.get('plsql:in_package'):
            name_prefix = self.env.temp_data['plsql:current_package'] + '.'
        
        sig_prefix = self.get_signature_prefix(sig)
        if sig_prefix:
            signode += addnodes.desc_annotation(sig_prefix, sig_prefix)

        fullname = ''
        if name_prefix:
            fullname += name_prefix

        fullname += name

        signode += addnodes.desc_name(name, name)
        
        if arglist:
            signode += addnodes.desc_parameterlist()
            stack = [signode[-1]]
            
            for token in arglist.split(','):
                if not token or token == ',' or token.isspace():
                    pass
                else:
                    token = token.strip()
                    stack[-1] += addnodes.desc_parameter(token, token)
            
        if retann:
            signode += addnodes.desc_returns(retann, retann)
            
        return fullname

    def get_index_text(self, name):
        return _('%s (PL/SQL %s)') % (name, self.objtype)
            
    def add_target_and_index(self, name, sig, signode):
        if name not in self.state.document.ids:
            signode['names'].append(name)
            signode['ids'].append(name)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            inv = self.env.domaindata['plsql']['objects']
            if name in inv:
                self.state_machine.reporter.warning(
                    'duplicate object description of %s, ' % name +
                    'other instance in ' + self.env.doc2path(inv[name][0]),
                    line=self.lineno)
            inv[name] = (self.env.docname, self.objtype)

        indextext = self.get_index_text(name)
        if indextext:
            self.indexnode['entries'].append(('single', indextext, name, ''))

class PlSqlPackage(PlSqlObject):
    """
    Description of a package object.
    """

    def get_signature_prefix(self, sig):
        return self.objtype + ' '

    def before_content(self):
        self.env.temp_data['plsql:in_package'] = True
        if self.names:
            self.env.temp_data['plsql:current_package'] = self.names[0]
    
    def after_content(self):
        self.env.temp_data['plsql:in_package'] = False

class PlSqlMethod(PlSqlObject):
    """
    Description of a package member.
    """
    
    def get_signature_prefix(self, sig):
        return self.objtype + ' '

class PlSqlXRefRole(XRefRole):
    """
    Description of a generic xref role.
    """

    def process_link(self, env, refnode, has_explicit_title, title, target):
        return title, target
        
class PlSqlDomain(Domain):
    """PL/SQL language domain."""
    name = 'plsql'
    label = 'PL/SQL'
    object_types = {
        'package': ObjType(l_('package'), 'pkg', 'obj'),
        'procedure': ObjType(l_('procedure'), 'proc', 'obj'),
        'function': ObjType(l_('function'), 'func', 'obj'),
    }

    directives = {
        'package': PlSqlPackage,
        'procedure': PlSqlMethod,
        'function': PlSqlMethod,
    }
    
    roles = {
        'pkg': PlSqlXRefRole(),
        'proc': PlSqlXRefRole(),
        'func': PlSqlXRefRole(),
    }
    
    initial_data = {
        'objects': {},  # fullname -> docname, objtype
    }

    def clear_doc(self, docname):
        for fullname, (fn, _) in self.data['objects'].items():
            if fn == docname:
                del self.data['objects'][fullname]

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        if target not in self.data['objects']:
            return None
        obj = self.data['objects'][target]
        return make_refnode(builder, fromdocname, obj[0], target,
                            contnode, target)

    def get_objects(self):
        for refname, (docname, type) in self.data['objects'].iteritems():
            yield (refname, refname, type, docname, refname, 1)

def setup(app):
    app.add_domain(PlSqlDomain)
