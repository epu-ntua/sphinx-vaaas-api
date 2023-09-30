import sys

import xmltodict
from gvm.connections import UnixSocketConnection
from gvm.errors import GvmError
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeCheckCommandTransform
from lxml import etree

path = '/home/pasiphae/sockets/gvmd.sock'
connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()
username = 'admin'
password = 'admin'
# , transform=transform
try:
    tasks = []
    with Gmp(connection=connection) as gmp:
        gmp.authenticate(username, password)
        print(gmp.get_port_lists())
        # tree = etree.parse(gmp.get_port_lists())
        # tasks = gmp.get_tasks()
        # for task in tasks.xpath('task'):
        #     print(task.find('name').text)
except GvmError as e:
    print('An error occurred', e, file=sys.stderr)
