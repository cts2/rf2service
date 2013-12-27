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

from config.ConfigArgs import ConfigArg, ConfigArgs
from config.ConfigManager import ConfigManager

_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
settings_filename = os.path.join(os.path.dirname(__file__), '..', '..','settings.conf')

config_parms = ConfigArgs('rf2entries',
                          [ConfigArg('refConcept', help='Sample RF2 Concept Id', default='206421002'),
                           ConfigArg('refDesc', help='Sample RF2 Description Id', default='316561013'),
                           ConfigArg('refRel', help='Sample RF2 Relationship Id', default='3444056025'),
                           ConfigArg('refPredicate', help='Sample RF2 Type ID', default='363698007'),
                           ConfigArg('refTargetConcept', help='Sample RF2 Target Concept Id', default='9972008'),
                           ConfigArg('refSimpleMap', help='Sample RF2 Simple Map Id', default='900000000000498005'),
                           ConfigArg('refSet', help='Sample RF2 Simple Refset Id', default='447565001'),
                           ConfigArg('refComponent', help='Sample RF2 Component Id', default='10495001'),
                           ConfigArg('refMapSource', help='Sample RF2 Map Source Id', default='5204005'),
                           ConfigArg('refMapTarget', help='Sample RF2 Map Target Id', default='C47.5'),
                           ConfigArg('refMatchvalue', help='Sample Description Match Value', default='Append')
                           ])

settings = ConfigManager(config_parms, cfgfile=settings_filename)

