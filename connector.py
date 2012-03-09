# -*- coding: utf8 -*-
import json
import elFinder
from pyramid.response import Response
from cgi import FieldStorage

#connector opts
_opts = {
	#'root' and url rewrite from ini file
	'root': '/tmp',
	'URL': 'http://localhost:8080/static/uploaded',
	## other options
	'debug': True,
	'fileURL': True,  # download files using connector, no direct urls to files
	# 'dirSize': True,
	# 'dotFiles': True,
	'fileMode': 0666,
	'dirMode': 0777,
	# 'uploadDeny': ['image', 'application'],
	# 'uploadAllow': ['image/png', 'image/jpeg'],
	# 'uploadOrder': ['deny', 'allow']
}

def connector(request):
    # init connector and pass options
    elf = elFinder.connector(request.registry.elfinder_options)
    
    # fetch only needed GET/POST parameters
    httpRequest = {}
    #form = cgi.FieldStorage()
    form=request.params
    for field in elf.httpAllowedParameters:
        if field in form:
            # Russiam hack
            if field == 'name':
                httpRequest[field] = form.getone(field).encode('utf-8')

            elif field == 'targets[]':
                #httpRequest[field] = form.getlist(field)
                httpRequest[field] = form.getall(field)

            # handle CGI upload
            elif field == 'upload[]':
                upFiles = {}
                cgiUploadFiles = form.getall(field)
                #if not isinstance(cgiUploadFiles, list):
                #    cgiUploadFiles = [cgiUploadFiles]
                for up in cgiUploadFiles:
                    #if hasattr(up, 'file') and hasattr(up, 'filename')
                    if isinstance(up, FieldStorage):
                        upFiles[up.filename.encode('utf-8')] = up.file # pack dict(filename: filedescriptor)
                httpRequest[field] = upFiles
            else:
                httpRequest[field] = form.getone(field)

    # run connector with parameters
    status, header, response = elf.run(httpRequest)

    # get connector output and print it out

    # code below is tested with apache only (maybe other server need other method?)

    #if len(header) >= 1:
    #    for h, v in header.iteritems():
    #        print h + ': ' + v
    #    print
    result=Response(status=status)
    try:
        del header['Connection']
    except:
        pass
    result.headers=header
    #print result.content_type

    if not response is None and status == 200:
        # send file
        if 'file' in response and isinstance(response['file'], file):
            #print "debuuuuuuggggg file"
            #print response['file'].read()
            result.body=response['file'].read()
            response['file'].close()

        # output json
        else:
            #print json.dumps(response, indent = True)
            result.body=json.dumps(response)
    return result

def includeme(config):

    _opts['root']=config.registry.settings['elfinder_root']
    _opts['URL']=config.registry.settings['elfinder_url']

    config.registry.elfinder_options=_opts

    config.add_route('connector', '/connector')
    config.add_view(connector,route_name='connector')
