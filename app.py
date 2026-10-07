from flask import Flask, render_template
import os
app = Flask(__name__)

@app.route('/')
@app.route('/resume')
def resume():
    return render_template('resume.html', title='Резюме')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html', title='Контакти')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)