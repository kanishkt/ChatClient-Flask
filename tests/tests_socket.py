from unittest import TestCase, main

from socketio.namespace import BaseNamespace
from socketio.virtsocket import Socket


class SocketIOServer(object):
    def __init__(self, *args, **kwargs):
        self.sockets = {}

    def get_socket(self, socket_id=''):
        return self.sockets.get(socket_id)


class SocketIOhandler(object):
    def __init__(self, *args, **kwargs):
        self.server = SocketIOServer()


class Namespace(BaseNamespace):
    """Mock a Namespace from the namespace module"""
    pass


class TestSocketAPI(TestCase):
    """Test the virtual Socket object"""

    def setUp(self):
        self.server = SocketIOServer()
        self.virtsocket = Socket(self.server, {})

    def test__set_namespaces(self):
        namespaces = {'/': Namespace}
        self.virtsocket._set_namespaces(namespaces)
        self.assertEqual(self.virtsocket.namespaces, namespaces)

    def test__set_request(self):
        request = {'test': 'a'}
        self.virtsocket._set_request(request)
        self.assertEqual(self.virtsocket.request, request)

    def test__set_environ(self):
        environ = []
        self.virtsocket._set_environ(environ)
        self.assertEqual(self.virtsocket.environ, environ)

    def test_connected_property(self):
        # not connected
        self.assertFalse(self.virtsocket.connected)

        # connected
        self.virtsocket.state = "CONNECTED"
        self.assertTrue(self.virtsocket.connected)

    def test_incr_hist(self):
        self.virtsocket.state = "CONNECTED"

        # cause a hit
        self.virtsocket.incr_hits()
        self.assertEqual(self.virtsocket.hits, 1)
        self.assertEqual(self.virtsocket.state, self.virtsocket.STATE_CONNECTED)

    def test_disconnect(self):
        # kill connected socket
        self.virtsocket.state = "CONNECTED"
        self.virtsocket.active_ns = {'test' : Namespace({'socketio': self.virtsocket}, 'test')}
        self.virtsocket.disconnect()
        self.assertEqual(self.virtsocket.state, "DISCONNECTING")
        self.assertEqual(self.virtsocket.active_ns, {})

    def test_kill(self):
        # kill connected socket
        self.virtsocket.state = "CONNECTED"
        self.virtsocket.active_ns = {'test' : Namespace({'socketio': self.virtsocket}, 'test')}
        self.virtsocket.kill()
        self.assertEqual(self.virtsocket.state, "DISCONNECTING")


if __name__ == '__main__':
    main()