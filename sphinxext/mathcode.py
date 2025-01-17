""" Sphinx extension to execute sympy code generating LaTeX

Copied more or less from sphinx/ext/mathbase.py.  That file has license:

    :copyright: Copyright 2007-2015 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from ast import parse, Expr, Expression

from six import exec_

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx.util.compat import Directive
from sphinx.util.nodes import set_source_info
from sphinx.ext.mathbase import displaymath

from sympy import latex

def eval_code(code_str, context):
    mod = parse(code_str, '<string>', 'exec')
    last_line = mod.body.pop() if isinstance(mod.body[-1], Expr) else None
    to_exec = compile(mod, '<string>', 'exec')
    exec_(to_exec, None, context)
    if last_line is None:
        return None
    to_eval = compile(Expression(last_line.value), '<string>', 'eval')
    return eval(to_eval, None, context)


class MathCodeDirective(Directive):

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'label': directives.unchanged,
        'name': directives.unchanged,
        'nowrap': directives.flag,
        'newcontext': directives.flag,
    }

    def get_context(self, newcontext=False):
        if setup.config.mathcode_use_plot_ns:
            import plot_directive
            if newcontext:
                plot_directive.plot_context = dict()
            return plot_directive.plot_context
        if newcontext:
            setup.code_context = dict()
        return setup.code_context

    def run(self):
        context = self.get_context(self.options.get('newcontext', False))
        val = eval_code('\n'.join(self.content), context)
        if val is None:
            return []
        node = displaymath()
        node['latex'] = latex(val)
        node['label'] = self.options.get('name', None)
        if node['label'] is None:
            node['label'] = self.options.get('label', None)
        node['nowrap'] = 'nowrap' in self.options
        node['docname'] = self.state.document.settings.env.docname
        ret = [node]
        set_source_info(self, node)
        if hasattr(self, 'src'):
            node.source = self.src
        if node['label']:
            tnode = nodes.target('', '', ids=['equation-' + node['label']])
            self.state.document.note_explicit_target(tnode)
            ret.insert(0, tnode)
        return ret


def setup(app):
    # Global variables
    setup.app = app
    setup.config = app.config
    setup.confdir = app.confdir
    # Workspace for code run in SympyMath blocks
    setup.code_context = dict()
    app.add_directive('mathcode', MathCodeDirective)
    app.add_config_value('mathcode_use_plot_ns', False, 'env')
