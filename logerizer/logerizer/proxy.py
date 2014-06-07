import asyncio
import sys


class LogerizeServer(asyncio.Protocol):

    def connection_made(self, transport):
        self.peer = transport.get_extra_info('peername')
        print('connection from {}'.format(self.peer))
        self.transport = transport

    def connection_lost(self, exc):
        print('connection lost from {}'.format(self.peer))

    def data_received(self, data):
        print('data from {} received: {}'.format(
            self.peer,
            data.decode()))
        self.process_data(data)

    def process_data(self, data):
        lines = data.decode().split('\n')
        lines = [x.strip() for x in lines]
        lines = [x for x in lines if x]
        lines = [x.split(None, 5) for x in lines]
        self.transport.write(data)


def run():
    print('args: {}'.format(sys.argv))
    rsock = sys.argv[1].split(':')
    wsock = sys.argv[2].split(':')
    rsock[1] = int(rsock[1])
    wsock[1] = int(wsock[1])

    loop = asyncio.get_event_loop()
    coro = loop.create_server(LogerizeServer, rsock[0], rsock[1])
    server = loop.run_until_complete(coro)
    print('listen on {}'.format(server.sockets[0].getsockname()))
    print('write on {}'.format(wsock))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('exit')
    finally:
        server.close()
        loop.close()
