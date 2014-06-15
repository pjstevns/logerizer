import asyncio
import argparse


class SinkServer(asyncio.Protocol):
    def data_received(self, data):
        print(data.decode())

    def connection_list(self):
        pass


def run():
    parser = argparse.ArgumentParser(description='Sink tcp data')
    parser.add_argument('--listen', nargs=1, default=['0.0.0.0:9200'])
    args = parser.parse_args()
    rsock = args.listen[0].split(':')
    rsock[1] = int(rsock[1])

    # server
    loop = asyncio.get_event_loop()
    coro_s = loop.create_server(SinkServer, rsock[0], rsock[1])
    server = loop.run_until_complete(coro_s)
    print('sink listen on {}'.format(server.sockets[0].getsockname()))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('exit')
    finally:
        server.close()
        loop.close()
