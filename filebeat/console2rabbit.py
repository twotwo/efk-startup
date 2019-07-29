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
from aio_pika import connect, Message, DeliveryMode, ExchangeType


class Sender(object):
    '''Send logs to RabbitMQ
    '''

    def __init__(self, rabbit):
        '''init begin/end points

        :param pika connection: Connection of RabbitMQ
        '''
        self.loop = asyncio.get_event_loop()
        self._pikaConnections = rabbit

        self.logger = init_logger('Sender')
        self.logger.info('Sender init')
        self.logger.warning('_pikaConnection=%s' % rabbit)

    def send(self, msg):
        
        self.loop.run_until_complete(self._send(msg))

    async def _send(self, msg):
        '''send msg to RabbitMQ
        '''
        try:
            key = '%(HosCode)s.task.%(Product)s.%(Level)s.%(Module)s.%(Action)s'%msg
        except KeyError as err:
            self.logger.warning('Failed to Generate Routing Key: %r'%err)
            return
        # Perform connection
        connection = await connect("amqp://guest:guest@192.168.130.215/", loop=self.loop)
        # Creating a channel
        channel = await connection.channel()
        logs_exchange = await channel.declare_exchange(
            'task_exchange',
            ExchangeType.TOPIC
        )

        message = Message(
            bytes(json.dumps(msg), 'utf-8'),
            delivery_mode=DeliveryMode.PERSISTENT
        )

        # Sending the message
        await logs_exchange.publish(message, routing_key=key)

        self.logger.debug('Sent: key=[%s], msg=%r' % (key, msg))

        await connection.close()


def init_logger(name):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    FORMAT = '%(asctime)s - %(module)s - %(levelname)s - %(name)s@%(lineno)d - %(message)s'
    datefmt = '%y/%m/%d %H:%M:%S'

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # add formatter to ch
    ch.setFormatter(logging.Formatter(FORMAT))

    # add ch to logger
    logger.addHandler(ch)

    # create TimedRotatingFileHandler
    trfh = logging.handlers.TimedRotatingFileHandler(
        filename='trans_log.log', when='D', interval=1,  encoding='utf8')
    trfh.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(trfh)

    return logger


def letsrock():
    '''readline from stdin, then print to stdout
    '''
    sender = Sender('rabbit config')
    for line in sys.stdin:

        try:
            json_log = json.loads(line.strip())
            if(json_log.get('message') is None):
                continue
            # Filter non-business logs by `HosCode`
            try:
                msg = json.loads(json_log.get('message'))
            except JSONDecodeError as ex:
                # print('message should in json format, msg=%s'%json_log.get('message'))
                continue
            if(msg.get('HosCode') is None):
                continue
            msg['collector'] = 'console2rabbit.py'
            if(json_log.get('container') is not None):
                msg['ConName'] = json_log['container'].get('name')
                if(json_log['container'].get('image') is not None):
                    msg['ConImage'] = json_log['container']['image'].get(
                        'name')
            sender.send(msg)
        except JSONDecodeError as ex:
            # print('Not container log, ignore ...')
            pass
        except KeyboardInterrupt as ex:
            print('KeyboardInterrupt')
        finally:
            # print(line.strip())
            pass


if __name__ == '__main__':

    letsrock()
