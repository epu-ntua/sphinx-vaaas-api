import sys
import xmltodict
from gvm.connections import SSHConnection, UnixSocketConnection
from gvm.errors import GvmError
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform, EtreeCheckCommandTransform
from gvm import xml
import logging
import json
from utils.utils import *
from app_logger.logger import MyLogger
from config.config import get_config
import sys

mode = None
if sys.argv[1] == 'dev':
    mode = 'GVM_DEV'
else:
    mode = 'GVM_PROD'
conf = get_config()
log =get_main_logger('gvm_manager')


class GvmManager:
    def __init__(self, socket_path, username, password):
        self._gmp = None
        self.s_path = socket_path
        self.uname = username
        self.passwd = password

    # @retry
    def get_gvm(self):
        try:
            # connection = UnixSocketConnection(path=self.s_path)
            connection = SSHConnection(hostname=conf[mode]['docker'], username=conf[mode]['ssh_user'], password=conf[mode]['ssh_pass'], port=conf[mode]['ssh_port'])
            with Gmp(connection=connection) as gmp:
                gmp.authenticate(self.uname, self.passwd)
                assert gmp is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
                self._gmp = gmp
                return gmp
        except GvmError as e:
            print('An error occurred', e, file=sys.stderr)
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
        except Exception as e:
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())

    def get_gmp_ssh(self):
        try:
            connection = SSHConnection(hostname=conf[mode]['docker'], username=conf['mode']['ssh_user'], password=conf['mode']['ssh_pass'], port=conf['mode']['ssh_port'])
            transform = EtreeTransform()
            with Gmp(connection=connection, transform=transform) as gmp:
                gmp.authenticate(self.uname, self.passwd)
                assert gmp is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
                self._gmp = gmp
                return gmp
        except GvmError as e:
            print('An error occurred', e, file=sys.stderr)
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())

    # ##############   TASKS    ###########################
    def get_version(self):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' - GMP is None '
            result = _gvm.get_version()
            return create_result('GET_VERSION_SUCCESS', xmltodict.parse(result)['get_version_response'], 1, 20, 'GET_TASKS_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_VERSION_FAILURE', None, 1, 1, e.__str__())

    # ##############   TASKS    ###########################

    def get_tasks(self, request_args, **kwargs):
        arguments = get_pagination_filter(request_args)
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_tasks(**arguments)
            print(result)
            return create_result('GET_TASKS_SUCCESS', xmltodict.parse(result)['get_tasks_response'], 1, 20, 'GET_TASKS_SUCCESS')
            # return create_result('GET_TASKS_SUCCESS', None, 1, 20, 'GET_TASKS_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_TASKS_FAILURE', None, 1, 1, e.__str__())

    def get_task(self, task_id):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_task(task_id=task_id)
            return create_result('GET_TASK_SUCCESS', xmltodict.parse(result)['get_tasks_response'], 1, 20, 'GET_TASK_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_TASK_FAILURE', None, 1, 1, e.__str__())

    def create_task(self, payload, **kwargs):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            arguments = {
                "name": payload.get('name') if checkValues(payload, 'name') else None,
                "config_id": payload.get('config_id') if checkValues(payload, 'config_id') else None,
                "target_id": payload.get('target_id') if checkValues(payload, 'target_id') else None,
                "scanner_id": payload.get('scanner_id') if checkValues(payload, 'scanner_id') else None,
                "alterable": payload.get('alterable') if checkValues(payload, 'alterable') else None,
                "hosts_ordering": payload.get('hosts_ordering') if checkValues(payload, 'hosts_ordering') else None,
                "schedule_id": payload.get('schedule_id') if checkValues(payload, 'schedule_id') else None,
                "alert_ids": payload.get('alert_ids') if checkValues(payload, 'alert_ids') else None,
                "comment": payload.get('comment') if checkValues(payload, 'comment') else None,
                "schedule_periods": payload.get('schedule_periods') if checkValues(payload, 'schedule_periods') else None,
                "observers": payload.get('observers') if checkValues(payload, 'observers') else None,
                "preferences": payload.get('preferences') if checkValues(payload, 'preferences') else None,
            }
            result = _gvm.create_task(**arguments)
            return create_result('CREATE_TASK_SUCCESS', xmltodict.parse(result)['create_task_response'], 1, 20, 'CREATE_TASK_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('CREATE_TASK_FAILURE', None, 1, 1, e.__str__())

    def update_task(self, task_id, payload, **kwargs):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            arguments = {
                "task_id": task_id,
                "name": payload.get('name') if checkValues(payload, 'name') else None,
                "config_id": payload.get('config_id') if checkValues(payload, 'config_id') else None,
                "target_id": payload.get('target_id') if checkValues(payload, 'target_id') else None,
                "scanner_id": payload.get('scanner_id') if checkValues(payload, 'scanner_id') else None,
                "alterable": payload.get('alterable') if checkValues(payload, 'alterable') else None,
                "hosts_ordering": payload.get('hosts_ordering') if checkValues(payload, 'hosts_ordering') else None,
                "schedule_id": payload.get('schedule_id') if checkValues(payload, 'schedule_id') else None,
                "alert_ids": payload.get('alert_ids') if checkValues(payload, 'alert_ids') else None,
                "comment": payload.get('comment') if checkValues(payload, 'comment') else None,
                "schedule_periods": payload.get('schedule_periods') if checkValues(payload, 'schedule_periods') else None,
                "observers": payload.get('observers') if checkValues(payload, 'observers') else None,
                "preferences": payload.get('preferences') if checkValues(payload, 'preferences') else None,
            }
            result = _gvm.modify_task(**arguments)
            return create_result('UPDATE_TASK_SUCCESS', xmltodict.parse(result)['update_task_response'], 1, 20, 'UPDATE_TASK_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('UPDATE_TASK_FAILURE', None, 1, 1, e.__str__())

    def delete_task(self, task_id):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.delete_task(task_id=task_id)
            return create_result('DELETE_TASK_SUCCESS', xmltodict.parse(result)['delete_task_response'], 1, 20, 'DELETE_TASK_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('DELETE_TASK_FAILURE', None, 1, 1, e.__str__())

    def start_task(self, task_id):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.start_task(task_id=task_id)
            return create_result('START_TASK_SUCCESS', xmltodict.parse(result)['start_task_response'], 1, 20, 'START_TASK_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('START_TASK_FAILURE', None, 1, 1, e.__str__())

    def stop_task(self, task_id):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.stop_task(task_id=task_id)
            return create_result('STOP_TASK_SUCCESS', xmltodict.parse(result)['stop_task_response'], 1, 20, 'STOP_TASK_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('STOP_TASK_FAILURE', None, 1, 1, e.__str__())

    def get_task_progress(self, task_id):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_task(task_id=task_id)
            return create_result('GET_TASK_PROGRESS_SUCCESS', xmltodict.parse(result)['get_tasks_response']['task'], 1, 20, 'GET_TASK_PROGRESS_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_TASK_PROGRESS_FAILURE', None, 1, 1, e.__str__())

    # ##############   SCANNERS    ###########################
    def get_scanners(self, request_args, **kwargs):
        arguments = get_pagination_filter(request_args)
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_scanners(**arguments)
            print(result)
            return create_result('GET_SCANNERS_SUCCESS', xmltodict.parse(result)['get_scanners_response'], 1, 20, 'GET_SCANNERS_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_SCANNERS_FAILURE', None, 1, 1, e.__str__())

    def get_scanner(self, scanner_id):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_scanner(scanner_id=scanner_id)
            return create_result('GET_SCANNER_SUCCESS', xmltodict.parse(result)['get_scanners_response'], 1, 20, 'GET_SCANNER_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_SCANNER_FAILURE', None, 1, 1, e.__str__())

    def create_scanner(self, payload):
        pass

    def delete_scanner(self, request_args, **kwargs):
        pass

    def update_scanner(self, payload):
        pass

    #  ##############   TARGETS    ###########################
    def get_targets(self, request_args, **kwargs):
        arguments = get_pagination_filter(request_args)
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_targets(**arguments)
            return create_result('GET_TARGETS_SUCCESS', xmltodict.parse(result)['get_targets_response'], 1, 20, 'GET_TARGETS_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_TARGETS_FAILURE', None, 1, 1, e.__str__())

    def get_target(self, target_id, **kwargs):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_target(target_id=target_id)
            return create_result('GET_TARGET_SUCCESS', xmltodict.parse(result)['get_targets_response'], 1, 20, 'GET_TARGET_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_TARGET_FAILURE', None, 1, 1, e.__str__())

    def create_target(self, payload, **kwargs):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            arguments = {
                "name": payload.get('name') if checkValues(payload, 'name') else None,
                "hosts": payload.get('hosts') if checkValues(payload, 'hosts') else None,
                "make_unique": payload.get('make_unique') if checkValues(payload, 'make_unique') else None,
                "asset_hosts_filter": payload.get('asset_hosts_filter') if checkValues(payload, 'asset_hosts_filter') else None,
                "comment": payload.get('comment') if checkValues(payload, 'comment') else None,
                "exclude_hosts": payload.get('exclude_hosts') if checkValues(payload, 'exclude_hosts') else None,
                "ssh_credential_id": payload.get('ssh_credential_id') if checkValues(payload, 'ssh_credential_id') else None,
                "ssh_credential_port": payload.get('ssh_credential_port') if checkValues(payload, 'ssh_credential_port') else None,
                "smb_credential_id": payload.get('smb_credential_id') if checkValues(payload, 'smb_credential_id') else None,
                "esxi_credential_id": payload.get('esxi_credential_id') if checkValues(payload, 'esxi_credential_id') else None,
                "snmp_credential_id": payload.get('snmp_credential_id') if checkValues(payload, 'snmp_credential_id') else None,
                "alive_test": payload.get('alive_test') if checkValues(payload, 'alive_test') else None,
                "reverse_lookup_only": payload.get('reverse_lookup_only') if checkValues(payload, 'reverse_lookup_only') else None,
                "reverse_lookup_unify": payload.get('reverse_lookup_unify') if checkValues(payload, 'reverse_lookup_unify') else None,
                "port_range": payload.get('port_range') if checkValues(payload, 'port_range') else None,
                "port_list_id": payload.get('port_list_id') if checkValues(payload, 'port_list_id') else None,
            }
            result = _gvm.create_target(**arguments)
            return create_result('CREATE_TARGET_SUCCESS', xmltodict.parse(result)['create_target_response'], 1, 20, 'CREATE_TARGET_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('CREATE_TARGET_FAILURE', None, 1, 1, e.__str__())

    def delete_target(self, target_id):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.delete_target(target_id=target_id)
            return create_result('DELETE_TARGET_SUCCESS', xmltodict.parse(result)['delete_target_response'], 1, 20, 'DELETE_TARGET_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('DELETE_TARGET_FAILURE', None, 1, 1, e.__str__())

    def update_target(self, target_id, payload):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            arguments = {
                "target_id": target_id,
                "name": payload.get('name') if checkValues(payload, 'name') else None,
                "hosts": payload.get('hosts') if checkValues(payload, 'hosts') else None,
                "comment": payload.get('comment') if checkValues(payload, 'comment') else None,
                "exclude_hosts": payload.get('exclude_hosts') if checkValues(payload, 'exclude_hosts') else None,
                "ssh_credential_id": payload.get('ssh_credential_id') if checkValues(payload, 'ssh_credential_id') else None,
                "ssh_credential_port": payload.get('ssh_credential_port') if checkValues(payload, 'ssh_credential_port') else None,
                "smb_credential_id": payload.get('smb_credential_id') if checkValues(payload, 'smb_credential_id') else None,
                "esxi_credential_id": payload.get('esxi_credential_id') if checkValues(payload, 'esxi_credential_id') else None,
                "snmp_credential_id": payload.get('snmp_credential_id') if checkValues(payload, 'snmp_credential_id') else None,
                "alive_test": payload.get('alive_test') if checkValues(payload, 'alive_test') else None,
                "reverse_lookup_only": payload.get('reverse_lookup_only') if checkValues(payload, 'reverse_lookup_only') else None,
                "reverse_lookup_unify": payload.get('reverse_lookup_unify') if checkValues(payload, 'reverse_lookup_unify') else None,
                "port_list_id": payload.get('port_list_id') if checkValues(payload, 'port_list_id') else None,
            }
            result = _gvm.modify_target(**arguments)
            return create_result('UPDATE_TARGET_SUCCESS', xmltodict.parse(result)['modify_target_response'], 1, 20, 'UPDATE_TARGET_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('UPDATE_TARGET_FAILURE', None, 1, 1, e.__str__())

    # ##############   REPORTS    ###########################
    def get_reports(self, request_args, **kwargs):
        arguments = get_pagination_filter(request_args)
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_reports(**arguments)
            return create_result('GET_REPORTS_SUCCESS', xmltodict.parse(result)['get_reports_response'], 1, 20, 'GET_REPORTS_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_REPORTS_FAILURE', None, 1, 1, e.__str__())

    def get_report(self, report_id):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_report(report_id=report_id)
            return create_result('GET_REPORT_SUCCESS', xmltodict.parse(result)['get_reports_response'], 1, 20, 'GET_REPORT_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_REPORT_FAILURE', None, 1, 1, e.__str__())

    def get_report_details(self, report_id, payload):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            arguments = {
                "report_id": report_id,
                "filter": payload.get('filter') if checkValues(payload, 'filter') else None,
                "filter_id": payload.get('filter_id') if checkValues(payload, 'filter_id') else None,
                "delta_report_id": payload.get('delta_report_id') if checkValues(payload, 'delta_report_id') else None,
                "report_format_id": payload.get('report_format_id') if checkValues(payload, 'report_format_id') else None,
                "ignore_pagination": payload.get('ignore_pagination') if checkValues(payload, 'ignore_pagination') else None,
                "details": payload.get('details') if checkValues(payload, 'details') else None
            }
            result = _gvm.get_report(**arguments)
            return create_result('GET_REPORT_DETAILS_SUCCESS', xmltodict.parse(result)['get_reports_response'], 1, 20, 'GET_REPORT_DETAILS_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_REPORT_DETAILS_FAILURE', None, 1, 1, e.__str__())

    def delete_report(self, request_args):
        return create_result('GET_REPORT_FAILURE', '', 1, 20, 'FUNCTION NOT YET IMPLEMENTED', '405')

    def get_report_formats(self, request_args):
        arguments = get_pagination_filter(request_args)
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_report_formats(**arguments)
            return create_result('GET_REPORT_FORMATS_SUCCESS', xmltodict.parse(result)['get_report_formats_response'], 1, 20, 'GET_REPORT_FORMATS_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_REPORT_FORMATS_FAILURE', None, 1, 1, e.__str__())

    def get_report_format(self, report_format_id):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_report_format(report_format_id=report_format_id)
            return create_result('GET_REPORT_FORMAT_SUCCESS', xmltodict.parse(result)['get_report_formats_response'], 1, 20, 'GET_REPORT_FORMAT_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_REPORT_FORMAT_FAILURE', None, 1, 1, e.__str__())

    #  ##############   PORT LISTS    ###########################
    def get_port_lists(self, request_args, **kwargs):
        arguments = get_pagination_filter(request_args)
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_port_lists(**arguments)
            return create_result('GET_PORT_LISTS_SUCCESS', xmltodict.parse(result)['get_port_lists_response'], 1, 20, 'GET_PORT_LISTS_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_PORT_LISTS_FAILURE', None, 1, 1, e.__str__())

    def get_port_list(self, port_list_id):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_port_list(port_list_id=port_list_id)
            return create_result('GET_PORT_LIST_SUCCESS', xmltodict.parse(result)['get_port_lists_response'], 1, 20, 'GET_PORT_LIST_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_PORT_LIST_FAILURE', None, 1, 1, e.__str__())

    #  ##############   CONFIGURATIONS    ###########################
    def get_configs(self, request_args, **kwargs):
        arguments = get_pagination_filter(request_args)
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            # result = _gvm.get_configs(**arguments)
            result = _gvm.get_configs()
            print('-------------------', result)
            return create_result('GET_CONFIGS_SUCCESS', xmltodict.parse(result)['get_configs_response'], 1, 20, 'GET_CONFIGS_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_CONFIGS_FAILURE', None, 1, 1, e.__str__())

    def get_config(self, config_id, **kwargs):
        try:
            _gvm = self.get_gvm()
            assert _gvm is not None, dmsg('') + 'Func: ' + func_name() + ' GMP is None '
            result = _gvm.get_config(config_id)
            _gvm.modify_config_set_nvt_selection()
            return create_result('GET_CONFIG_SUCCESS', xmltodict.parse(result)['get_configs_response'], 1, 20, 'GET_CONFIG_SUCCESS')
        except Exception as e:
            print('An error occurred', e, file=sys.stderr)
            # logging.error('An error occurred: ' + e.__str__())
            log.exception(dmsg('') + 'An error occurred: ' + e.__str__())
            return create_result('GET_CONFIG_FAILURE', None, 1, 1, e.__str__())
