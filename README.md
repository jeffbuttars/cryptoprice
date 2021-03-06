# Cryptoprice

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
our settings module for use by the `App`. We also setup a basic root logger here. If debug/dev mode
is detected then we'll log the app specific routes, settings and components at start up.

The components we build and use in this app are:

* [aioclient](src/aioclient/client.py) for performing HTTP client call asynchronously

### [settings.py](src/settings.py)

This is fairly simple, mostly it just maps environmental values into our settings.
We add and override some default settings for template searching and override the
`RENDERERS` setting to use our own [src/local_utils/renderer.py](JSONRenderer) for
our endpoints.


## Custom Asynchronous Backends

#### Asyncio and component initialization
These backends are [API Star Components](https://github.com/encode/apistar#components) and it's
important to note that **components are registered and preloaded(initialized) before the App's IOLoop
is started**. This will cause problems if you try get an IOLoop and create connections on component
Initialization. For instance, if the Redis component gets the IOLoop and uses it to create a
connection pool at initialization. It's connection pool will be on a different IOLoop than what the Redis client
calls will come from, which is an error.
This is because components are register and preloaded(by default)
before the App's IOLoop is created and started. Because of this, components that need connection
pools or connections to other services make those connections lazily as needed by client requests.
This is not as elegant as beging able to initialize components after the App's IOLoop is created
and then have access to that IOLoop, but is necessary for now.

### Redis
The redis module defines a [Component](https://github.com/encode/apistar#components) and a [Command](https://github.com/encode/apistar#command-routing)

The command available is `redis_cli` and will open the Redis CLI using the App's settings.

```bash
$ ./app.py redis_cli
[::1]:6379>
```

### Postgresql
The asyncpg module defines a [Component](https://github.com/encode/apistar#components) and a [Command](https://github.com/encode/apistar#command-routing)

The command available is `dbshell` and will run `psql` with the App's connection settings.

```bash
$ ./app.py dbshell
psql (10.1)
Type "help" for help.

cryptoprice=#
```

## Aioclient component

## The Slack Bot

## A Very Basic Database Script
