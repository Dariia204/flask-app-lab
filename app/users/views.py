from flask import render_template, request, redirect, url_for
from app.users import users_bp

@users_bp.route('/hi/<string:name>')
def greetings(name):
    name_upper = name.upper()
    age = request.args.get('age', None, type=int)
    return render_template('users/hi.html', name=name_upper, age=age, title='Greeting Page')

@users_bp.route('/admin')
def admin():
    to_url = url_for('users.greetings', name='administrator', age=45, _external=True)
    print(f"Redirecting to: {to_url}")
    return redirect(to_url)