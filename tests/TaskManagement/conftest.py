import threading

from twisted.internet import reactor
from twisted.web import resource, server, guard
from twisted.cred.portal import IRealm, Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse

from zope.interface import implementer


server_thread = None


# Start the local HTTP server before the tests start.
def pytest_configure(config):
    global server_thread
    server_thread = _runHttpServer()


# Stop the local HTTP server after the tests are done.
def pytest_unconfigure(config):
    global server_thread
    reactor.callLater(0, reactor.stop)
    server_thread.join()


#
# Run a local HTTP server for testing the HttpRequestManager.
# This server is accessible via http://localhost:8080/, and it has the following URL resources:
#  - /success  - This request will respond to a GET request normally with an HTML page.
#  - /timeout  - This request will respond to a GET request first with a few bytes and then do nothing.
#                It is intended to emulate a timeout.
#  - /auth     - Respond to GET requests and requires an authentication. You need to use Basic Auth with user:user as
#                the username and password to access this resource.
#
def _runHttpServer() -> "threading.Thread":
    class RootResource(resource.Resource):
        isLeaf = False

        def __init__(self):
            super().__init__()
            self._success = SuccessfulResource()
            self._timeout = TimeoutResource()

            checkers = [InMemoryUsernamePasswordDatabaseDontUse(user = b"user")]
            portal = Portal(SimpleRealm(), checkers)
            self._auth_resource = guard.HTTPAuthSessionWrapper(portal, [guard.BasicCredentialFactory("auth")])

        def getChild(self, name, request):
            if name == b"success":
                return self._success
            elif name == b"timeout":
                return self._timeout
            elif name == b"auth":
                return self._auth_resource
            return resource.Resource.getChild(self, name, request)

    # This resource can be accessed via /success. It will reply with an HTML page.
    class SuccessfulResource(resource.Resource):
        isLeaf = True

        def getChild(self, name, request):
            if name == b"":
                return self
            return resource.Resource.getChild(self, name, request)

        def render_GET(self, request):
            return "<html>Hello, world!</html>".encode("utf-8")

    # This resource can be accessed via /timeout. It will first send 3 replies, with 1 second between each. After that
    # It will not do anything to emulate a problem on the server side. This way we can test if the client side can
    # handle this case correctly, such as with a timeout.
    class TimeoutResource(resource.Resource):
        isLeaf = True

        def __init__(self):
            super().__init__()
            self._count = 0

        def getChild(self, name, request):
            if name == b"":
                return self
            return resource.Resource.getChild(self, name, request)

        def render_GET(self, request):
            self._process(request)
            return server.NOT_DONE_YET

        def _process(self, request):
            if self._count > 10:
                request.finish()

            if self._count == 3:
                # emulate a timeout by not replying anything
                return

            data = ("%s" % self._count) * 10
            request.write(data.encode("utf-8"))
            self._count += 1
            reactor.callLater(0.5, self._process, request)

    # A realm which gives out L{SuccessfulResource} instances for authenticated users.
    @implementer(IRealm)
    class SimpleRealm(object):
        def requestAvatar(self, avatar_id, mind, *interfaces):
            if resource.IResource in interfaces:
                return resource.IResource, SuccessfulResource(), lambda: None
            raise NotImplementedError()

    def _runServer():
        site = server.Site(RootResource())
        reactor.listenTCP(8080, site)
        reactor.run()

    t = threading.Thread(target = _runServer)
    t.start()
    return t
