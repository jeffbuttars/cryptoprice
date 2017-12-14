# Cryptoprice

A proof of concept project on building the basics for a fully asynchronous Python REST api with [API Star](https://github.com/encode/apistar).

## Install / Packaging / Pip
This project is built and managed with [Pipenv](https://docs.pipenv.org).
Make sure you have [Pipenv](https://docs.pipenv.org) installed on your system.

To create a virtualenv and install the project packages, from the proejct root directory:

For a production build environment:

    $ pipenv install


For a development build environment:

    $ pipenv install --dev


## TODO / Wish List
* Websocket example
* GraphQL endpoint
* Asynchronous SQLAlchemy usage instead of raw connection.

## Files

### [app.py](src/app.py)

This is the entry point of the application and is also the highest level of orchestration for your
[API Star](https://github.com/encode/apistar) app. This is where we import the libraries and app
specific modules that we'll use to construct the `App` instance.  

In this application, we have several custom components we need to register with the `App` and
our settings module for use by the `App`

### `settings.py`


## Custom Asynchronous Backends
### Redis
### Postgresql

## Aioclient component

## The Slack Bot

## A Very Basic Database Script
