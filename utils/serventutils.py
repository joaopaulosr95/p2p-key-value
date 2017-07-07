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

import utils

# Logging setup
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s][%(levelname)s] %(message)s",
                    datefmt="%m-%d-%Y %I:%M:%S %p")

"""
| ===================================================================
| read_input_file: gets a list of services from input_file
| ===================================================================
"""

def read_input_file(input_file):
    services = dict()
    with open(input_file) as input_file:
        for line in input_file.readlines():
            line = ''.join(line).strip(' ')
            if line != "#" and not line.isspace():
                splitted_line = line.replace('\t', ' ').replace('  ', ' ').split()
                service_key = splitted_line[0]  # Extracts service name
                services[service_key] = " ".join(splitted_line[1:])  # Service port, protocol and any more info
    return services

"""
| ===================================================================
| local_db_search: takes a key searches for it in local storage
| ===================================================================
"""

def local_db_search(srv_sock, service_list, recv_message, ip_addr):
    logger = logging.getLogger(__name__)

    # Check if key is locally stored
    if recv_message in service_list:

        # Prepare response
        send_header = struct.pack(utils.MESSAGE_FORMAT["RESPONSE"], utils.MESSAGE_TYPES["RESPONSE"])
        send_message = send_header + recv_message + '\t' + service_list[recv_message] + '\x00\x00'
        try:
            srv_sock.sendto(send_message, (ip_addr[0], ip_addr[1]))
            logger.info("Answer sent successfully to %s:%d", ip_addr[0], ip_addr[1])
        except:
            pass
        finally:
            return True
    else:
        return False

"""
| ===================================================================
| forward_query: takes a query and forward it to other peers
| ===================================================================
"""

def forward_query(srv_sock, recv_data, recv_header_size, ttl, from_addr, exclude_list, seq, other_peers):
    logger = logging.getLogger(__name__)

    # Prepare forward query
    send_header = struct.pack(utils.MESSAGE_FORMAT["QUERY"], utils.MESSAGE_TYPES["QUERY"], ttl,
                              utils.ip_to_int(from_addr[0]), from_addr[1], seq)
    send_message = send_header + recv_data[recv_header_size:]
    for peer in other_peers:

        # As opt args are stored as string, here we convert peer port to int in order
        # to properly forward query message
        peer = tuple([peer.split(":")[0], int(peer.split(":")[1])])
        # print ("%s:%d => %s:%d" % (peer[0], int(peer[1]), peer_addr[0], int(peer_addr[1])))
        if peer not in exclude_list:
            try:
                srv_sock.sendto(send_message, peer)
                logger.info("Query forwarded successfully to %s", peer)
            except:
                pass
