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

import logging
import struct
import socket
import utils

"""
| ===================================================================
| get_responses: watch network for query responses
| ===================================================================
"""
def get_responses(sock):
    logger = logging.getLogger(__name__)

    responses = 0
    while True:
        sock.settimeout(utils.RECV_TIMEOUT)
        try:
            recv_data, ip_addr = sock.recvfrom(utils.MAX_BUFFER_SIZE)
            sock.settimeout(None)
            if recv_data:
                recv_header_size = struct.calcsize(utils.MESSAGE_FORMAT["RESPONSE"])
                recv_message_type = struct.unpack(utils.MESSAGE_FORMAT["RESPONSE"], recv_data[:recv_header_size])[0]
                if recv_message_type == utils.MESSAGE_TYPES["RESPONSE"]:
                    logger.info("%s:%d answers '%s'" % (ip_addr[0], ip_addr[1], recv_data[recv_header_size:]))
                    responses += 1
        except socket.timeout:
            if responses > 0:
                logger.info("Received: %d responses", responses)
                break
            else:
                raise

"""
| ===================================================================
| p2p_ask_kv: asks network for a key and waits for response
| ===================================================================
"""
def p2p_ask_kv(sock, send_header, key, srv_host, srv_port):
    logger = logging.getLogger(__name__)

    for i in range(0, 2):
        sock.settimeout(utils.RECV_TIMEOUT)
        try:
            sock.sendto(send_header + key, (srv_host, int(srv_port)))
            sock.settimeout(None)
            try:
                get_responses(sock)
                break
            except:
                raise
        except socket.timeout:
            if i == 1:
                logger.warning("Nothing was received after two attempts. Moving on...")
            else:
                logger.warning("Timeout for first attempt exceeded. Retrying...")
