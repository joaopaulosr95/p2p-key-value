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
import argparse
import logging
import socket
import struct
import sys

from utils import utils, clientutils

# Logging setup
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s][%(levelname)s] %(message)s",
                    datefmt="%m-%d-%Y %I:%M:%S %p")

"""
| ===================================================================
| main program
| ===================================================================
"""
if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('server', type=str, metavar="host:port", help="ip:port of running server")
    opt = parser.parse_args()

    # connection parameters
    srv_host, srv_port = opt.server.split(":")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def flush():
        sys.stdout.write("Enter a service name to search: ")
        sys.stdout.flush()

    flush()
    while True:
        try:
            user_input = raw_input()
            if user_input.lower() == 'exit':
                logger.info(" Bye =)")
                break
            elif len(user_input) == 0:
                logger.warning("Your query must be at least 1 character long")
            else:

                # Prepare query
                send_header = struct.pack(utils.MESSAGE_FORMAT["CLIREQ"], utils.MESSAGE_TYPES["CLIREQ"])
                clientutils.p2p_ask_kv(sock, send_header, user_input.lower(), srv_host, srv_port)
            flush()
        except KeyboardInterrupt:
            print("\nBye =)")
            break
    sock.close()
