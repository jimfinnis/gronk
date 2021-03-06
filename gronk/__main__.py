import tornado.httpserver
import tornado.ioloop
import tornado.web
import ssl
import os
import logging
from optparse import OptionParser
import codecs,markdown
import gronk

from tornado.web import URLSpec as URL
from concurrent.futures import ThreadPoolExecutor
from pkg_resources import resource_filename

# so that we can get links like [[this]]
from markdown.extensions import wikilinks
from gronk.extensions import GronkExtensions

# this is the path the data files are read from. It's '.' by default.
datapath=None

# massage the directory name so it works in links - we form a link in a subdir
# by using {{d}}{{name}}.
def getdirprefix(d):
    if d=='.' or d=='/':
        return ''
    else:
         return d+'/'

# All web request handlers are derived from this - it adds 'gronk'
# to the namespace, withe the info structure set up in __init__.py.
# This means we can use things like {{gronk.version}} in templates.

class RootWebHandler(tornado.web.RequestHandler):
    def get_template_namespace(self):
        ns = super(RootWebHandler, self).get_template_namespace()
        ns.update({
            'gronk': gronk.info
        })
        return ns

# used for rendering most templates (except the 404), this will spin
# off a new coroutine for each request.

class WebHandler(RootWebHandler):
    # create an executor for the entire class
    executor = ThreadPoolExecutor(max_workers=os.cpu_count()) 

    # just adds a logger object    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.logger=logging.getLogger(__name__)
        
    # this is called in response to GET requests. It in turn
    # calls _get() in the subclasses inside a separate thread,
    # writes the result and finishes the response.
    
    @tornado.gen.coroutine        
    def get(self,*args):
        io = tornado.ioloop.IOLoop.current()
        xml = yield io.run_in_executor(WebHandler.executor,
            lambda: self._get(self.request,*args))
        if xml is not None:
            self.write(xml)
        self.finish()

# 404 handler is a special case - we just return the 404 template
# result in response to all requests

class NotFoundHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.set_status(404)
        print("THIS RENDERER")
        return self.render('404.html',d=getdirprefix('.'))

# this adds to WebHandler the facility for processing markdown, serving
# files given a directory and a name.

class MarkdownHandler(WebHandler):
    def servefile(self,dir,name):
        self.logger.critical('looking for '+name+' in '+dir)
        # No caching
        self.set_header('Cache-control','no-cache, no-store, must-revalidate')
        # if the name ends with a slash remove it
        if name.endswith('/'):
            name = name[:-1]
        # make the filename by appending .md, the markdown suffix
        mdname = name+'.md'
        # try to find it in the datapath and subdir.
        file = os.path.join(datapath,dir,mdname)
        if os.path.exists(file):
            # found it, so this isn't a default page
            isdefault=False
        else:
            # can't find it in the current dir - is it in the default pages?
            file = os.path.join(resource_filename(__name__,'defaults'),mdname)
            isdefault=True
            if not os.path.exists(file):
                # oops.
                self.logger.critical("cannot find file: "+file)
                return self.render_string('404.html',name=name,d=getdirprefix(dir))
        # we have the file, load it.
        text = codecs.open(file, mode="r", encoding="utf-8").read()
        
        # process the markdown with some extensions. Our own extension will
        # store some data created during processing, so keep a reference to it.
        # Note that we change directory so any links should come out
        # right..
        ext = GronkExtensions(name)
        html = markdown.markdown(text,extensions=
            [wikilinks.WikiLinkExtension(end_url=''),ext])

        self.logger.info("************************** NODE SERVED: "+name)

        # now process and return the template, passing in the name,
        # whether it's a default, the navs and title built from the extension,
        # and the raw html which came from the markdown. These will
        # visible to the template.

        return self.render_string('main.html',
            name=name,
            isdefault=isdefault,
            navs=ext.navs,
            d=getdirprefix(dir),
            title=ext.title,
            content=html)
    

# our main handler, derived from WebHandler (as all proper handlers should be)
# via WebHandler.
# It defines _get(), which takes the additional 'name' argument - the first
# group captured in the URL defined by the application. The get() method
# of the WebHandler class will call this.

class MainHandler(MarkdownHandler):
    def _get(self,request,name):
        return self.servefile('.',name)
        
class SubDirHandler(MarkdownHandler):
    def _get(self,request,dir,name):
        return self.servefile(dir,name)
        

# this encapsulates the tornado server details.
class TornadoServer:
    def __init__(self,dp='.',webport=8000):
        # grab a logger
        self.logger = logging.getLogger(__name__)
        # templates must be loaded from the 'templates' directory
        self.templatepath = resource_filename(__name__,'templates')
        # set the data path, (. by default)
        global datapath
        datapath = dp
        # set the web port (8000 by default)
        self.webport=webport
        self.running=False
        
    # this makes the web server application itself
    def createwebserver(self,cached):
        # this is where our static files live (css, js etc.)
        staticroot = resource_filename(__name__,'static')
        # create our web application with a list of URLSpec
        # objects (we imported URLSpec as URL above). These
        # are regexes which are checked in order, so put less specific
        # ones at the end.
        app = tornado.web.Application([
            # favicon fetch will just return a static file
            URL(r".*/(favicon\.ico)",tornado.web.StaticFileHandler,
                kwargs={'path':staticroot}),

            # looking for anything in /static/ will also return
            # that file
            URL(r"/static/(.*)",tornado.web.StaticFileHandler,
                kwargs={'path':staticroot}),
            # subdirectories each have their own set of files
            URL(r"/(.*)/(.*)",SubDirHandler),
            # everything else goes to the main handler for the current directory
            URL(r"/(.*)",MainHandler)
            ],
            # template locations
            template_path=self.templatepath,
            # whether we cache compiled templates or not
            compiled_template_cache=cached,
            # and what to do if we don't get a match in the list above
            # (return a 404)
            default_handler_class=NotFoundHandler,
            )

        # create the webserver
        webserv = tornado.httpserver.HTTPServer(app)
        print("Web listening on %d" % self.webport)
        # and set it listening on the port provided
        webserv.listen(self.webport)

    # this actually runs the server
    def run(self,cached):
        # create the server
        self.createwebserver(cached)
        # and start the main loop
        tornado.ioloop.IOLoop.instance().start()



def main():
    parser = OptionParser()
    parser.add_option('-p','--port',dest='port',help='set port to PORT',metavar='PORT',
        type='int',default=8000)
    parser.add_option('','--log',dest='loglevel',default='INFO',
        help='set logging level (debug/info/warning/error/critical)')
    
    (options,args)=parser.parse_args()
    
    GronkExtensions.usage = parser.format_help() # for the {{@usage} tag
    numeric_loglevel = getattr(logging, options.loglevel.upper(), None)
    if not isinstance(numeric_loglevel, int):
        raise ValueError('Invalid log level: %s' % options.loglevel)

    # this is an ugly hack
    logger = logging.getLogger("gronk")
    logger.setLevel(numeric_loglevel)

    print('Setting log level to %s [%s]' % (options.loglevel.upper(),numeric_loglevel))    
    import sys
    TornadoServer(webport=options.port).run(False)
    
    
