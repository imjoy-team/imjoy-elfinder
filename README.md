# elFinder connector for Jupyter server proxy

This elFinder is specifically built for the [ImJoy](https://imjoy.io) project, an open source platform for deploying computational tools to the end user.

## What is elFinder

elFinder is an Open-source file manager for the web, written in JavaScript using jQuery and jQuery UI, [the project](https://github.com/Studio-42/elfinder) is maintained by [Studio 42](https://github.com/Studio-42).

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

## License

MIT
