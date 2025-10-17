import re
import asyncio


class UDPClientProtocol(asyncio.DatagramProtocol):
    """ This class is necessary because asyncio.DatagramProtocol does not introduce data receiving """

    def __init__(self):
        super().__init__()
        self.recvq = asyncio.Queue()

    def datagram_received(self, data, addr):
        self.recvq.put_nowait(data)

    async def _recv_until(self, eot: bytes) -> list[bytes]:
        packets = []
        while True:
            data = await self.recvq.get()
            packets.append(data)
            if data.endswith(eot):
                return packets

    async def recv_many(self, eot: bytes, timeout: int = 5) -> list[bytes]:
        return await asyncio.wait_for(self._recv_until(eot=eot), timeout=timeout)

    async def recv_one(self, timeout: int = 5):
        return await asyncio.wait_for(self.recvq.get(), timeout=timeout)


async def query_master(address: str, port: int, timeout: int = 5) -> list[tuple]:
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPClientProtocol(),
        remote_addr=(address, port)
    )
    transport.sendto(b'\xff\xff\xff\xffgetservers 68 empty full\x00', (address, port))
    packets = await protocol.recv_many(eot=b'EOT\x00\x00\x00', timeout=timeout)

    servers = []
    for data in packets:
        if data[:23] != b'\xff\xff\xff\xffgetserversResponse\\':
            raise ValueError('Invalid server response.')
        data = data[23:]

        for i in range(0, len(data), 7):
            entry = data[i:i+7]
            if entry == b'EOT\x00\x00\x00':
                break
            _ip = f'{entry[0]}.{entry[1]}.{entry[2]}.{entry[3]}'
            _port = (entry[4] << 8) + entry[5]
            servers.append((_ip, _port))
    return servers


async def query_server(address: str, port: int, timeout: int = 5) -> dict | None:
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPClientProtocol(),
        remote_addr=(address, port)
    )
    transport.sendto(b'\xff\xff\xff\xffgetstatus\x00', (address, port))
    packet = await protocol.recv_one(timeout=timeout)
    transport.close()

    data = packet.strip().split(b'\n')
    if data[0] != b'\xff\xff\xff\xffstatusResponse':
        raise ValueError('Invalid server response.')

    server_info = {'address': address, 'port': port}
    opts = data[1].strip(b'\\').split(b'\\')
    if len(opts) % 2 != 0:
        raise ValueError('Bad server info string.')
    for i in range(0, len(opts)-1, 2):
        value = int(opts[i+1]) if opts[i+1].isdigit() else opts[i+1].decode()
        server_info[opts[i].decode()] = value

    server_info['players'] = []
    for p_data in data[2:]:
        ping, score, name = p_data.split(b' ', maxsplit=2)
        raw_name = name.strip(b'"').decode()
        server_info['players'].append({
            'ping': int(ping),
            'score': int(score),
            'raw_name': name.strip(b'"').decode(),
            'name': re.sub(r'\^.', '', raw_name)
        })
    return server_info


def do_cli():
    import argparse
    parser = argparse.ArgumentParser(description='Query quake servers.')
    parser.add_argument('-q3m', help='query Quake III Arena ♂master♂ server', metavar='address:port')
    parser.add_argument('-q3s', help='query Quake III Arena server', metavar='address:port')
    args = parser.parse_args()

    if args.q3m:
        address, port = args.q3m.split(':')
        print(f'Querying ♂master♂ server {address}:{port}...')
        res = asyncio.run(query_master(address, int(port)))
        for address, port in res:
            print(f'{address}:{port}')
        print('------------------------')
        print(f'{len(res)} servers found.')

    elif args.q3s:
        address, port = args.q3s.split(':')
        res = asyncio.run(query_server(address, int(port)))
        for key in res:
            print(f'{key}: {res[key]}')

    else:
        print(parser.print_help())


if __name__ == '__main__':
    do_cli()

