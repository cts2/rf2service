# -*- coding: utf-8 -*-
# Copyright (c) 2013, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import os

from ConfigManager.ConfigArgs import ConfigArg, ConfigArgs
from ConfigManager.ConfigManager import ConfigManager

_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
settings_filename = os.path.join(os.path.dirname(__file__), '..', '..','settings.conf')

# dodecode controls how the "tabify" function works for RF2.  If 'true', it is decoded into utf8, if false
#          into unicode.  We use False on Mac systems and True on (some) Linux systems
# autobypass: True means don't do the splash screen
# gatewayport:  Port for the JavaGateway (default is 25333)
# staticroot: URL of the static content server
config_parms = ConfigArgs('settings',
                          [ConfigArg('dodecode', help='Decode string text to utf8', default='False'),
                           ConfigArg('autobypass', help='Skip the splash screen', default='False'),
                           ConfigArg('gatewayport', help='py4j bridge port', default='25333'),
                           ConfigArg('staticroot', help='path to static server files'),
                          ])

settings = ConfigManager(config_parms)