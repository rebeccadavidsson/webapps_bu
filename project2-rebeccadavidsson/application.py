import os
import time

from flask import Flask, session, render_template, request, redirect, flash, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"

socketio = SocketIO(app)
Session(app)

# Create global variable for all channels
channels = []
messages = {}

@app.route("/")
def index():
    """Open home page."""

    # Check to see if user was already logged in
    try:
        current_channel = session["current_channel"]
    except:
        current_channel = None

    # If user had already logged in, render page for chat with channels
    try:
        return render_template("home.html", username=session["username"],
                        channels=channels, current_channel=current_channel)
    except:
        return render_template("home.html", username=None)


@app.route("/username", methods=["POST"])
def username():
    """Check for username and remember in session."""

    username = request.form.get("username")

    # Check for errors
    if username:
        session["username"] = username
        return jsonify({"succes": True, "username": username})
    else:
        return jsonify({"succes": False})

@socketio.on("createchannel")
def createchannel(channel):
    """Create new channel and its environment with messages."""

    # Check if this channelname is already in channelslist
    if channel in channels:

        # Check if there were messages in this room.
        try:
            data = {"channel": channel, "messages": messages[channel],
                    "allchannels": channels, "add": False}
        except KeyError:
            data = {"channel": channel, "messages": None,
                    "allchannels": channels, "add": False}

        # Leave old channel and remember new one
        leave_room(session["current_channel"])
        session["current_channel"] = channel

        # Add user to the current channel
        join_room(channel)

        emit("join_channel", data)
    else:
        # Add new channel to list of all channels
        channels.append(channel)

        # Remember current channel in session for later use
        session["current_channel"] = channel

        # Create empty messages environment for this room
        messages[channel] = []

        # Add user to the current channel
        join_room(channel)

        data = {"channel": channel, "messages": messages[channel],
                "allchannels": channels, "add": True}

        # Make new channel and join this channel
        emit("join_channel", data, broadcast=True)



@socketio.on("new_message")
def new_message(data):
    """Emit a new message into data."""

    # Update messages in this channel
    dict = {"username": session["username"], "message": data["message"],
            "time": time.ctime(time.time())}
    messages[data["channel"]].append(dict)

    # Ensure a maximum of 100 messages for a channel.
    if len(messages[data["channel"]]) >= 100:
        messages[data["channel"]].pop(0)

    emit("push_message", dict, room=data["channel"])


@socketio.on("join_channel")
def join_channel(channel):
    """Let user view messages in specific channel"""

    # If this is the first channel, force add to list of channels.
    # Other new channels are added by "create channel" function.
    if channels == []:
        channels.append(channel)
        messages[channel] = []
        first = True
    else:
        first = False
        # leave_room(session["current_channel"])

    session["current_channel"] = channel

    # Use flask_socketio's function to join a room
    # Used to send messages to a room
    join_room(channel)

    # Check if there are messages in this channel
    try:
        data = {"channel": channel, "messages": messages[channel],
            "allchannels": channels, "first": first, "add": True}
    except KeyError:
        data = {"channel": channel, "messages": None,
            "allchannels": channels, "first": first, "add": True}

    # Emit socketio function (defined in javascript)
    emit("join_channel", data, broadcast=False)



@app.route('/logout', methods=['POST'])
def logout():
    """Log out user"""
    session.clear()
    return redirect("/")


# Alternative to FLASK_DEBUG in 'flask run'; run with python appliation.py
if __name__ == '__main__':
    socketio.run(app, use_reloader=True)
