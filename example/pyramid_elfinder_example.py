import os

from pyramid.config import Configurator
from pyramid_elfinder import PYRAMID_ELFINDER_FILEBROWSER
from pyramid.events import NewRequest

def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
        })
    event.request.add_response_callback(cors_headers)

def main(global_settings, **settings):
    config = Configurator(
        settings=settings,
    )
    config.include('pyramid_elfinder')
    config.add_static_view('static', 'static')
    config.add_route(PYRAMID_ELFINDER_FILEBROWSER, '/')
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)
    return config.make_wsgi_app()


if __name__ == '__main__':
    here = os.path.dirname(os.path.realpath(__file__))
    uploads = os.path.join(here, 'static', 'uploads')
    settings = {
        'pyramid_elfinder_root': uploads,
        'pyramid_elfinder_url': '/static/uploads/'
    }
    app = main({}, **settings)

    from wsgiref.simple_server import make_server
    httpd = make_server('0.0.0.0', 6543, app)
    print('==========Server for ElFinder is Running=========\nhttp://127.0.0.1:6543\n')
    httpd.serve_forever()
