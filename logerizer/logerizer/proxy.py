import asyncio
import argparse

wsock = None


class LogerizeClient(asyncio.Protocol):
    def connection_made(self, transport):
        self.connected = True
        self.peer = transport.get_extra_info('peername')
        self.transport = transport

    def connection_lost(self, exc):
        self.connected = False


class LogerizeServer(asyncio.Protocol):
    clients = {}
    queue = None
    _buffer = None

    def __init__(self, *args, **kw):
        super(LogerizeServer, self).__init__(*args, **kw)

    def connection_made(self, transport):
        self.peer = transport.get_extra_info('peername')
        print('connection from {}'.format(self.peer))
        self.transport = transport
        self._buffer = bytearray()

    def connection_lost(self, exc):
        print('connection lost from {}'.format(self.peer))

    def data_received(self, data):
        self.process_data(data)

    def flush(self):
        if not self.queue:
            return
        msg = '\n\t'.join(self.queue.get('msg'))
        key = self.queue.get('key')
        data = '%s: %s' % (key, msg)
        asyncio.Task(self.send_data(data.encode()))
        self.queue = None

    @asyncio.coroutine
    def send_data(self, data):
        global wsock
        client = self.clients.get(self.peer)
        if client is None or not client.connected:
            loop = asyncio.get_event_loop()
            proto, client = yield from loop.create_connection(
                LogerizeClient, wsock[0], wsock[1])
            client.server_transport = self.transport
            self.clients[self.peer] = client
        client.transport.write(data)
        client.transport.close()

    def process_data(self, data):
        self._buffer += bytearray(data)
        assert(isinstance(self._buffer, bytearray))
        lastnl = self._buffer.rindex(b'\n')

        data = self._buffer[:lastnl+1].decode()
        rest = self._buffer[lastnl+1:]
        self._buffer = bytearray(rest)
        lines = [x for x in data.split('\n') if x]
        for line in lines:
            try:
                keylen = line[15:].index(':') + 15
                key = line[:keylen]
                msg = line[keylen+2:]
            except:
                msg = line

            if self.queue:
                if self.queue.get('key') == key:
                    self.queue['msg'].append(msg)
                else:
                    self.flush()
            if not self.queue:
                self.queue = dict(
                    key=key,
                    msg=[msg, ]
                )

        loop = asyncio.get_event_loop()
        loop.call_later(2, self.flush)


def run():
    global loop
    global wsock
    parser = argparse.ArgumentParser(description='Cleanup syslog messages')
    parser.add_argument('--listen', nargs=1, default=['0.0.0.0:5542'])
    parser.add_argument('--sendto', nargs=1, default=['localhost:9200'])
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
