import inspect

from django import template
from django.template.base import TokenType

register = template.Library()


@register.filter
def view_instance_code(instance):
    return inspect.getsource(instance.__class__).strip()


@register.tag
def code(parser, token):
    # making the node verbatim
    parameters = token.split_contents()
    lang = parameters[1]
    try:
        verbatim = parameters[2] == 'True'
    except IndexError:
        verbatim = True
    if verbatim:
        for token in parser.tokens:
            contents = token.contents
            if token.token_type == TokenType.BLOCK:
                if contents.split()[0] == 'endcode':
                    break
            if contents.strip():
                if token.token_type == TokenType.BLOCK:
                    token.contents = '{% ' + contents + ' %}'
                elif token.token_type == TokenType.VAR:
                    token.contents = '{{ ' + contents + ' }}'
                token.token_type = TokenType.TEXT
    nodelist = parser.parse(('endcode',))
    parser.delete_first_token()
    return CodeNode(nodelist, lang=lang, verbatim=verbatim)


class CodeNode(template.Node):
    def __init__(self, nodelist, lang, verbatim):
        self.nodelist = nodelist
        self.lang = lang
        self.verbatim = verbatim

    def render(self, context):
        contents = self.nodelist.render(context).replace('\n', '', 1)
        if self.verbatim:
            contents = remove_indentation(contents)
        inner_template = template.Template(
            '{% load pygmentify %}'
            '{% pygment %}{% verbatim %}'
            f'<pre lang={self.lang}>{contents}</pre>'
            '{% endverbatim %}{% endpygment %}'
        )
        return inner_template.render(context)


def guess_indentation(contents):
    indentation = ''
    lines = contents.split('\n')
    benchmark_line = lines[0]
    if benchmark_line:
        length = len(benchmark_line) - len(benchmark_line.lstrip())
        indentation = benchmark_line[:length]
    return indentation


def remove_indentation(contents):
    indent = guess_indentation(contents)
    lines = [line.replace(indent, '', 1) for line in contents.split('\n')]
    return '\n'.join(lines)
