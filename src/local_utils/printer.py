import logging
from pprint import pformat


logger = logging.getLogger(__name__)


def print_include(include, printer):
    print_routes(include.routes, printer)


def print_route(route, printer):
    printer(f"Route: {route.method:<6} {route.path:<16}{route.name} {route.view}")


def print_routes(routes, printer=None):
    printer = printer or logger.debug

    for route in routes:
        if hasattr(route, 'routes'):
            print_include(route, printer)
        else:
            print_route(route, printer)


def print_settings(settings, printer=None):
    printer = printer or logger.debug

    printer("Settings:\n%s", pformat(settings))


def print_components(components, printer=None):
    printer = printer or logger.debug

    printer("Components:")

    for comp in components:
        s = f" preload: {str(comp.preload):<5} init: {comp.init}"

        if hasattr(comp, 'cls'):
            printer(f"  {comp.cls.__name__:<16}{s}")
        else:
            printer(f"  {comp:<16}{s}")
