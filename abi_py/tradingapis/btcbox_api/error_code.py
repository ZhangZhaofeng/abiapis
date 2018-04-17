

def error_parser(json_dict):
    if isinstance(json_dict, dict):
        if  'result' in json_dict:
            if json_dict['result'] == False:
                code = str(json_dict['code'])
                contents = ERROR_CODES[code] if code in ERROR_CODES else 'unknown error'
                message = 'error code:' + code + ' content: ' + contents
                raise Exception(message)
    else:
        message = 'unkonwn error'
        raise Exception(message)


ERROR_CODES = {
    '100': 'need parameters',
'101' : 'useless parameters',
'102' :'coin not exist',
'103': 'key not exist',
'104': 'key not match secret',
'105': 'not authorized',
'106' :  'expired',
'107' :'need integer price',
'200' : 'no balance',
'201' :'too small',
'202' :'price need be set as 1-1000000',
'203' : 'no order',
'301' : 'no verified',
'401' :'system error',
'402' : 'too many request',
'403' : 'not an open api',
'404' :'IP is not allowed'
}