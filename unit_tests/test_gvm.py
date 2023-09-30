import unittest
from GVM.gvm_manager import GvmManager
from config.config import get_config

service_config = get_config()
gvm = GvmManager(service_config['GVM_DEV']['socket_path'], service_config['GVM_DEV']['username'], service_config['GVM_DEV']['password'])


class TestGVM(unittest.TestCase):
    def test_get_tasks(self):
        pass
