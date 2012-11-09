from flask import Flask, request, session, redirect, url_for,\
    abort, render_template, flash

from flask.views import MethodView

from flask.ext.mongoengine import MongoEngine
import datetime

# simple auth
USERNAME = 'admin'
PASSWORD = 'default'
MONGODB_DB = "my_test_db"
SECRET_KEY = "asecretkey"

app = Flask(__name__)
app.config.from_object(__name__)

db = MongoEngine(app)



class Post(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    title = db.StringField(max_length=120, required=True)
    text = db.StringField(required=True)

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'title'],
        'ordering': ['-created_at']
    }



## AUTH
# simple decorator
def user_required(f):
    """Checks whether user is logged in or raises error 401."""
    def decorator(*args, **kwargs):
        if not session.get('logged_in'):
            abort(401)
        return f(*args, **kwargs)
    return decorator

class AuthAPI(MethodView):
    decorators = [user_required]


class ListView(MethodView):
    def get(self):
        entries = Post.objects.all()
        return render_template('show_entries.html', entries=entries)


# Todo: validation
class AddPost(MethodView):
    def post(self):
        if request.method == 'POST':
            post = Post(
                title=request.form['title'],
                text=request.form['text']
            )
            post.save()
        else:
            flash('Error!')
        flash('New entry was successfully posted')
        return redirect(url_for('list'))

    def get(self):
        """
        handle ADD.
        simply return a 401 error
        """
#        return redirect(url_for('login'))
        abort(401)


class Login(MethodView):
    def get(self):
        return render_template('login.html')

    def post(self):
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('list'))
        return render_template('login.html', error=error)


class Logout(MethodView):
    def get(self):
        """
        handle session.
        if we receive a GET request outside session, then drop it.
        if we receive a POST request treat as a NotFound 404 Error.
        """
        if session.pop('logged_in', None):
            flash('Logged out')
            return redirect(url_for('list'))
        else:
            return 'wrong request!'
    def post(self):
        abort(404)


## VIEWS
# build some views here
app.add_url_rule('/', view_func=ListView.as_view('list'))
app.add_url_rule('/login', view_func=Login.as_view('login'))

# AUTH is required here
view = user_required(AuthAPI.as_view('logout','add'))
app.add_url_rule('/logout', view_func=Logout.as_view(('logout')))
app.add_url_rule('/add', view_func=AddPost.as_view('add_entry'))





if __name__ == '__main__':
    app.run()
