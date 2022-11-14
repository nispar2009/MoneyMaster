from flask import Flask, render_template, redirect, request, make_response
import sqlite3
import security

app = Flask(__name__)

connection = sqlite3.connect('moneymaster.db')
cursor = connection.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS users (username text, password text, balance int)')

@app.route('/', methods=['GET', 'POST'])
def index():
    connection = sqlite3.connect('moneymaster.db')
    cursor = connection.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        login = security.login(username, password)

        if login['user_exists']:
            if login['auth']:
                response = make_response('You are logged in to your account')
                response.set_cookie('moneymaster_user', username)
                return response
            else:
                return 'Error: Incorrect password'

        cursor.execute('INSERT INTO users (username, password, balance) VALUES (?, ?, 0)', (username, password))
        connection.commit()
        response = make_response('Your new account has been created.')
        response.set_cookie('moneymaster_user', username)
        return response

    print(request.cookies.get('moneymaster_user'))
    
    if len(list(cursor.execute('SELECT * FROM users WHERE username=?', (request.cookies.get('moneymaster_user'),)))) > 0:
        return render_template('index.html', user=list(cursor.execute('SELECT * FROM users WHERE username=?', (request.cookies.get('moneymaster_user'),)))[0])
    
    return render_template('login.html')

app.run(debug=True)