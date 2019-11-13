import os, json
import tornado.ioloop
import tornado.web

WWW_FOLDER=os.path.join(os.path.dirname(os.path.realpath(__file__)), "www")

class ApiHandler(tornado.web.RequestHandler):
	def initialize(self, core):
		self.core = core

	def set_default_headers(self):
		self.set_header('Content-Type', 'application/json')

	def get(self, method):
		if method == "logs":
			session = self.core.session()
			if session is None:
				self.write(json.dumps({"error": "Session not found."}))
			else:
				self.write(session.logs())
		else:
			self.write(json.dumps({"error": "Method Not Allowed"}))

	def post(self, method):
		if method == "analyze":
			for _, files in self.request.files.items():
				for info in files:
					session = self.core.new(info["filename"], info["body"])
					if session is not None:
						self.write(json.dumps({"error": None}))
					else:
						self.write(message=json.dumps({"error": "Invalid file extension."}))
		else:
			self.write(json.dumps({"error": "Method Not Allowed"}))


def make_app(settings, core):
	handlers = [
		(r"/", tornado.web.RedirectHandler, {"url": "/ui/index.html"}),
		(r"/api/(.*)", ApiHandler, core),
		(r"/ui/(.*)", tornado.web.StaticFileHandler, {'path': WWW_FOLDER})
	]
	return tornado.web.Application(handlers, **settings)

class Server():
	"""Python http server"""
	def __init__(self, core, listen=8080, proto="http"):
		super(Server, self).__init__()
		self.listen  = listen
		self.proto = proto
		self.app = make_app({'debug': True}, dict(core=core))

	def run(self):
		self.app.listen(self.listen)
		print("Server available at {proto}://localhost:{port}".format(proto=self.proto, port=self.listen))
		tornado.ioloop.IOLoop.instance().start()