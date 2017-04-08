# coding: utf-8

#
# Copyright © 2017 weirdgiraffe <giraffe@cyberzoo.xyz>
#
# Distributed under terms of the MIT license.
#
import os
import pytest
import re
import requests
import seasonvar.parser as parser
from seasonvar.requester import Requester
from seasonvar import day_items, season_info, episodes
from datetime import datetime


@pytest.mark.online
def test_parse_main_page_dayblocks():
    req = Requester()
    main_page_html = req.main_page()
    dates = []
    for d, content in parser._main_page_dayblocks(main_page_html):
        dates.append(d)
        assert len(content) > 0
    assert len(dates) > 0


@pytest.mark.online
def test_parse_main_page_items_online():
    date = datetime.today()
    datestr = date.strftime('%d.%m.%Y')
    changes = list(day_items(datestr))
    assert len(changes) > 0
    for c in changes:
        assert 'url' in c
        assert c['url'] != ''
        assert 'name' in c
        assert c['name'] != ''
        assert 'changes' in c
        assert c['changes'] != ''


@pytest.mark.online
def test_parse_episodes_online():
    date = datetime.today()
    datestr = date.strftime('%d.%m.%Y')
    changes = list(day_items(datestr))
    assert len(changes) > 0
    c = changes[0]
    e = list(episodes(c['url']))
    assert len(e) > 0


@pytest.mark.parametrize('term, min_suggestions', [
    ('bone', 1),
    ('привет', 1),
    ('hhhhhhhhhhhhhhhhhhhпривет', 0),
])
def test_pase_latin_search_items_online(term, min_suggestions):
    req = Requester()
    search_response = req.search(term)
    suggestions = list(parser.search_items(search_response))
    assert len(suggestions) >= min_suggestions
    for i in suggestions:
        assert i['url'] is not None


@pytest.mark.skipif(os.getenv('TRAVIS', 'false') == 'true',
                    reason='TRAVIS could not access this CDN')
@pytest.mark.online
def test_play_online_episodes():
    info = season_info('/serial-13945-Horoshee_mesto.html')
    assert info is not None
    assert 'playlist' in info
    assert len(info['playlist']) > 0
    assert 'url' in info['playlist'][0]
    el = list(episodes(info['playlist'][0]['url']))
    assert len(el) > 0
    for e in el:
        assert re.match(r'.*\.(m3u8|mp4)$', e['url'])
        assert len(e['name']) != 0
        res = requests.head(e['url'])
        assert res.status_code == 200