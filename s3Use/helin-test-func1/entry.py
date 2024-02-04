#!/usr/bin/env python
import logging
import os
import sys

from flask import Flask, request, abort, g
from gevent.pywsgi import WSGIServer


class FuncApp(Flask):
    def __init__(self, name, loglevel=logging.DEBUG):
        super(FuncApp, self).__init__(name)
        # init the class members
        self.root = logging.getLogger()
        self.ch = logging.StreamHandler(sys.stdout)

        self.root.setLevel(loglevel)
        self.ch.setLevel(loglevel)
        self.ch.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(self.ch)


        @self.route('/healthz', methods=['GET'])
        def healthz():
            return "", 200

        @self.route('/', methods=['GET', 'POST', 'PUT', 'HEAD', 'OPTIONS', 'DELETE'])
        def funcEntry():
            return "hello world"

app = FuncApp(__name__, logging.DEBUG)
app.logger.info("Starting gevent based server")
svc = WSGIServer(('0.0.0.0', 8080), app)
svc.serve_forever()

