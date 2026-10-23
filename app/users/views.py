from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    make_response,
)
from app.users import users_bp


@users_bp.route('/hi/<string:name>')
def greetings(name):
  name_upper = name.upper()
  age = request.args.get('age', None, type=int)
  return render_template(
      'users/hi.html', name=name_upper, age=age, title='Greeting Page'
  )


@users_bp.route('/admin')
def admin():
  to_url = url_for(
      'users.greetings', name='administrator', age=45, _external=True
  )
  return redirect(to_url)


# 1. Сторінка входу (Login)
@users_bp.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    # Проста перевірка (заглушка)
    if username == 'admin' and password == '1234':
      session['user'] = username
      flash('Ви успішно увійшли в систему!', 'success')
      return redirect(url_for('users.profile'))
    else:
      flash('Wrong data! Try again!', 'error')
      return redirect(url_for('users.login'))

  return render_template('users/login.html', title='Вхід')


# 2. Сторінка профілю (Profile) з кукі та темою
@users_bp.route('/profile')
def profile():
  if 'user' not in session:
    flash('Будь ласка, увійдіть для доступу до профілю.', 'warning')
    return redirect(url_for('users.login'))

  user = session['user']
  cookies = request.cookies
  theme = request.cookies.get('theme', 'light')  # тема за замовчуванням світла

  return render_template(
      'users/profile.html',
      title='Профіль',
      user=user,
      cookies=cookies,
      theme=theme,
  )


# 3. Вихід із системи (Logout)
@users_bp.route('/logout')
def logout():
  session.pop('user', None)
  flash('Ви вийшли із системи.', 'info')
  return redirect(url_for('users.login'))


# 4. Робота з кукі: Додавання / Видалення
@users_bp.route('/cookie/add', methods=['POST'])
def add_cookie():
  key = request.form.get('key')
  value = request.form.get('value')
  max_age = request.form.get('max_age', type=int)

  response = make_response(redirect(url_for('users.profile')))
  if key and value:
    response.set_cookie(key, value, max_age=max_age)
    flash(f"Кукі '{key}' успішно додано!", 'success')
  return response


@users_bp.route('/cookie/delete', methods=['POST'])
def delete_cookie():
  key = request.form.get('key')
  response = make_response(redirect(url_for('users.profile')))
  if key:
    response.delete_cookie(key)
    flash(f"Кукі '{key}' видалено!", 'info')
  return response


@users_bp.route('/cookie/delete_all', methods=['POST'])
def delete_all_cookies():
  response = make_response(redirect(url_for('users.profile')))
  for key in request.cookies:
    if key != 'session':  # сесію залишаємо, щоб не розлогінити користувача
      response.delete_cookie(key)
  flash('Усі кукі видалено!', 'info')
  return response


# 5. Зміна колірної схеми (Теми)
@users_bp.route('/theme/<string:theme_name>')
def change_theme(theme_name):
  response = make_response(redirect(url_for('users.profile')))
  response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
  flash(f'Тему змінено на {theme_name}!', 'success')
  return response