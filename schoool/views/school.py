# -*- coding: utf-8 -*-

from datetime import date

from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
import requests

from schoool.renderers import render_json


view = Blueprint('auth', __name__)


@view.route('/school/search')
def search():
    query = request.values.get('query')
    if not query:
        raise BadRequest('The required parameter "query" is missing.')

    url = 'http://hes.sen.go.kr/spr_ccm_cm01_100.do'
    params = {
        'kraOrgNm': query,
    }
    json = requests.get(url, params=params).json
    dirty = json.get('resultSVO').get('orgDVOList')
    data = [{
        'code': data['orgCode'],
        'name': data['kraOrgNm'],
        'address': data['zipAdres'],
        'type': data['schulCrseScCodeNm'],
    } for data in dirty]
    return render_json(data)


@view.route('/school/<code>/meals')
def meals(code):
    year = request.values.get('year', date.today().year, type=int)
    month = request.values.get('month', date.today().month, type=int)

    url = 'http://hes.sen.go.kr/sts_sci_md00_001.do'
    data = {
        'schulCode': code,
        'schulCrseScCode': 4,
        'ay': year,
        'mm': month,
    }

    html = requests.get(url, data=data).html
    tds = [list(td.stripped_strings) for td in html.find_all('td')]
    tds = filter(None, tds)

    meals = []

    for items in tds:
        meal = {
            'date': '{}-{}-{:02d}'.format(year, month, int(items[0])),
            'lunch': [],
            'dinner': [],
        }

        try:
            dinner_index = items.index(u'[석식]')
        except ValueError:
            dinner_index = len(items) - 1

        meal['lunch'] = items[2:dinner_index]
        meal['dinner'] = items[dinner_index + 1:]
        meals.append(meal)

    return render_json(meals)
