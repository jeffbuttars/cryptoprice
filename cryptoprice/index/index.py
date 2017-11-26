import logging
from apistar import Route, annotate, render_template
from apistar.renderers import HTMLRenderer


logger = logging.getLogger(__name__)


@annotate(renderers=[HTMLRenderer()])
def index(name: str=''):
    logger.debug("INDEX %s", name)
    return render_template('index.html', name=name)


routes = [
    Route('/{name}', 'GET', index, name='index-named'),
    Route('/', 'GET', index, name='index'),
]
