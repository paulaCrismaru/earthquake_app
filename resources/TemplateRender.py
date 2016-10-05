import webapp2
import jinja2
import os

template_dir = os.path.join(os.path.join(os.path.dirname(__file__), "..\\templates"))
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               extensions=['jinja2.ext.autoescape'],
                               autoescape=True)

class TemplateRender(webapp2.RequestHandler):

    def _write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def _render_str(self, template, **params):
        t = JINJA_ENV.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self._write(self._render_str(template, **kw))