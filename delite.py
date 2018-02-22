import cherrypy
import led_engine
from crontab import CronTab
from neopixel import Color
import os
import re
import json
import urllib
import urlparse


def parse_url(url):
    split_url = urlparse.urlsplit(url)
    resource = split_url.path[1:]
    params = dict(urlparse.parse_qsl(split_url.query))
    return resource, params


def create_url(resource, params):
    path = "http://localhost:8080/"
    return path + resource + "?" + urllib.urlencode(params)


@cherrypy.expose
class LedBrightness(object):

    def __init__(self, lamp):
        self.lamp = lamp
        self.brightness = self.GET()

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        return str(self.lamp.getBrightness())

    def POST(self, value):
        self.lamp.setBrightness(int(value))
        self.brightness = int(value)


@cherrypy.expose
class Schedule(object):
 
    def __init__(self):
        self.cron = CronTab(user="pi")

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        self.cron.read()
        jobs_iter = self.cron.find_comment(re.compile(".*delite.*", re.IGNORECASE))
        sched = []
        for job in jobs_iter:
            h, m = job.hour.render(), job.minute.render()
            url = job.command.split("curl -d \"\" -X POST ")[-1]
            _, name = job.comment.split("::")
            command, params = parse_url(url)
            sched.append({"name": name, "command": command, "params": params, "hour": h, "minute": m})
        return json.dumps(sched)

    @cherrypy.tools.accept(media='application/json')
    def POST(self):
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        data = json.loads(rawData)

        self.cron.read()
        job = self.cron.new(command="curl -d \"\" -X POST %s" % create_url(data["command"], data["params"]))
        job.set_comment("delite::%s" % data["name"])
        job.hour.on(data["hour"])
        job.minute.on(data["minute"])
        self.cron.write()

    @cherrypy.tools.accept(media='application/json')
    def PUT(self):
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        data = json.loads(rawData)

        self.cron.read()
        job = list(self.cron.find_comment("delite::" + data["name"]))
        if len(job) == 0:
            raise cherrypy.HTTPError(404, "Unknown job '%s'" % data["name"])
        else:
            job = job[0]
            job.set_command("curl -d \"\" -X POST %s" % create_url(data["command"], data["params"]))
            job.set_comment("delite::%s" % data["name"])
            job.hour.on(data["hour"])
            job.minute.on(data["minute"])
            self.cron.write()

    def DELETE(self):
        pass


class LedServer(object):

    def __init__(self):
        self.lamp = led_engine.LedEngine()
        self.brightness = LedBrightness(self.lamp)
        self.schedule = Schedule()

    @cherrypy.expose
    def index(self):
        return open("frontend.html")

    @cherrypy.expose
    def preset(self, value):
        if value == "on":
            self.lamp.turnOn()
        elif value == "off":
            self.lamp.turnOff()
        elif value == "sunset":
            self.lamp.gradient("red", "darkorange", 0.6)
        elif value == "sunrise":
            self.lamp.gradient("blue", "yellow", 0.6)

    @cherrypy.expose
    def color(self, r, g, b):
        self.lamp.setColor(int(r), int(g), int(b))

    @cherrypy.expose
    def sunrise(self, duration=10):
        self.lamp.sunrise(int(duration))

    @cherrypy.expose
    def sunset(self, duration=10):
        self.lamp.sunset(int(duration))

    @cherrypy.expose
    def gradient(self, color_center="yellow", color_grad="red", ratio=1.0):
        self.lamp.gradient(color_center, color_grad, ratio)

    @cherrypy.expose
    def gradMove(self, color_center="red", color_grad="yellow", iterations=5, wait_ms=10):
        self.lamp.gradMove(color_center, color_grad, int(iterations), int(wait_ms))

    @cherrypy.expose
    def rainbow(self, iterations=5, wait_ms=20):
        self.lamp.rainbowCycle(int(iterations), int(wait_ms))

    @cherrypy.expose
    def wipe(self, r, g, b, wait_ms=50):
        self.lamp.colorWipe(Color(int(r), int(g), int(b)), int(wait_ms))

    @cherrypy.expose
    def glow(self, iterations=5, wait_ms=5):
        self.lamp.glow(int(iterations), int(wait_ms))


if __name__ == "__main__":
    current_dir = os.path.abspath(os.getcwd())

    config = {
        'global': {
            'server.socket_host': '0.0.0.0'
        },
        '/': {
            'tools.staticdir.root': current_dir,
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static',
        },
        '/brightness': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/schedule': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
    }

    cherrypy.quickstart(LedServer(), "/", config)
