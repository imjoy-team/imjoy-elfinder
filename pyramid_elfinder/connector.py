# -*- coding: utf8 -*-
# orignal file https://github.com/Studio-42/elfinder-python/blob/master/connector.py
# changed by Alexandr Rakov 08-03-2012

import json
import elFinder
from cgi import FieldStorage
from pyramid.response import Response

# connector opts
_opts = {
    # 'root' and url rewrite from ini file
    'root': '/tmp',
    'URL': 'http://localhost:6543/static/uploaded',
    # other options
    'debug': True,
    # if False: download files using connector, no direct urls to files
    'fileURL': True,
    # 'dirSize': True,
    # 'dotFiles': True,
    'fileMode': 0666,
    'dirMode': 0777,
    # 'uploadDeny': ['image', 'application'],
    # 'uploadAllow': ['image/png', 'image/jpeg'],
    # 'uploadOrder': ['deny', 'allow']
}


# pymode:lint_ignore=C901
def connector(request):
    # init connector and pass options
    elf = elFinder.connector(_opts)

    # fetch only needed GET/POST parameters
    httpRequest = {}
    form = request.params
    for field in elf.httpAllowedParameters:
        if field in form:
            # Russian file names hack
            if field == 'name':
                httpRequest[field] = form.getone(field).encode('utf-8')

            elif field == 'targets[]':
                httpRequest[field] = form.getall(field)

            # handle CGI upload
            elif field == 'upload[]':
                upFiles = {}
                cgiUploadFiles = form.getall(field)
                for up in cgiUploadFiles:
                    if isinstance(up, FieldStorage):
                        # pack dict(filename: filedescriptor)
                        upFiles[up.filename.encode('utf-8')] = up.file
                httpRequest[field] = upFiles
            else:
                httpRequest[field] = form.getone(field)

    # run connector with parameters
    status, header, response = elf.run(httpRequest)

    # get connector output and print it out

    result = Response(status=status)
    try:
        del header['Connection']
    except:
        pass
    result.headers = header

    if not response is None and status == 200:
        # send file
        if 'file' in response and isinstance(response['file'], file):
            result.body = response['file'].read()
            response['file'].close()

        # output json
        else:
            result.body = json.dumps(response)
    return result


def includeme(config):
    _opts['root'] = config.registry.settings['elfinder_root']
    _opts['URL'] = config.registry.settings['elfinder_url']

    config.add_jinja2_search_path("pyramid_elfinder:templates")
    config.add_static_view('static_elfinder', 'pyramid_elfinder:static')

    config.add_route('connector', '/connector')
    config.add_route('elfinder', '/elfinder/')
    config.add_view(connector, route_name='connector')

    config.add_view(lambda x: {}, route_name='elfinder',
                    renderer='templates/elfinder/filebrowser.jinja2')
