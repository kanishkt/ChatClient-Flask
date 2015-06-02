from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from gevent import monkey
from werkzeug.utils import secure_filename
from login import create_app
from setup import app
import os
from flask_user import login_required
from socketio.server import SocketIOServer
from werkzeug.wsgi import SharedDataMiddleware

from flask import Flask, Response, request, render_template, url_for, redirect
from chat_models import ChatRoom, get_object_or_404, get_or_create, init_db

monkey.patch_all()
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

'''
Route to Display all the available chat rooms
'''
@app.route('/chat')
@login_required
def rooms():
    context = {"rooms": ChatRoom.query.all()}
    return render_template('rooms.html', **context)
'''
Route to Display the selected room or return an error
'''
@app.route('/chat/<path:slug>')
def room(slug):
    context = {"room": get_object_or_404(ChatRoom, slug=slug)}
    return render_template('room.html', **context)


'''
Function to check if the file is in the desired format
'''
def is_valid_filename(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

'''
Route to save the input file using FLask-Upload
'''
@app.route('/upload_image', methods='POST')
def upload_file(slug):
    file = request.files['file']
    if file and is_valid_filename(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        context = {"room": get_object_or_404(ChatRoom, slug=slug)}
        return redirect('/chat/<path:slug>')
    return ''

'''
Route to handle post from the "Add room" form on the homepage, and redirect to the new room.
'''
@app.route('/create', methods=['POST'])
def create():
    name = request.form.get("name")
    if name:
        room, created = get_or_create(ChatRoom, name=name)
        return redirect(url_for('room', slug=room.slug))
    return redirect(url_for('rooms'))

'''
Class to define various sockets for socket.io
'''
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    nicknames = []

    def initialize(self):
        self.logger = app.logger
        self.log("Socketio session started")

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_join(self, room):
        self.room = room
        self.join(room)
        return True

    def on_nickname(self, nickname):
        self.log('Nickname: {0}'.format(nickname))
        self.nicknames.append(nickname)
        self.session['nickname'] = nickname
        self.broadcast_event('announcement', '%s has connected' % nickname)
        self.broadcast_event('nicknames', self.nicknames)
        return True, nickname

    def recv_disconnect(self):
        # Remove nickname from the list.
        self.log('Disconnected')
        nickname = self.session['nickname']
        self.nicknames.remove(nickname)
        self.broadcast_event('announcement', '%s has disconnected' % nickname)
        self.broadcast_event('nicknames', self.nicknames)
        self.disconnect(silent=True)
        return True

    def on_user_message(self, msg):
        self.log('User message: {0}'.format(msg))
        self.emit_to_room(self.room, 'msg_to_room',
                          self.session['nickname'], msg)
        return True

    def on_user_image(self, url):
        self.emit_to_room(self.room, 'user_image',
                          self.session['nickname'], url)
        return True


@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'/chat': ChatNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()

'''
Start development web server
'''
if __name__ == '__main__':
    create_app()
    init_db()
    ap = SharedDataMiddleware(app, {'/': os.path.join(os.path.dirname(__file__), 'static')})
    SocketIOServer(('0.0.0.0', 5000), ap,
                   namespace="socket.io", policy_server=False).serve_forever()
    app.run(debug=True)