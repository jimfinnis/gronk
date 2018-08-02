import tornado.httpserver
import tornado.ioloop
import tornado.web
import ssl
import os
import logging
import codecs,markdown
import gronk

from tornado.web import URLSpec as URL
from concurrent.futures import ThreadPoolExecutor
from pkg_resources import resource_filename

from markdown.extensions import wikilinks

datapath=None

class RootWebHandler(tornado.web.RequestHandler):
    def get_template_namespace(self):
        ns = super(RootWebHandler, self).get_template_namespace()
        ns.update({
            'gronk': gronk.info
        })
        return ns

# used for rendering most templates (except the 404)
class WebHandler(RootWebHandler):
    executor = ThreadPoolExecutor(max_workers=os.cpu_count()) 
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.logger=logging.getLogger(__name__)
        
    @tornado.gen.coroutine        
    def get(self,*args):
        io = tornado.ioloop.IOLoop.current()
        xml = yield io.run_in_executor(WebHandler.executor,
            lambda: self._get(self.request,*args))
        if xml is not None:
            self.write(xml)
        self.finish()


class NotFoundHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.set_status(404)
        return self.render('404.html')

class MainHandler(WebHandler):
    def _get(self,request,name):
        self.set_header('Cache-control','no-cache, no-store, must-revalidate')
        if name.endswith('/'):
            name = name[:-1]
        file = os.path.join(datapath,name)+'.md'
        if os.path.exists(file):
            text = codecs.open(file, mode="r", encoding="utf-8").read()
            html = markdown.markdown(text,extensions=[wikilinks.WikiLinkExtension()])
            return self.render_string('main.html',
                name=name,
                content=html)
        else:
            return self.render_string('404.html',name=name)
        


class TornadoServer:
    def __init__(self,dp,webport):
        self.templatepath = resource_filename(__name__,'templates')
        global datapath
        datapath = dp
        self.webport=webport
        self.running=False
        self.logger = logging.getLogger(__name__)
        
    def __enter__(self):
        return self
    def __exit__(self,et,ev,tb):
        pass

    def createwebserver(self,compiledTemplateCache):
        staticroot = resource_filename(__name__,'static')
        print(staticroot)
        app = tornado.web.Application([
            # favicon fetch
            URL(r".*/(favicon\.ico)",tornado.web.StaticFileHandler,
                kwargs={'path':staticroot}),

            #where static files live
            URL(r"/static/(.*)",tornado.web.StaticFileHandler,
                kwargs={'path':staticroot}),
            # everything else
            URL(r"/(.*)",MainHandler)
        ],template_path=self.templatepath,
            compiled_template_cache=compiledTemplateCache,
            default_handler_class=NotFoundHandler,
            )

        webserv = tornado.httpserver.HTTPServer(app)
        print("Web listening on %d" % self.webport)
        webserv.listen(self.webport)

    def run(self,cached):
        self.createwebserver(cached)
        self.running=True
        tornado.ioloop.IOLoop.instance().start()



def main(args=None):
    with TornadoServer('.',8000) as s:
        s.run(False)
    
    
