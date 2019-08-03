# -*- coding: utf-8 -*-
############################################################
#
# Read logs from stdout, then send to RabbitMQ
#
############################################################

import os
import sys
import json
from json.decoder import JSONDecodeError

import logging
import logging.handlers

import asyncio
from aio_pika import connect_robust, Channel, Message, DeliveryMode, ExchangeType
from aio_pika.pool import Pool

import argparse
from subprocess import Popen, PIPE

from logger_helper import print2console

class Sender(object):
    '''Send logs to RabbitMQ
    '''

    def __init__(self, loop):
        '''init begin/end points

        :param pika connection: Connection of RabbitMQ
        '''
        self.loop = loop
        self.logger = init_logger('Sender')
        self.logger.warning('init Sender ...')
        self.__init_pools()

    def __init_pools(self):
        '''init connection pooling
        '''
        def get_connection():
            self.logger.warning('AMQP_URI=%s' % os.getenv(
                "AMQP_URI", "amqp://guest:guest@192.168.130.215/"))
            return connect_robust(os.getenv("AMQP_URI", "amqp://guest:guest@192.168.130.215/"))

        self.connection_pool = Pool(
            get_connection, max_size=5, loop=self.loop)

    def _run(self, command):
        '''start a subprocess and return stdout
        see https://docs.python.org/3/library/subprocess.html#popen-constructor
        '''
        process = Popen(command, bufsize=102400, stdout=PIPE, shell=True)
        while True:
            line = process.stdout.readline().rstrip()
            if not line:
                break
            yield line

    def parse_msg(self, line, verbose=False):
        try:
            json_log = json.loads(line.strip())
            if verbose: print('json_log=%r'%json_log)
            # log not in json format or don't have message field
            if not isinstance(json_log, dict) or json_log.get('message') is None:
                return None
            # Filter non-business logs by `HosCode`
            try:
                msg = json.loads(json_log.get('message'))
                if msg.get('HosCode') is None:
                    return None
            except JSONDecodeError as ex:
                # print('message should in json format, err=%r, msg=%s'%(ex, json_log.get('message')))
                return None
            except AttributeError:
                # message don't have HosCode key
                return None

            msg['collector'] = 'filebeat2rabbit'
            if json_log.get('container') is not None:
                msg['ConName'] = json_log['container'].get('name')
                if(json_log['container'].get('image') is not None):
                    msg['ConImage'] = json_log['container']['image'].get(
                        'name')

            if verbose: print('prepare send msg %r'%msg)
            return msg
        except JSONDecodeError as ex:
            # print('Not container log, ignore ...')
            return None

    async def send(self, msg):
        '''Send with Retry
        '''
        try:
            await self._send(msg)
        except Exception as ex:
            if msg.get("retry") is None:
                msg["retry"] = 1
                await self._send(msg)
            else:
                self.logger.error('Failed to send: err=%r, msg=%s' % (ex, msg))

    async def run(self, verbose):
        '''start a subprocess and read from it's stdout
        if can parse to msg, then send to rabbitmq
        '''

        # https://aio-pika.readthedocs.io/en/latest/quick-start.html#connection-pooling
        async def get_channel() -> Channel:
            async with self.connection_pool.acquire() as connection:
                return await connection.channel(publisher_confirms=False)
        channel_pool = Pool(get_channel, max_size=20, loop=self.loop)

        async with channel_pool.acquire() as channel:  # type: aio_pika.Channel

            logs_exchange = await channel.declare_exchange(
                'task_exchange',
                ExchangeType.TOPIC,
                durable=True
            )

            try:
                for line in self._run(os.getenv("FILEBEAT_CMD", "filebeat -c filebeat.docker.yml")):
                    msg = self.parse_msg(line, verbose)
                    if msg:

                        try:
                            key = '%(HosCode)s.task.%(Product)s.%(Level)s.%(Module)s.%(Action)s' % msg
                        except KeyError as er:
                            self.logger.error('Failed to Generate Routing Key: %r' % er)
                            continue

                        # Sending the message
                        await logs_exchange.publish(
                            Message(
                                bytes(json.dumps(msg), 'utf-8'),
                                delivery_mode=DeliveryMode.PERSISTENT
                            ),
                            routing_key=key)

                        self.logger.debug('Sent: key=[%s], msg=%r' % (key, msg))

                        # await channel.close()
                        
            except KeyboardInterrupt:
                self.logger.error('Exit by Interrupt ...')
                sys.exit(0)
            except Exception as ex:
                self.logger.error('Exit by err=%r'%ex)
                sys.exit(1)


def init_logger(name):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    h_stdout = logging.StreamHandler(sys.stdout)
    h_stdout.setLevel(logging.DEBUG)
    h_stdout.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(h_stdout)
    
    FORMAT = '%(asctime)s - %(module)s - %(levelname)s - %(name)s@%(lineno)d - %(message)s'
    # create stderr handler and set level to error
    h_stderr = logging.StreamHandler() # default use stderr
    h_stderr.setLevel(logging.WARNING)
    h_stderr.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(h_stderr)

    return logger

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Console2RabbitMQ')
    parser.add_argument('--test', dest='test', action='store_true')
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    parser.add_argument('-n', dest='number', type=int, default=100,
                        help='Number of output logs')
    args = parser.parse_args()

    if(args.test):
        print2console(args.number)
    else:
        loop = asyncio.get_event_loop()
        sender = Sender(loop)
        loop.run_until_complete(sender.run(verbose=args.verbose))
