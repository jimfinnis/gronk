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



# special commands are on lines starting with @
# They are:
# @nav x y z    : put links to x, y, z at the top
# @title ..     : set the title string
# @do ..        : execute some python statement in a private namespace to this file;
#                 you can access the variables with the {{..}} pattern.

commandRegex = re.compile(r"^@.*")

class Commands(Preprocessor):
    # this is constructed with a pointer to the extension object,
    # so we can put data in that, and the its creator can get the data out.
    def __init__(self,ext,md):
        self.ext = ext
        super().__init__(md)
        
    def run(self, lines):
        out = []
        for line in lines:
            m = commandRegex.match(line)
            if m:
                x = line[1:] # get the actual command after the @..
                # if there's a space, split into command and argument(s) (a string called 'rest')
                if ' ' in x:
                    try:
                        (cmd,rest) = x.split(' ',1)
                    except ValueError as e:
                        print("String is:",x)
                        raise e
                else:
                    # otherwise that's the whole command and 'rest' will be None
                    cmd = x
                    
                # process the command themselves
                if cmd == 'nav':
                    self.ext.navs=rest.split()
                elif cmd == 'title':
                    self.ext.title = rest
                elif cmd == 'do':
                    exec(rest,self.ext.vars)
                else:
                    raise Exception('unknown special command '+cmd)
            else:
                out.append(line)
        self.ext.navs.insert(0,'index') # that's always there.
        return out


# this will evaluate an expression in {{..}} and return the value
class InlinePattern(Pattern):
    def __init__(self,pat,ext):
        self.ext=ext
        super().__init__(pat)
    def handleMatch(self, m):
        text = m.group(3)
        return str(eval(text,self.ext.vars))
        
class GronkExtensions(Extension):
    def __init__(self,name):
        self.navs=[]
        self.vars={}
        self.title=name
    def extendMarkdown(self,md,globals):
        md.preprocessors.add('commands',Commands(self,md),'_end')
        md.inlinePatterns.add('gronkinline',InlinePattern(INLINE_RE,self),'_end')
