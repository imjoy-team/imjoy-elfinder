connector.py
------------
| This is conector for elfinder file manager, written for pyramid framework.
| Based on original https://github.com/Studio-42/elfinder-python/blob/master/connector.py
| For work you also need https://github.com/Studio-42/elfinder-python/blob/master/elFinder.py

How to try it:
--------------
In your virtualenv run:
```
git clone git://github.com/aleksandr-rakov/elfinder-pyramid.git
cd elfinder-pyramid/elfinder_pyramid_example/
python setup.py develop
pserve development.ini
```

And open http://127.0.0.1:6543/ in your browser.
Done!

Install:
--------
add to config:

    config.include('pyramid_elfinder.connector')

goto http://localhost:6543/elfinder/

TinyMCE:
--------

    <script src="//tinymce.cachefly.net/4.0/tinymce.min.js"></script>
    {% include 'elfinder/tinymce.jinja2' %}
    <script>
      tinymce.init({
        selector:'textarea.tinymce',
        browser_spellcheck : true,
        content_css: ["/static_norm/css/tu.css", "/static_norm/css/mytiny.css"],
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
-------------
- This connector support only v.1 protocol
- requires PIL for thumbnail generator
