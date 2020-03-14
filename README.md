[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/oeway/pyramid_elfinder/master)

# Jupyter elFinder

A web file browser for managing data on remote jupyter servers, specifically built for the [ImJoy](https://imjoy.io) project, an open source platform for deploying computational tools to the end user.

The frontend is built with [elFinder](https://github.com/Studio-42/elfinder) and a Python backend server.

## What is elFinder?

elFinder is an open-source file manager for web, written in JavaScript using jQuery and jQuery UI, [the project](https://github.com/Studio-42/elfinder) is maintained by [Studio 42](https://github.com/Studio-42). 

[Try their online demo here](https://studio-42.github.io/elFinder/).


## Installation

```sh
pip install -U jupyter-elfinder
```

## Basic Usage

```sh
jupyter-elfinder
```

You will then see the following message:

```sh
==========Jupyter elFinder server is running=========
http://127.0.0.1:8765
```

By default, it will browse the example data folder. In order to browse your own directory, you can set it by passing `--root-dir=/PATH/TO/MY/FOLDER`.


![jupyter-elfinder-screenshot](example-data/jupyter-elfinder-screenshot.png)

## Use it with remote Jupyter notebook server

If you don't have jupyter notebook, run:

```sh
pip install -U jupyter
```

Next, install jupyter server proxy:

```sh
pip install -U jupyter-server-proxy
```

Now start Jupyter notebook:

```sh
jupyter notebook --ip=0.0.0.0
```

You should then go to `http://YOUR_NOTEBOOK_URL/elfinder` (depending on what you get from your notebook, for example, the url can be `http://localhost:8000/elfinder`).

## Try it on MyBinder

1. Start an instance on MyBinder: https://mybinder.org/v2/gh/oeway/pyramid_elfinder/master

2. Get the URL and add `/elFinder` after, make sure you have something like `https://hub.gke.mybinder.org/user/oeway-pyramid_elfinder-q2q1dhbn/elFinder`

3. You should be able to see a file browser.


## License

MIT
