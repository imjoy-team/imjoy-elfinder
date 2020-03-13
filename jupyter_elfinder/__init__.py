"""
orignal file
https://github.com/Studio-42/elfinder-python/blob/master/connector.py changed
by Alexandr Rakov 08-03-2012
"""

JUPYTER_ELFINDER_CONNECTOR = "jupyter_elfinder_connector"
JUPYTER_ELFINDER_FILEBROWSER = "jupyter_elfinder_filebrowser"


def includeme(config):
    config.include(".routes")
    config.include(".assets")
    config.scan(".views")
