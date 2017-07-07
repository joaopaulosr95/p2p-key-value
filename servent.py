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
import random
import socket
import struct

from utils import utils, serventutils

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
    parser.add_argument('port', type=int, metavar="port", default='65535', help="port of running server")
    parser.add_argument('input_file', type=str, metavar="input_file", help="input file")
    parser.add_argument('--other_peers', type=str, metavar="HOST:PORT", default=[], nargs="*",
                        help="other peers executing the system")
    opt = parser.parse_args()

    # connection parameters
    srv_host = '0.0.0.0' #socket.gethostbyname(socket.gethostname())
    srv_port = int(opt.port)

    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.bind((srv_host, srv_port))
    logger.info("Server running at %s:%d", srv_host, srv_port)

    # Lets read and achieve the input services list
    service_list = serventutils.read_input_file(opt.input_file)

    # Here we keep a track of all queries we've already answered
    query_history = []

    # Lets generate a random seq to start
    seq = random.randint(0, utils.MAX_SEQ)
    try:
        while True:
            srv_sock.settimeout(utils.RECV_TIMEOUT)
            recv_data = None
            try:
                recv_data, ip_addr = srv_sock.recvfrom(utils.MAX_BUFFER_SIZE)
                srv_sock.settimeout(None)
            except socket.timeout:
                pass
            except socket.error, e:
                logger.error(str(e))
                break

            if recv_data:

                # First of all we extract message_type before processing whole messsage
                recv_message_type = struct.unpack("!H", recv_data[:struct.calcsize("!H")])[0]

                if recv_message_type == utils.MESSAGE_TYPES["CLIREQ"]:
                    recv_header_size = struct.calcsize(utils.MESSAGE_FORMAT["CLIREQ"])

                    # Get key asked from user
                    recv_message = recv_data[recv_header_size:]
                    seq = (seq + 1) % utils.MAX_SEQ

                    if (ip_addr[0], ip_addr[1], seq, recv_message) not in query_history:
                        logger.info("[CLIREQ] %s:%s asked for '%s'" % (ip_addr[0], ip_addr[1],
                                                                       recv_data[recv_header_size:]))
                        if serventutils.local_db_search(srv_sock, service_list, recv_message, ip_addr):

                            # Append query to query_history
                            query_history.append((ip_addr[0], ip_addr[1], seq, recv_message))

                            # Prepare forward query
                            send_header = struct.pack(utils.MESSAGE_FORMAT["QUERY"], utils.MESSAGE_TYPES["QUERY"],
                                                      utils.TTL, utils.ip_to_int(ip_addr[0]), ip_addr[1], seq)
                            send_message = send_header + recv_data[recv_header_size:]
                            for peer in opt.other_peers:

                                # As opt args are stored as string, here we convert peer port to int in order
                                # to properly forward query message
                                peer = tuple([peer.split(":")[0], int(peer.split(":")[1])])
                                # print ("%s:%d => %s:%d" % (peer[0], int(peer[1]), ip_addr[0], int(ip_addr[1])))
                                if peer != ip_addr:
                                    try:
                                        srv_sock.sendto(send_message, peer)
                                        logger.info("Query forwarded successfully to %s", peer)
                                    except:
                                        pass
                            serventutils.forward_query(srv_sock, recv_data, recv_header_size, utils.TTL,
                                                       ip_addr, [(srv_host, srv_port)], seq, opt.other_peers)
                        else:
                            logger.warning("Couldn't find %s in my service list" % recv_message)

                elif recv_message_type == utils.MESSAGE_TYPES["QUERY"]:
                    recv_header_size = struct.calcsize(utils.MESSAGE_FORMAT["QUERY"])
                    _, recv_ttl, recv_from, recv_port, recv_seq = struct.unpack(utils.MESSAGE_FORMAT["QUERY"],
                                                                                recv_data[:recv_header_size])

                    recv_from = utils.int_to_ip(recv_from)

                    # Get key asked from user
                    recv_message = recv_data[recv_header_size:]

                    if (recv_from, recv_port, recv_seq, recv_message) not in query_history:
                        logger.info("[QUERY] %s:%s asked for '%s'" % (recv_from, recv_port,
                                                                      recv_data[recv_header_size:]))
                        if serventutils.local_db_search(srv_sock, service_list, recv_message, (recv_from, recv_port)):

                            # Append query to query_history
                            query_history.append((ip_addr[0], ip_addr[1], seq, recv_message))

                            # Sends query to other peers as long as TTL > 0
                            if recv_ttl > 0:
                                recv_ttl -= 1

                                serventutils.forward_query(srv_sock, recv_data, recv_header_size, recv_ttl,
                                                           (recv_from, recv_port),
                                                           [(ip_addr[0], int(ip_addr[1])), (srv_host, srv_port)],
                                                           seq, opt.other_peers)
                        else:
                            logger.warning("Couldn't find %s in my service list" % recv_message)
    except KeyboardInterrupt:
        print ("Bye =)")
    finally:
        srv_sock.close()
