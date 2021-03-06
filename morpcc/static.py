from .app import App
from webob import static
from webob.exc import HTTPNotFound, HTTPUnauthorized, HTTPNotModified
from pkg_resources import resource_filename
import os
import hashlib
from datetime import datetime, timedelta
import morepath

ETAG = hashlib.md5(datetime.now().strftime(
    r'%Y%d%d%H').encode('ascii')).hexdigest()


class StaticRoot(object):

    module = 'morpcc'
    directory = 'static_files'

    def __init__(self, path):
        self.path = path or ''

    def resource_path(self):
        if not self.path.strip():
            return None
        d = resource_filename(self.module, self.directory)
        return os.path.join(d, self.path)


@App.path(model=StaticRoot, path='/__static__/morpcc', absorb=True)
def get_staticroot(absorb):
    return StaticRoot(absorb)


@App.view(model=StaticRoot)
def serve_static(context, request):
    path = context.resource_path()
    if not path:
        raise HTTPNotFound()

    settings = request.app.settings.__dict__
    max_age = int(settings.get(
        'caching', {}).get('max-age', (60*60)))

    etag = request.headers.get('If-None-Match', '')

    def add_headers(response):
        response.headers.add('Cache-Control', 'public, max-age=%s' % max_age)
        response.headers.add('Expires', (
            datetime.utcnow() +
            timedelta(seconds=max_age)).strftime(r'%a, %d %b %Y %H:%M:%S GMT'))
        response.headers.add('ETag', ETAG)

    if etag and etag == ETAG:
        @request.after
        def add_notmodified_headers(response):
            add_headers(response)

        return morepath.Response(status=304)

    resp = request.get_response(static.FileApp(path))
    if resp.status_code == 404:
        raise HTTPNotFound()
    if resp.status_code == 403:
        raise HTTPUnauthorized()

    @request.after
    def add_caching_headers(response):
        add_headers(response)
    return resp


class DeformStaticRoot(StaticRoot):

    module = 'deform'
    directory = 'static'


@App.path(model=DeformStaticRoot, path='/__static__/deform', absorb=True)
def get_deformstaticroot(absorb):
    return DeformStaticRoot(absorb)
