#!/usr/bin/env python
# coding=utf-8

"""
Copyright (c) 2017 Joao Paulo Bastos <joaopaulosr95@gmail.com>

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
import random
import socket
import struct

import utils

# Logging setup
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s][%(levelname)s]%(message)s",
    datefmt="%m-%d-%Y %I:%M:%S %p")

"""
| ===================================================================
| read_input_file: gets a list of services from input_file
| ===================================================================
"""


def read_input_file(input_file):
    services = dict()
    with open(input_file) as input_file:
        try:
            line = input_file.readline().strip()
            if line[0:1] != "#" and not line.isspace():
                splitted_line = line.split(None, )
                service_key = splitted_line[0]  # Extracts service name
                service_val = " ".join(splitted_line[1:len(splitted_line)])  # Service port, protocol and any more info
                services[service_key] = service_val
        except IOError:
            input_file.close()
    return services


"""
| ===================================================================
| main program
| ===================================================================
"""
if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, metavar="port", default='65535', help="port of running server")
    parser.add_argument('input_file', type=str, metavar="input_file", help="input file")
    parser.add_argument('--other_peers', type=str, metavar="HOST:PORT", default=[], nargs="*",
        help="other peers executing the system")
    opt = parser.parse_args()
    print opt

    # connection parameters
    srv_host = '0.0.0.0'
    srv_port = int(opt.port)

    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.bind((srv_host, srv_port))
    logger.info("Server running at %s:%d", srv_host, srv_port)

    # Lets read and achieve the input services list
    service_list = read_input_file(opt.input_file)
    query_history = []

    seq = random.randint(0, utils.MAX_SEQ)
    while True:
        srv_sock.settimeout(utils.RECV_TIMEOUT)
        try:
            recv_data, ip_addr = srv_sock.recvfrom(utils.MAX_BUFFER_SIZE)
            srv_sock.settimeout(None)
            if recv_data:
                recv_message_type = struct.unpack("!H", recv_data[:struct.calcsize("!H")])[0]
		logger.info('{} from {}'.format(recv_message_type, str(ip_addr[0])))

                if recv_message_type == utils.MESSAGE_TYPES["CLIREQ"]:
                    recv_header_size = struct.calcsize(utils.MESSAGE_FORMAT["CLIREQ"])
                    recv_unpacked = struct.unpack(utils.MESSAGE_FORMAT["CLIREQ"], recv_data[:recv_header_size])
                    logger.info("%s:%d asked for '%s'" % (ip_addr[0], ip_addr[1], recv_data[recv_header_size:]))

                    send_header = struct.pack(utils.MESSAGE_FORMAT["QUERY"], utils.MESSAGE_TYPES["QUERY"],
                        utils.TTL, ip_addr[0], ip_addr[1], seq)
                    for peer in opt.other_peers:
                        if peer != ip_addr:
                            try:
                                srv_sock.sendto(send_header + recv_data[recv_header_size:], (peer[0], peer[1]))
                            except:
                                pass

                    if (ip_addr[0], ip_addr[1], seq, recv_message) not in query_history:
                        if recv_message in service_list:
                            send_header = struct.pack(utils.MESSAGE_FORMAT["RESPONSE"], utils.MESSAGE_TYPES["RESPONSE"])
                            srv_sock.sendto(send_header + service_list[recv_message], (recv_from, recv_port))

                    seq = (seq + 1) % utils.MAX_SEQ

                elif recv_message_type == utils.MESSAGE_TYPES["QUERY"]:
                    recv_header_size = struct.calcsize(utils.MESSAGE_FORMAT["QUERY"])
                    recv_message_type, recv_ttl, recv_from, recv_port, recv_seq = struct.unpack(
                        utils.MESSAGE_FORMAT["QUERY"], recv_data[:recv_header_size])

                    # Get key asked from user
                    recv_message = recv_data[recv_header_size:]

                    if (recv_from, recv_port, recv_seq, recv_message) not in query_history:
                        logger.info("%s:%d asked for '%s'" % (ip_addr[0], ip_addr[1], recv_data[recv_header_size:]))

                        # Checks if key is locally stored
                        if recv_message in service_list:
                            send_header = struct.pack(utils.MESSAGE_FORMAT["RESPONSE"], utils.MESSAGE_TYPES["RESPONSE"])
                            srv_sock.sendto(send_header + service_list[recv_message], (recv_from, recv_port))

                        # Sends query to other peers as long as TTL > 0
                        if recv_ttl > 0:
                            recv_ttl -= 1
                            send_header = struct.pack(utils.MESSAGE_FORMAT["QUERY"], utils.MESSAGE_TYPES["QUERY"],
                                recv_ttl, recv_from, recv_port, recv_seq)
                            for peer in opt.other_peers:
                                if peer != ip_addr:
                                    try:
                                        srv_sock.sendto(send_header + recv_data[recv_header_size:], (peer[0], peer[1]))
                                    except:
                                        pass

        except socket.timeout:
            pass
        except KeyboardInterrupt:
            break
        except socket.error:
            break

    srv_sock.close()
