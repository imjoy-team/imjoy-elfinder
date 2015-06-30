"""
orignal file
https://github.com/Studio-42/elfinder-python/blob/master/connector.py changed
by Alexandr Rakov 08-03-2012
"""


def includeme(config):
    config.include('.routes')
    config.include('.assets')
    config.scan('.views')
    config.add_view(lambda x: {},
                    route_name='elfinder',
                    renderer='templates/elfinder/filebrowser.jinja2')
