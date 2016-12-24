# -*- coding: utf-8 -*-

import json
import os

from bs4 import BeautifulSoup
from flask import Flask, request, Response
import requests
from werkzeug.exceptions import default_exceptions

from schoool import cache
from schoool.views import blueprints


def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.from_pyfile(os.path.abspath(config))
    else:
        app.config.from_envvar('CONFIG')

    install_errorhandler(app)
    register_blueprints(app)

    cache.init_app(app)

    monkey_patch_response_html()
    monkey_patch_response_json()

    return app


def register_blueprints(app):
    for blueprint_name in blueprints:
        path = 'schoool.views.%s' % blueprint_name
        view = __import__(path, fromlist=[blueprint_name])
        blueprint = getattr(view, 'view')
        app.register_blueprint(blueprint)


def install_errorhandler(app):
    def errorhandler(err):
        accept = request.headers.get('Accept', '')

        if 'application/json' in accept:
            data = {
                'status': err.code,
                'name': err.name,
                'description': err.description
            }
            res = json.dumps(data)
            return Response(res, mimetype='application/json', status=err.code)

        html = "<h1>{0}: {1}</h1><p>{2}</p>".format(err.code, err.name,
                                                    err.description)
        return Response(html, status=err.code)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = errorhandler


def monkey_patch_response_html():
    @property
    def _html(self):
        return BeautifulSoup(self.text, 'html.parser')
    requests.Response.html = _html


def monkey_patch_response_json():
    @property
    def _json(self):
        return json.loads(self.text)
    requests.Response.json = _json
