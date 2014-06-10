import asyncio
import argparse
import time


class LogerizeClient(asyncio.Protocol):
    def connection_made(self, transport):
        self.connected = True
        self.peer = transport.get_extra_info('peername')
        print('connection to {}'.format(self.peer))
        self.transport = transport

    def connection_lost(self, exc):
        print('connection lost from {}'.format(self.peer))

    def data_received(self, data):
        print('send data: %s' % data.decode())
        self.server_transport.write(data)


class LogerizeServer(asyncio.Protocol):
    client = None
    queue = None

    def connection_made(self, transport):
        self.peer = transport.get_extra_info('peername')
        print('connection from {}'.format(self.peer))
        self.transport = transport

    def connection_lost(self, exc):
        print('connection lost from {}'.format(self.peer))

    def data_received(self, data):
        self.process_data(data)

    def flush(self):
        msg = '\n\t'.join(self.queue.get('msg'))
        key = self.queue.get('key')
        data = '%s: %s\n' % (key, msg)
        asyncio.Task(self.send_data(data.encode()))
        self.queue = None

    @asyncio.coroutine
    def send_data(self, data):
        client = self.client
        if client is None or not client.connected:
            protocol, client = yield from loop.create_connection(
                LogerizeClient, wsock[0], wsock[1])
            client.server_transport = self.transport
            self.client = client
        client.transport.write(data)

    def process_data(self, data):
        lines = [x for x in data.decode().split('\n') if x]
        for line in lines:
            try:
                keylen = line[15:].index(':') + 15
            except:
                print('ERR: %s' % line)
                continue
            key = line[:keylen]
            msg = line[keylen+2:]
            if self.queue:
                if self.queue.get('key') == key:
                    self.queue['msg'].append(msg)
                elif self.queue.get('key'):
                    self.flush()
            if not self.queue:
                self.queue = dict(
                    key=key,
                    msg=[msg, ]
                )
        if self.queue:
            self.flush()


def run():
    global loop
    global wsock
    parser = argparse.ArgumentParser(description='Cleanup syslog messages')
    parser.add_argument('--listen', nargs=1, default='0.0.0.0:5542')
    parser.add_argument('--sendto', nargs=1, default='localhost:9200')
    args = parser.parse_args()
    rsock = args.listen[0].split(':')
    wsock = args.sendto[0].split(':')
    rsock[1] = int(rsock[1])
    wsock[1] = int(wsock[1])

    # server
    loop = asyncio.get_event_loop()
    coro_s = loop.create_server(LogerizeServer, rsock[0], rsock[1])
    server = loop.run_until_complete(coro_s)
    print('listen on {}'.format(server.sockets[0].getsockname()))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('exit')
    finally:
        server.close()
        loop.close()
