|Build Status| |Coveralls| |Stories in Ready|

Forked from `elfinder-pyramid`_ writed by `Aleksandr Rakov`_

connector.py
------------

This is conector for elfinder file manager, written for pyramid
framework. Based on original
https://github.com/Studio-42/elfinder-python/blob/master/connector.py
and https://github.com/Studio-42/elfinder-python/blob/master/elFinder.py

Now you can find connector there http://github.com/ITCase/elfinder

How to try it:
--------------

In your virtualenv run:

.. code-block:: bash

    $ git clone https://github.com/ITCase/pyramid_elfinder.git
    $ cd pyramid_elfinder/example
    $ python pyramid_elfinder_example.py

And open http://127.0.0.1:6543/ in your browser. Done!

Install to app:
---------------

add to config:

::

    config.include('pyramid_elfinder')

goto http://localhost:6543/elfinder/

TinyMCE:
--------

.. code-block:: html

    <script src="//tinymce.cachefly.net/4.0/tinymce.min.js"></script>
    {% include 'elfinder/tinymce.jinja2' %}
    <script>
      tinymce.init({
        selector:'textarea.tinymce',
        browser_spellcheck : true,
        content_css: ["/static_extra/css/tu.css", "/static_extra/css/mytiny.css"],
        plugins: "image link code contextmenu fullpage fullscreen "+
                "hr insertdatetime lists media paste preview "+
                "print table textcolor "+
                "visualchars wordcount",
        toolbar1: "fullpage preview print forecolor backcolor inserttable",
        toolbar2: "styleselect formatselect fontselect fontsizeselect cut copy paste  removeformat subscript superscript",
        toolbar3: "undo redo | bold italic underline strikethrough | bullist numlist outdent indent blockquote | alignleft aligncenter alignright alignjustify |",
        file_browser_callback: elFinderBrowser,
      });
    </script>
    <textarea class="tinymce"></textarea>


Notes:
------

-  This connector support only v.1 protocol
-  requires PIL for thumbnail generator

.. _elfinder-pyramid: http://github.com/aleksandr-rakov/elfinder-pyramid
.. _Aleksandr Rakov: http://github.com/aleksandr-rakov
.. |Stories in Ready| image:: https://badge.waffle.io/itcase/pyramid_elfinder.png?label=ready&title=Ready
   :target: https://waffle.io/itcase/pyramid_elfinder
.. |Build Status| image:: https://travis-ci.org/ITCase/pyramid_elfinder.svg?branch=master
   :target: https://travis-ci.org/ITCase/pyramid_elfinder
.. |Coveralls| image:: https://coveralls.io/repos/ITCase/pyramid_elfinder/badge.png
  :target: https://coveralls.io/r/ITCase/pyramid_elfinder

