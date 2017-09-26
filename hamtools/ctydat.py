#!/usr/bin/env python
"""
cty.dat file reader and lookup

Copyright 2014 by Jeffrey M. Laughlin
Copyright (C) 2005-2009 Fabian Kurz, DJ1YFK

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Ported from yfklog

Alpha quality, largely untested; please help!
"""

from collections import defaultdict
import re

import pdb


class InvalidDxcc(Exception):
    pass


class CtyDat(object):
    fields = ['name', 'cq', 'itu', 'cont', 'lat', 'lon', 'utcoff', 'prefix']

    def __init__(self, infile):
        self.prefixes = defaultdict(list)
        self.dxcc = {}
        for line in infile:
            if line[0] != ' ':
                # DXCC line
                line=line.strip()
                fields = [f.strip() for f in line.split(':')]
                dxcc = dict(list(zip(self.fields, fields)))
                mainprefix = dxcc['prefix']
                self.dxcc[mainprefix] = dxcc
            else:
                line=line.strip()
                line = line.rstrip(';')
                line = line.rstrip(',')
                prefixes = line.split(',')
                self.prefixes[mainprefix].extend(prefixes)

    def getwpx(self, call):
        prefix = None
        a,b,c = None, None, None
        fields = call.split('/')
        try: a,b,c = fields
        except Exception:
            try: a,b = fields
            except Exception:
                a = fields

        if c is None and None not in (a,b):
            if b in ('QRP', 'LGT'):
                b = a
                a = None

        if b.isdigit():
            raise Exception("invalid callsign %s" % call)

        if a is None and c is None:
            if re.search('\d', b) is not None:
                prefix = re.search('(.+\d)[A-Z]*', b).group(0)
            else:
                prefix = b[0:2] + '0'
        elif a is None and c is not None:
            if len(c) == 1 and c.isdigit():
                _1 = re.search('(.+\d)[A-Z]*', b).group(0)
                mo = re.search('^([A-Z]\d)\d$', _1)
                if mo is not None:
                    prefix = _1 + c
                else:
                    mo = re.search('(.*[A-Z])\d+', _1)
                    prefix = mo.group(0) + c
            elif re.search('(^P$)|(^M{1,2}$)|(^AM$)|(^A$)', c) is not None:
                mo = re.search('(.+\d)[A-Z]*', b)
                prefix = mo.group(0)
            elif re.search('^\d\d+$/', c) is not None:
                mo = re.search('(.+\d)[A-Z]*', b)
                prefix = mo.group(0)
            else:
                if c[-1].isdigit():
                    prefix = c
                else:
                    prefix = c + '0'
        elif a is not None:
            if a[-1].isdigit():
                prefix = a
            else:
                prefix = a + '0'
        return prefix

    def __extract_call(self,test):
        """
        Pulls out only the call sign from a cty.dat exception entry.
        """

        if test[0] != '=':
            call = None # Return None if a prefix entry.

        else:
            # Strip off the = and force upper case.
            call = test[1:].upper()

            # Remove zone information if present.
            if '(' in call or '[' in call:
                mo      = re.search('^([A-Z0-9\/]+)([\[\(].+)', call)
                call    = mo.group(1)

        return call


    def getdxcc(self, call):
        matchchars  = 0
        goodzone    = None
        matchprefix = None

        perfect_match   = False
        cty_entry       = ''
        for mainprefix, tests in self.prefixes.items():
            if perfect_match: break
            for test in tests:
                if perfect_match: break

                # First check if there is an exact match of the callsign
                # in the cty.dat database.
                if call.upper() == self.__extract_call(test):
                    cty_entry       = test[1:]
                    matchprefix     = mainprefix
                    perfect_match   = True

                # If no exact callsign match, then find the best prefix match.
                elif call[0].upper() == test[0].upper():
                    testlen = len(test) # Look for the longest prefix that matches
                    if call[:testlen] == test[:testlen] and matchchars <= testlen:
                        matchchars  = testlen
                        cty_entry   = test
                        matchprefix = mainprefix


        try:
            mydxcc = self.dxcc[matchprefix]
        except KeyError:
            raise InvalidDxcc(matchprefix)

        # CQ Zones in (), ITU Zones in []
        cty_entry_zones = None
        if '(' in cty_entry or '[' in cty_entry:
            mo = re.search('^([A-Z0-9\/]+)([\[\(].+)', cty_entry)
            cty_entry_zones = mo.group(0)
                
        if cty_entry_zones is not None:
            mo = re.search('\((\d+)\)', cty_entry_zones)
            if mo is not None:
                mydxcc['cq'] = mo.group(0)[1:-1]
            mo = re.search('\[(\d+)\]', cty_entry_zones)
            if mo is not None:
                mydxcc['itu'] = mo.group(0)[1:-1]

        # Convert to strings to numbers
        # Floats
        keys = ['utcoff', 'lat', 'lon']
        for key in keys:
            mydxcc[key] = float(mydxcc[key])

        # Ints
        keys = ['cq', 'itu']
        for key in keys:
            mydxcc[key] = int(mydxcc[key])

        if mydxcc['prefix'].startswith('*'):
            if (mydxcc['prefix'] == '*TA1'):  mydxcc['prefix'] = "TA"  # Turkey
            if (mydxcc['prefix'] == '*4U1V'): mydxcc['prefix'] = "OE"  # 4U1VIC is in OE..
            if (mydxcc['prefix'] == '*GM/s'): mydxcc['prefix'] = "GM"  # Shetlands
            if (mydxcc['prefix'] == '*IG10'):  mydxcc['prefix'] = "I"  # African Italy
            if (mydxcc['prefix'] == '*IT9'):  mydxcc['prefix'] = "I"  # Sicily
            if (mydxcc['prefix'] == '*JW/b'): mydxcc['prefix'] = "JW"  # Bear Island

        return mydxcc

