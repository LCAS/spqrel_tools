#!/usr/bin/env python
import web  # http.server
from os import chdir, path
import signal
import time
from json import loads, dumps
from logging import error, warn, info, debug, basicConfig, INFO
from pprint import pformat
from threading import Thread

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

basicConfig(level=INFO)

TEMPLATE_DIR = path.realpath(
    path.join(
        path.dirname(__file__),
        'www'
    )
)


html_config = {
    'websocket_suffix': ':9090',
}

render = web.template.render(TEMPLATE_DIR, base='base', globals=globals())

chdir(TEMPLATE_DIR)


class JsonWSProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        info("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        info("WebSocket connection open.")

    def sendJSON(self, data):
        buf = dumps(data)
        self.sendMessage(buf.encode('utf-8'), False)

    def onMessage(self, payload, isBinary):
        # Debug
        if isBinary:
            warn("Binary message received: {0} bytes".format(len(payload)))
        else:
            info("Text message received: {0}".format(payload.decode('utf8')))
            message_text = payload.decode('utf8')
            payload = loads(message_text)
            debug(pformat(payload))
            self.onJSON(payload)

    #@abstractmethod
    def onJSON(self, payload):
        warn('should not work')

    def onClose(self, wasClean, code, reason):
        info("WebSocket connection closed: {0}".format(reason))


class EchoJSONProtocol(JsonWSProtocol):
    def onJSON(self, payload):
        info('called')
        self.sendJSON(payload)


class WSBackend(object):

    def __init__(self, protocol=EchoJSONProtocol):
        self.protocol = protocol

    def wait_until_shutdown(self, loop):
        self.is_running = True
        info('backend is running')
        while self.is_running:
            try:
                time.sleep(.1)
                yield
            except KeyboardInterrupt:
                info("shutdown")
                break
        loop.stop()

    def stop(self):
        self.is_running = False

    def talker(self):
        factory = WebSocketServerFactory(u"ws://0.0.0.0:8128")
        factory.protocol = self.protocol

        self.loop = asyncio.get_event_loop()
        coro = self.loop.create_server(factory, '0.0.0.0', 8128)
        server = self.loop.run_until_complete(coro)
        asyncio.async(self.wait_until_shutdown(self.loop))

        #signal.signal(signal.SIGINT, self.signal_handler)
        self.loop.run_forever()

        info("Closing...")
        server.close()

        self.loop.run_until_complete(server.wait_closed())
        self.loop.close()






class ControlServer(web.application):
    def __init__(self):
        urls = (
            '/', 'Index',
        )
        web.application.__init__(self, urls, globals())

    def run(self, port=8027, *middleware):
        info('webserver running.')
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))



# def set_ws_protocol():
#     forward =  web.ctx.env.get('HTTP_X_FORWARDED_HOST','')
#     if 'lcas.lincoln.ac.uk' in forward:
#         html_config['rosws_protocol'] = 'wss'
#     else:
#         html_config['rosws_protocol'] = 'ws'
#     info html_config['rosws_protocol']


class Index(object):
    def GET(self):
        return render.index()


class Webserver(Thread):

    def __init__(self, app, port=8127):
        self.app = app
        self.port = port
        super(Webserver, self).__init__()

    def run(self):
        port = 8127
        info("Webserver started.")
        self.app.run(port=port)
        info("Webserver stopped.")

    def stop(self):
        self.app.stop()


def signal_handler(webserver, backend, signum, frame):
    info('shutdown triggered')
    webserver.stop()
    info('webserver shutdown')
    backend.stop()
    info('backend shutdown')


if __name__ == "__main__":

    webserver = Webserver(ControlServer())
    backend = WSBackend(EchoJSONProtocol)
    signal.signal(signal.SIGINT,
                  lambda s, f: signal_handler(webserver, backend, s, f))
    webserver.start()
    backend.talker()

