from pyramid.view import view_config

@view_config(route_name='home', renderer='files.html')
def my_view(request):
    return {}

@view_config(route_name='home-ru', renderer='files.html')
def my_view_ru(request):
    return {'mode':'ru'}
