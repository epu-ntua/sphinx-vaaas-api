import os, sys, platform
import time

from app_logger.logger import MyLogger
from utils.utils import *
from sanic import Sanic
from sanic.response import json as sanic_json
from sanic_cors import CORS, cross_origin
from GVM.gvm_manager import GvmManager
from config.config import get_config
import json as simple_json

# from sanic_openapi import swagger_blueprint

log = get_main_logger(__name__)

app = Sanic(__name__)
app.config['CORS_AUTOMATIC_OPTIONS'] = True
app.config['CORS_HEADERS'] = 'Content-Type,Authorization'
CORS(app)

# app.blueprint(swagger_blueprint)

service_config = get_config()

# gvm = GvmManager()
gvm = None


def setup_GVM_Manager():
    global gvm
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == 'dev':
                gvm = GvmManager(socket_path=service_config['GVM_DEV']['socket_path'], username=service_config['GVM_DEV']['username'], password=service_config['GVM_DEV']['password'])
                # logging.info('The VAaaS API Module is running in "development" mode!')
                log.info(dmsg('') + 'The VAaaS API Module is running in "development" mode!')
            elif sys.argv[1] == 'prod':
                gvm = GvmManager(socket_path=service_config['GVM_PROD']['socket_path'], username=service_config['GVM_PROD']['username'], password=service_config['GVM_PROD']['password'])
                # logging.info('The VAaaS API Module is running in "production" mode!')
                log.info(dmsg('') + 'The VAaaS API Module is running in "production" mode!')
            else:
                gvm = GvmManager(socket_path=service_config['GVM_DEV']['socket_path'], username=service_config['GVM_DEV']['username'], password=service_config['GVM_DEV']['password'])
                # logging.info('The VAaaS API Module is running in "development" mode!')
                log.info(dmsg('') + 'The VAaaS API Module is running in "development" mode!')
        else:
            gvm = GvmManager(socket_path=service_config['GVM_DEV']['socket_path'], username=service_config['GVM_DEV']['username'], password=service_config['GVM_DEV']['password'])
            # logging.info('The VAaaS API Module is running in "development" mode!')
            log.info(dmsg('') + 'The VAaaS API Module is running in "development" mode!')
        assert gvm is not None, "GVM initialization went south! gvm is None!!!!"
    except Exception as e:
        log.exception(dmsg('') + 'Something went wrong during GvmManager Initialization! -> ' + e.__str__(), 'error')


# def setup():
#     # Try to connect to VAAAS engine through SSH
#     success = False
#     while not success:
#         result = os.system('sshpass -p ' + service_config['GVM_DEV']['ssh_pass'] +
#                            ' ssh -o StreamLocalBindUnlink=yes -o StreamLocalBindMask=0111 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ' +
#                            '-f -nNT -L /vaaas/gvmd.sock:/usr/local/var/run/gvmd.sock '
#                            + service_config['GVM_DEV']['ssh_user'] + '@' + service_config['GVM_DEV']['docker'] + ' -p 2222')
#         _log(dmsg('') + " **************************************" + str(result) + " **************************************", 'debug')
#         if result == 0:
#             _log(dmsg('') + '-------------------------- Result is 0!', 'info')
#             success = True
#             setup_GVM_Manager()
#         else:
#             success = False
#         time.sleep(10)


root_path = '/api/v1'


@app.route(root_path + "/health")
@cross_origin(app)
async def health(request):
    # logging.debug("request: ", request.method)
    log.info(dmsg('') + "request: " + request.method)
    return sanic_json({"Response": "This is a health check for VAaaS API V1"}, status=200, content_type='application/json')


@app.route(root_path + "/version", methods=['GET', 'OPTIONS'])
@cross_origin(app)
async def version(request):
    # logging.debug("request: ", request.method)
    log.info(dmsg('') + "request: " + request.method)
    response = gvm.get_version()
    return sanic_json(response, status=int(response['status_code']), content_type='application/json')


#  ##############   TASKS    ###########################
@app.route(root_path + "/tasks", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(app)
async def tasks(request):
    try:
        if request.method == "GET":
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + "request: " + request.method)
            response = gvm.get_tasks(request.args)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        elif request.method == 'POST':
            print(request.body)
            payload = simple_json.loads(request.body)
            response = gvm.create_task(payload)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/tasks/<task_id:string>", methods=['GET', 'DELETE'])
@cross_origin(app)
async def task(request, task_id):
    try:
        if request.method == "GET":
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_task(task_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        elif request.method == 'DELETE':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.delete_task(task_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        elif request.method == 'PUT':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.update_task(task_id, request.body)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/tasks/<task_id:string>/start", methods=['GET'])
@cross_origin(app)
async def start_task(request, task_id):
    try:
        if request.method == "GET":
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.start_task(task_id=task_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/tasks/<task_id:string>/stop", methods=['GET'])
@cross_origin(app)
async def stop_task(request, task_id):
    try:
        if request.method == "GET":
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.stop_task(task_id=task_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/tasks/<task_id:string>/progress", methods=['GET'])
@cross_origin(app)
async def task_progress(request, task_id):
    try:
        if request.method == "GET":
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_task_progress(task_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


# ##############   SCANNERS    ###########################
@app.route(root_path + "/scanners")
@cross_origin(app)
async def scanners(request):
    try:
        if request.method == "GET":
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_scanners(request.args)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/scanners/<scanner_id:string>", methods=['GET', 'DELETE'])
@cross_origin(app)
async def scanner(request, scanner_id):
    try:
        if request.method == "GET":
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_scanner(scanner_id=scanner_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


#  ##############   TARGETS    ###########################
@app.route(root_path + "/targets", methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@cross_origin(app)
async def targets(request):
    try:
        if request.method == 'GET':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_targets(request.args)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        elif request.method == 'POST':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            payload = simple_json.loads(request.body)
            response = gvm.create_target(payload)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/targets/<target_id:string>", methods=['GET', 'PUT', 'DELETE'])
@cross_origin(app)
async def target(request, target_id):
    try:
        if request.method == 'GET':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_target(target_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        elif request.method == "DELETE":
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            # payload = simple_json.loads(request.body)
            response = gvm.delete_target(target_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        elif request.method == 'PUT':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            payload = simple_json.loads(request.body)
            response = gvm.update_target(target_id, payload)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


# ##############   REPORTS    ###########################
@app.route(root_path + "/reports", methods=['GET'])
@cross_origin(app)
async def reports(request):
    try:
        if request.method == 'GET':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_reports(request.args)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')

        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/reports/<report_id:string>", methods=['GET', 'POST', 'OPTIONS', 'DELETE'])
@cross_origin(app)
async def report(request, report_id):
    try:
        if request.method == 'GET':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_report(report_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        elif request.method == 'POST':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            payload = simple_json.loads(request.body)
            response = gvm.get_report_details(report_id, payload)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/reports/formats", methods=['GET'])
@cross_origin(app)
async def report_formats(request):
    try:
        if request.method == 'GET':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_report_formats(request.args)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/reports/formats/<report_format_id:string>", methods=['GET'])
@cross_origin(app)
async def report_formats(request, report_format_id):
    try:
        if request.method == 'GET':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_report_format(report_format_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


#  ##############   PORT LISTS    ###########################
@app.route(root_path + "/ports", methods=['GET'])
@cross_origin(app)
async def ports(request):
    try:
        if request.method == 'GET':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_port_lists(request.args)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/ports/<port_list_id:string>", methods=['GET'])
@cross_origin(app)
async def port(request, port_list_id):
    try:
        if request.method == 'GET':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_port_list(port_list_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


#  ##############   CONFIGS    ###########################
@app.route(root_path + "/configs", methods=['GET'])
@cross_origin(app)
async def configs(request):
    try:
        if request.method == 'GET':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_configs(request.args)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


@app.route(root_path + "/configs/<config_id:string>", methods=['GET'])
@cross_origin(app)
async def config(request, config_id):
    try:
        if request.method == 'GET':
            # logging.debug("request: ", request.method)
            log.info(dmsg('') + f"request: {request.method} -> {request.url}")
            response = gvm.get_config(config_id)
            return sanic_json(response, status=int(response['status_code']), content_type='application/json')
        else:
            response = create_result('This method is not allowed for this endpoint', None, 1, 1, 'METHOD NOT ALLOWED')
            return sanic_json(response, status=405, content_type='application/json')
    except Exception as e:
        response = create_result('Some error has occurred', None, 1, 1, e.__str__(), '404')
        return sanic_json(response, status=404, content_type='application/json')


if __name__ == "__main__":
    # logging.debug(platform.system())
    log.info(dmsg('') + "Platform: " + platform.system())
    # setup()
    setup_GVM_Manager()
    app.run(host="0.0.0.0", port=8000, debug=True, access_log=True)
