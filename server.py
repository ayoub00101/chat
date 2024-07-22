import flask
import flask_socketio as fs

app = flask.Flask(__name__)
app.secret_key = "supersecretkey"
socketio = fs.SocketIO(app)
users = []
messages = []

@app.route("/")
def home():
    return flask.render_template("home.html")

@app.route("/chat/<username>")
def chat(username):
    username = username.lower().strip()
    if username not in users:
        flask.flash("Nom d'utilsateur non valide ou non connecté.")
        return flask.redirect(flask.url_for("home"))
    return flask.render_template("chat.html", username=username)

@app.route("/submit", methods=["POST"])
def new_user():
    username = flask.request.form.get("username").lower().strip()
    if not username:
        flask.flash("Le nom d'utilisateur est requis.")
        return flask.redirect(flask.url_for("home"))
    elif username in users:
        flask.flash("Ce nom est déjà utilisé par un utilisateur en ligne. Veuillez réessayer.")
        return flask.redirect(flask.url_for("home"))
    users.append(username)
    socketio.emit("send_message",f'<span style="color:red;">{username}</span> est arrivé(e)', room=None)
    return flask.redirect(flask.url_for("chat", username=username))

@socketio.on("receive_message")
def resend(data):
    print("Message reçu.")
    print(data)
    username,message = data["username"],data["message"]

    to_send = f'<span style="color:red;">{username}</span>: {message}'
    if messages:
        if messages[-1][0] == username:
            to_send = message
    messages.append((username,message))
    fs.emit("send_message", to_send, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
