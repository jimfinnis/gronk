#
# Just some custom Markdown extension stuff.
#

import re
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree

# {{inline}}
INLINE_RE = r'(\{\{)(.+?)\}\}'

def convnum(n,cmd):
    if cmd.startswith('f'):
        return float(n)
    else:
        return int(n)


# Special commands go in {{...}}

# this will do one of several things to something inside {{..}} brackets.
# {{@nav x y z}}        : put links to x, y, z at the top
# {{@title ..}}         : set the title string
# {{@do ..}}            : execute some python statement in a private namespace to this file;
#                         you can access the variables with the {{..}} pattern.
# In the following, prepending with "f" leaves the result as float, otherwise it's converted
# to int for output.
# {{@[f]postinc var n}} : increment variable by n, return old value
# {{@[f]preinc var n}}  : increment variable by n, return new value
# {{@[f]accum var n}}   : increment variable by n, return n

# {{expr}}              : evaluate and return expression

# {{@usage}}            : return Gronk's options as an inline block

class InlinePattern(Pattern):
    def __init__(self,pat,ext):
        self.ext=ext
        super().__init__(pat)
    def handleMatch(self, m):
        text = m.group(3)
        if text.startswith('@'):
            # handle special commands
            text = text[1:]
            if ' ' in text:
                (cmd,rest) = text.split(' ',1)
            else:
                cmd = text
            if cmd == 'postinc' or cmd =='fpostinc':
                (var,n) = rest.split()
                prev = self.ext.vars[var]
                self.ext.vars[var] += float(n)
                return str(convnum(prev),cmd)
            elif cmd == 'preinc' or cmd =='fpreinc':
                (var,n) = rest.split()
                self.ext.vars[var] += float(n)
                return str(convnum(self.ext.vars[var],cmd))
            elif cmd == 'accum' or cmd == 'faccum':
                (var,n) = rest.split()
                n = float(n)
                self.ext.vars[var] += n
                return str(convnum(n,cmd))
            elif cmd == 'nav':
                self.ext.navs=rest.split()
                return ''
            elif cmd == 'title':
                self.ext.title = rest
                return ''
            elif cmd == 'do':
                exec(rest,self.ext.vars)
                return ''
            elif cmd == 'usage':
                el = etree.Element('pre')
                el.text = GronkExtensions.usage
                return el
            else:
                raise Exception('unknown inline command: @'+cmd)
        else:
            return str(eval(text,self.ext.vars))
        
class GronkExtensions(Extension):
    usage = ''
    def __init__(self,name):
        self.navs=['index']
        self.vars={}
        self.title=name
    def extendMarkdown(self,md,globals):
        md.inlinePatterns.add('gronkinline',InlinePattern(INLINE_RE,self),'_end')
