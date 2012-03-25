from pyramid.config import Configurator

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_renderer(".html", "pyramid.mako_templating.renderer_factory")
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('home-ru', '/ru')
    config.include('elfinder_pyramid_example.connector')
    config.scan()
    return config.make_wsgi_app()
