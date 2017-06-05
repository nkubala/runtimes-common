#!/usr/bin/python

# Copyright 2017 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import time
import unittest

from apiclient.discovery import build

import test_util


class TestDebug(unittest.TestCase):

    def __init__(self, url, methodName='runTest'):
        self._url = url + test_util.DEBUG_ENDPOINT
        unittest.TestCase.__init__(self)

    def runTest(self):

        dbg_service = build('clouddebugger', 'v2')
        debugger = dbg_service.debugger()
        debuggees_service = debugger.debuggees()
        debuggees = debuggees_service.list(clientVersion='google.com/python/v2',
                                           includeInactive=False,
                                           project='787876332324',
                                           x__xgafv='2').execute()

        print json.dumps(debuggees, indent=2)

        bp_service = debuggees_service.breakpoints()

        bp_payload = {
            'location': {
                'path': 'server.py',
                'line': 240
            }
        }

        debuggee_list = debuggees.get('debuggees', [])
        for debuggee in debuggee_list:
            dId = debuggee.get('id')
            bp_service.set(debuggeeId=dId,
                           body=bp_payload,
                           clientVersion='google.com/python/v2').execute()

        time.sleep(5)
        output, response_code = test_util.get(self._url)
        self.assertEquals(response_code, 0,
                          'Error encountered inside sample application!')
        time.sleep(5)

        for debuggee in debuggee_list:
            dId = debuggee.get('id')
            active_breakpoints = bp_service.list(debuggeeId=dId,
                                                 stripResults=False,
                                                 includeInactive=False,
                                                 clientVersion='google.com/python/v2',
                                                 x__xgafv='2').execute()

            print json.dumps(active_breakpoints, indent=2)

        # logging.info(output)
