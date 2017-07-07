#!/usr/bin/env python
# coding=utf-8

"""
Copyright (c) 2017
Gabriel Pacheco     <gabriel.pacheco@dcc.ufmg.br>
Guilherme Sousa     <gadsousa@gmail.com>
Joao Paulo Bastos   <joaopaulosr95@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import socket
import struct

"""
| ===================================================================
| Constants definition
| ===================================================================
"""

MESSAGE_TYPES = {"CLIREQ": 1, "QUERY": 2, "RESPONSE": 3}
MESSAGE_FORMAT = {"CLIREQ": "!H", "QUERY": "!HHLHL", "RESPONSE": "!H"}
MAX_BUFFER_SIZE = 1000
MAX_SEQ = 4294967295L
RECV_TIMEOUT = 4.0
TTL = 3

"""
| ===================================================================
| ip_to_int: converts ip address to long
| ===================================================================
"""
def ip_to_int(ip):
    return struct.unpack("!L", socket.inet_aton(ip))[0]

"""
| ===================================================================
| int_to_ip: converts long to ip address
| ===================================================================
"""
def int_to_ip(intip):
    return socket.inet_ntoa(struct.pack("!L", intip))
