all: test

test:
	nosetests --with-coverage --cover-package jupyter_elfinder --cover-erase --with-doctest --nocapture

coverage: test
	coverage html
