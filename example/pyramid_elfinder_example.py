import os

from pyramid.config import Configurator
from pyramid_elfinder import PYRAMID_ELFINDER_FILEBROWSER


def main(global_settings, **settings):
    config = Configurator(
        settings=settings,
    )
    config.include('pyramid_elfinder')
    config.add_static_view('static', 'static')
    config.add_route(PYRAMID_ELFINDER_FILEBROWSER, '/')
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
    httpd.serve_forever()
