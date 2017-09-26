#!/usr/bin/env python
#
# Copyright 2009, 2012 by Jeffrey M. Laughlin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import io as StringIO
from nose.tools import *
from . import adif
from decimal import Decimal
from datetime import datetime

TEST_ADIF = """
Exported using NA Version 10.57, conforming to ADIF specification 1.0
<adif_ver:4>1.00
<eoh>
<call:5>AB9RN<freq:6>14.150<mode:3>SSB<qso_date:8>20120714<time_on:4>1200
<rst_sent:3>59 <rst_rcvd:3>59 <comment:2>08<eor>
<call:5>K4NNQ<freq:6>14.150<mode:3>SSB<qso_date:8>20120714<time_on:4>1206
<rst_sent:3>59 <rst_rcvd:3>59 <comment:2>08<eor>
<call:6>KC0YSH<freq:6>14.150<mode:3>SSB<qso_date:8>20120714<time_on:4>1206
<rst_sent:3>59 <rst_rcvd:3>59 <comment:2>07<eor>
"""

def test_parse():
    flo = StringIO.StringIO(TEST_ADIF)
    reader = adif.Reader(flo)
    i = reader._lex()
    eq_(next(i), adif.Field(name='call', type='', body='AB9RN'))
    eq_(next(i), adif.Field(name='freq', type='', body='14.150'))
    eq_(next(i), adif.Field(name='mode', type='', body='SSB'))
    eq_(next(i), adif.Field(name='qso_date', type='', body='20120714'))
    eq_(next(i), adif.Field(name='time_on', type='', body='1200'))
    eq_(next(i), adif.Field(name='rst_sent', type='', body='59 '))
    eq_(next(i), adif.Field(name='rst_rcvd', type='', body='59 '))
    eq_(next(i), adif.Field(name='comment', type='', body='08'))
    eq_(next(i), adif.Field(name='eor', type='', body=''))
    eq_(next(i), adif.Field(name='call', type='', body='K4NNQ'))

def test_iter_records():
    flo = StringIO.StringIO(TEST_ADIF)
    reader = adif.Reader(flo)
    i = iter(reader)
    eq_(next(i), {'call': 'AB9RN', 'freq': '14.150', 'mode': 'SSB', 'qso_date': '20120714',
                   'time_on': '1200', 'rst_sent': '59 ', 'rst_rcvd': '59 ',
                   'comment': '08',
                   'app_datetime_on': datetime(2012, 0o7, 14, 12, 0)})

def test_version():
    flo = StringIO.StringIO(TEST_ADIF)
    reader = adif.Reader(flo)
    eq_(reader.adif_ver, Decimal('1.00'))

