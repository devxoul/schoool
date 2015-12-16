# -*- coding: utf-8 -*-

from datetime import date

from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
import requests

from schoool.renderers import render_json


URLS = [
    'hes.sen.go.kr',  # 서울
    'hes.pen.go.kr',  # 부산
    'hes.dge.go.kr',  # 대구
    'hes.ice.go.kr',  # 인천
    'hes.gen.go.kr',  # 광주
    'hes.dje.go.kr',  # 대전
    'hes.use.go.kr',  # 울산
    'hes.sje.go.kr',  # 세종
    'hes.goe.go.kr',  # 경기
    'hes.kwe.go.kr',  # 강원
    'hes.cbe.go.kr',  # 충북
    'hes.cne.go.kr',  # 충남
    'hes.jbe.go.kr',  # 전북
    'hes.jne.go.kr',  # 전남
    'hes.gbe.kr',     # 경북
    'hes.gne.go.kr',  # 경남
    'hes.jje.go.kr',  # 제주
]


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
