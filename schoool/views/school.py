# -*- coding: utf-8 -*-

from datetime import date
import json

from werkzeug.exceptions import BadRequest
from flask import Blueprint, request
import requests

from schoool import cache
from schoool.renderers import render_json


URLS = [
    'stu.sen.go.kr',  # 서울
    'stu.pen.go.kr',  # 부산
    'stu.dge.go.kr',  # 대구
    'stu.ice.go.kr',  # 인천
    'stu.gen.go.kr',  # 광주
    'stu.dje.go.kr',  # 대전
    'stu.use.go.kr',  # 울산
    'stu.sje.go.kr',  # 세종
    'stu.goe.go.kr',  # 경기
    'stu.kwe.go.kr',  # 강원
    'stu.cbe.go.kr',  # 충북
    'stu.cne.go.kr',  # 충남
    'stu.jbe.go.kr',  # 전북
    'stu.jne.go.kr',  # 전남
    'stu.gbe.kr',     # 경북
    'stu.gne.go.kr',  # 경남
    'stu.jje.go.kr',  # 제주
]


view = Blueprint('auth', __name__)


@view.route('/school/search')
def search():
    query = request.values.get('query')
    if not query:
        raise BadRequest('The required parameter "query" is missing.')

    cache_key = 'school-search:' + query
    cached_data = cache.get(cache_key)
    if cached_data:
        return render_json(json.loads(cached_data))

    url = 'http://m.schoolinfo.go.kr/disclosure/school/result'
    params = {
        'hgNmEncUri': query,
    }
    html = requests.get(url, params=params).html
    data = []
    for panel in html.find_all(class_='panel'):
        type_ = panel.find(class_='panel-title').find('button').text
        for item in panel.find_all(class_='list-group-item'):
            name = item.contents[1].strip()
            code = item['href'].split('/')[-1]
            data.append({
                'name': name,
                'type': type_,
                'code': code,
            })

    cache.set(cache_key, json.dumps(data))
    return render_json(data)


@view.route('/school/<code>/meals')
def meals(code):
    year = request.values.get('year', date.today().year, type=int)
    month = request.values.get('month', date.today().month, type=int)

    cache_key = 'school-meals:{}:{}-{}'.format(code, year, month)
    cached_data = cache.get(cache_key)
    if cached_data:
        return render_json(json.loads(cached_data))

    if code[0] == 'A':
        host_cache_key = 'school-host:{}'.format(code)
        host = cache.get(host_cache_key)
        if not host:
            url = 'http://m.schoolinfo.go.kr/disclosure/gongsi/infoDefault/{}'\
                .format(code)
            html = requests.get(url).html
            address = html.find('td', string='주소')\
                          .find_next_sibling('td')\
                          .string
            cities = [u'서울', u'부산', u'대구', u'인천', u'광주', u'대전', u'울산',
                      u'세종', u'경기', u'강원', u'충청북도', u'충청남도', u'전라북도',
                      u'전라남도', u'경상북도', u'경상남도', u'제주']
            for i, city in enumerate(cities):
                if address.startswith(city):
                    host = URLS[i]
                    cache.set(host_cache_key, host)
                    break
    else:
        index = ord(code[0]) - 66
        host = URLS[index]

    url = 'http://{}/sts_sci_md00_001.do'.format(host)
    data = {
        'schulCode': code,
        'schulCrseScCode': 4,
        'ay': year,
        'mm': '{:02d}'.format(month),
    }

    meals = []

    html = requests.get(url, data=data).html
    if u'자료가 없습니다.' not in html.decode('utf-8'):
        tds = [list(td.stripped_strings) for td in html.find_all('td')]
        tds = filter(None, tds)

        for items in tds:
            meal = {
                'date': '{}-{:02d}-{:02d}'.format(year, month, int(items[0])),
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

    cache.set(cache_key, json.dumps(meals))
    return render_json(meals)
