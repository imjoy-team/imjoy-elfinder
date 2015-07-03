"""
orignal file
https://github.com/Studio-42/elfinder-python/blob/master/connector.py changed
by Alexandr Rakov 08-03-2012
"""

PYRAMID_ELFINDER_CONNECTOR = 'pyramid_elfinder_connector'
PYRAMID_ELFINDER_FILEBROWSER = 'pyramid_elfinder_filebrowser'


def includeme(config):
    config.include('.routes')
    config.include('.assets')
    config.scan('.views')
