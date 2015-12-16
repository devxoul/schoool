# -*- coding: utf-8 -*-

import json

from flask import Response


def render_json(data=None):
    if data is None:
        return Response('{}', mimetype='application/json')
    if isinstance(data, list):
        data = dict(data=data)
    return Response(json.dumps(data), mimetype='application/json')
