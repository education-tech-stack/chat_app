from flask import Flask, jsonify, request
import os
import arrow

from database import Database
from conversation import Conversation

conversations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'conversation/'))

database = Database()

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/get_all_users')
def get_all_users():
    all_users = database.get_all_users()

    return jsonify(all_users)


@app.route('/add_user')
def add_user():
    data = request.form
    username = data['username']
    real_name = data['real_name']

    return jsonify('User Created')


@app.route('/user_exists', methods=['POST'])
def user_exists():
    username = request.form.get('username')
    exists = database.user_exists(username)

    return jsonify({'exists': exists})


def get_conversation_db_path_for_users(data):
    user_one = data['user_one']
    user_two = data['user_two']

    users_in_order = sorted([user_one, user_two])
    users_in_order = ' '.join(users_in_order)

    conversation_db = users_in_order + '.db'
    conversation_db_path = os.path.join(conversations_dir, conversation_db)

    return conversation_db_path


@app.route('/create_conversation_db', methods=['POST'])
def create_conversation_db():
    conversation_db_path = get_conversation_db_path_for_users(request.form)

    if not os.path.exists(conversation_db_path):
        conversation = Conversation(conversation_db_path)
        conversation.initialise_table()

    return jsonify({
        'success': True,
    })


@app.route('/get_message_history', methods=['POST'])
def get_message_history():
    conversation_db_path = get_conversation_db_path_for_users(request.form)
    conversation = Conversation(conversation_db_path)

    history = conversation.get_history()

    return jsonify({
        'history': history
    })


@app.route('/send_message/<username>', methods=['POST'])
def send_message(username):
    data = request.form
    author = data['author']
    message = data['message']
    date_sent = arrow.now().timestamp

    conversation_db_path = get_conversation_db_path_for_users({'user_one': author, 'user_two': username})
    conversation = Conversation(conversation_db_path)
    conversation.add_message(author, message, date_sent)

    return jsonify({
        'success': True
    })


@app.route('/get_new_messages', methods=['POST'])
def get_new_messages():
    data = request.form
    conversation_db_path = get_conversation_db_path_for_users(data)
    conversation_db = Conversation(conversation_db_path)

    timestamp = data['timestamp']
    requester_username = data['user_one']

    new_messages = conversation_db.get_new_messages(timestamp, requester_username)

    return jsonify({
        'messages': new_messages
    })


@app.route('/update_avatar/<username>', methods=['POST'])
def update_avatar(username):
    img_b64 = request.form.get('img_b64')

    return jsonify({
        'success': True
    })


@app.route('/get_user_avatar/<username>')
def get_avatar(username):
    avatar_b64 = database.get_user_avatar(username)['avatar']

    return jsonify({
        'avatar': avatar_b64
    })


@app.route('/add_friend', methods=['POST'])
def add_friend():
    data = request.form
    user_one = data['user_one']
    user_two = data['user_two']

    if database.user_exists(user_two) and database.user_exists(user_one):
        database.add_friend(user_one, user_two)
        success = True
    else:
        success = False

    return jsonify({
        'success': success
    })


@app.route('/get_friends/<username>')
def get_friends(username):
    friends = database.get_friends(username)

    if len(friends):
        all_friends = database.get_users_by_username(friends)
    else:
        all_friends = []

    return jsonify({
        'friends': all_friends
    })


@app.route('/block_friend', methods=['POST'])
def block_friend():
    data = request.form
    user_one = data['user_one']
    user_two = data['user_two']

    database.block_friends(user_one, user_two)

    return jsonify({
        'success': True
    })


if __name__ == '__main__':
    app.run(debug=True)
