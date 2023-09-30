import json
from app_logger.logger import MyLogger


def get_main_logger(name=__name__):
    return MyLogger(logger_name=name).get_logger()


log = get_main_logger('utils.py')


def create_result(result_, items, page: int = 1, items_per_page: int = 1, more: str = "", status_code: str = '0'):
    temp = {"page": page,
            "page_size": items_per_page,
            "status_code": status_code,
            "result": '',
            "more": more,
            "items": []}

    if (result_ is not None) and (result_ != ''):
        temp['result'] = result_
    else:
        temp['result'] = ''
    if items is not None:
        # print(items)
        if items.get('@status') is not None:
            temp['status_code'] = items.get('@status')
        else:
            temp['status_code'] = "422"
        for i in items:
            temp['items'] = items

    else:
        temp['items'] = []
    return temp


def getPagination(page_nb, items_per_page):
    offset = 0
    try:
        if (page_nb is not None) and (items_per_page is not None):
            assert isinstance(page_nb, int), '"page_nb" should be of type int'
            assert isinstance(items_per_page, int), '"items_per_page" should be of type int'

            if page_nb > 0:
                offset = (page_nb - 1) * items_per_page
            else:
                offset = items_per_page
            return offset
        else:
            return offset
    except Exception as e:
        # logger.error("Either page_nb or items_per_page is Null " + e.__str__())
        log.exception(dmsg('') + "Either page_nb or items_per_page is Null " + e.__str__())
        return offset


def checkpayload(payload, *args):
    if len(payload) > 0:
        return True
    else:
        return False


def checkKeys(payload, *args):
    i = None
    result = False
    if checkpayload(payload):
        for i in args:
            if i in payload:
                result = True
            else:
                result = False
                # logging.error('one of the payload keys was invalid: ' + i)
                log.exception(dmsg('') + 'one of the payload keys was invalid: ' + i)
                break
        return result
    else:
        # logging.error('payload was empty')
        log.exception(dmsg('') + 'payload was empty')
        return False


def checkValues(payload, *args):
    i = None
    result = False
    # print(payload.get('initiatorID'))
    if checkpayload(payload):
        for i in args:
            if (payload.get(i) is not None) and (payload.get(i) != ''):
                result = True
            else:
                result = False
                # logging.error('payload value is either None or empty: ' + i)
                log.exception(dmsg('') + 'payload value is either None or empty: ' + i)
                break
        return result
    else:
        # logging.error('payload was empty')
        log.exception(dmsg('') + 'payload was empty')
        return False


def dmsg(text_s):
    import inspect
    import os
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename
    filename = os.path.splitext(os.path.basename(caller_filename))[0]
    return filename + '.py:' + str(inspect.currentframe().f_back.f_lineno) + '| ' + text_s


def get_pagination_filter(request_arguments):
    arguments = {
        "filter": "first=%s rows=%s sort=%s" % (request_arguments.get('first') if request_arguments.get('first') else 1,
                                                request_arguments.get('rows') if request_arguments.get('rows') else 100,
                                                request_arguments.get('sort') if request_arguments.get('sort') else 'name')
    }
    return arguments


def func_name():
    import inspect
    return inspect.stack()[1][3].upper()
