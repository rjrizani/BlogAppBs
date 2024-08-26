from flask import Flask, render_template,request,redirect,url_for,session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import*
import json
import math
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin

app = Flask(__name__)

with open('config.json', 'r') as c:
    param = json.load(c)["parameters"]

if param["local_server"]:
    app.config['SQLALCHEMY_DATABASE_URI'] = param["local_url"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = param["prod_url"]

SECRET_KEY = param["secret_key"]

#app.config['SECRET_KEY']
app.config['SECRET_KEY']=param['secret_key']

db = SQLAlchemy(app)
#pip install mysqlclient
# pip3 install mysql-connector



class Contact(db.Model):
    sno = db.Column('sno',db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(20))

class Posts(db.Model):
    post_id = db.Column('post_id',db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    sub_title = db.Column(db.String(200))
    location = db.Column(db.String(50))
    author = db.Column(db.String(30))
    date_posted = db.Column(db.Date)
    image = db.Column(db.String(150))
    content_1= db.Column(db.Text)
    content_2 = db.Column(db.Text)
    slug = db.Column(db.String(100), unique=True)

class Users(UserMixin,db.Model):
    id = db.Column('id',db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(50), nullable=False)

@app.route("/")
def home():
    db.session.commit()
    post_data = Posts.query.all()
    n = 2
    last = math.ceil(len(post_data)/n)
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    j = (page-1)*n
    posts = post_data[j:j+n]

    if page == 1:
        prev = "#"
        next = "/?page="+str(page+1)
    elif page == last:
        prev = "/?page="+str(page-1)
        next = "#"
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)


    return render_template("index.html", posts=posts, param=param, prev=prev, next=next)


@app.route("/post/<slug>", methods=['GET'])
def post(slug):
    single_post = Posts.query.filter_by(slug=slug).first()
    return render_template("post.html", post=single_post,param=param)

@app.route("/about")
def about():
    return render_template("about.html", param=param)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username, password=password).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('login'))
    return render_template("login.html", param=param)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/contact",methods=['GET','POST'])
def contact():
    if (request.method=='POST'):
        Name = request.form.get('name')
        Email = request.form.get('email')
        Msg = request.form.get('message')
        entry = Contact(name=Name,email=Email, message=Msg, date=datetime.today().date())
        db.session.add(entry)
        db.session.commit()
    return render_template("contact.html", param=param)

@app.route("/admin",methods=['GET', 'POST'])
@login_required
def dashboard():
    user = current_user.name
    posts = Posts.query.filter_by(author=user).all()
    contacts = Contact.query.filter_by().all()
    if not current_user.username == param['admin']:
        style= 'display:none;'
    return render_template("admin/index.html", param=param, posts=posts, contacts=contacts, user=user)


@app.route("/editPost/<string:post_id>",methods=['GET', 'POST'])
def edithtml(post_id):
    if request.method == 'POST':
        ntitle = request.form.get('title')
        nsubtitle = request.form.get('subtitle')
        nauthor = request.form.get('author')
        nimage = request.form.get('image')
        nlocation = request.form.get('location')
        nslug = request.form.get('slug')
        ndate = datetime.now()
        ncontent1 = request.form.get('content1')
        ncontent2 = request.form.get('content2')
        if post_id == '0':  # add a new post in db
            post = Posts(title=ntitle, sub_title=nsubtitle, location=nlocation,
                         content_1=ncontent1, content_2=ncontent2, author=nauthor, image=nimage, slug=nslug,
                         date_posted=datetime.now())
            db.session.add(post)
            db.session.commit()
        else:
            post = Posts.query.filter_by(post_id=post_id).first()
            post.title = ntitle
            post.sub_title = nsubtitle
            post.author = nauthor
            post.image = nimage
            post.location = nlocation
            post.date_posted = ndate
            post.content_1 = ncontent1
            post.content_2 = ncontent2
            post.slug = nslug
            db.session.commit()
        return redirect(url_for('dashboard'))
    post = Posts.query.filter_by(post_id=post_id).first()
    return render_template('admin/editPost.html', param=param, post=post, post_id=post_id)


@app.route("/delete/<string:post_id>",methods=['GET', 'POST'])
def delete(post_id):
    post = Posts.query.filter_by(post_id=post_id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if (request.method == 'POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()
        if user:
            flash("Email already exists")
            return redirect(url_for('signup'))
        new_user = Users(name=name, username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
    return render_template("signup.html", param=param)

#login manager

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080)