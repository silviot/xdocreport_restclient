import requests
import json


def invoke_service(template, data, data_type, template_engine):
    url = 'http://127.0.0.1:8080/jaxrs/report'
    data = {
        'dataType': data_type.upper(),
        'data': json.dumps(data),
        'templateEngineKind': template_engine,
        'outFileName': 'out',
    }
    files = {'templateDocument': template}
    result = requests.post(url, data, files=files)
    if result.status_code / 100 != 2:
        raise RuntimeError
    return result.content
