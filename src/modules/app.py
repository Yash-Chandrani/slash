from flask import Flask, request, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_user, LoginManager, UserMixin,logout_user, current_user
from scraper import driver
# from forms import RegisterForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__, template_folder=".")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY']='504038774627ae2489c38028'
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(length=50),nullable=False)
    email = db.Column(db.String(length=100), nullable=False, unique=True)
    password = db.Column(db.String(length=30), nullable=False)

    @property
    def passwordInput(self):
        return self.passwordInput

    @passwordInput.setter
    def passwordInput(self,plain_text_password):
        self.password=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self,attempted_password):
        return bcrypt.check_password_hash(self.password,attempted_password)

class Wishlist(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    user_id=db.Column(db.Integer(),db.ForeignKey('users.id'))
    product_title=db.Column(db.String(length=1000),nullable=False)
    product_link=db.Column(db.String(length=1000),nullable=False)
    product_price=db.Column(db.Float(),nullable=False)
    product_website=db.Column(db.String(length=100),nullable=False)
    product_rating=db.Column(db.Float(),nullable=False)

@app.route("/")
def landingpage():
    return render_template("./webapp/static/landing.html")


@app.route("/search", methods=["POST", "GET"])
def product_search(new_product="", sort=None, currency=None, num=None):
    product = request.args.get("product_name")
    if product == None:
        product = new_product

    data = driver(product, currency, num, 0, False, None, True, sort)

    return render_template("./webapp/static/result.html", data=data, prod=product, user_login=current_user.is_authenticated)


@app.route("/filter", methods=["POST", "GET"])
def product_search_filtered():

    product = request.args.get("product_name")
    sort = request.form["sort"]
    currency = request.form["currency"]
    num = request.form["num"]

    if sort == "default":
        sort = None
    if currency == "usd":
        currency = None
    if num == "default":
        num = None
    return product_search(product, sort, currency, num)

@app.route('/register', methods=['GET','POST'])
def register_page():
    from forms import RegisterForm
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user_to_create=Users(name=form.name.data,
                                 email=form.email.data,
                                 passwordInput=form.password1.data)
            db.session.add(user_to_create)
            db.session.commit()
            return redirect(url_for('landingpage'))
        except IntegrityError:
            db.session.rollback()
            flash('An account with this email already exists. Please use a different email.', category='danger')
    if form.errors!= {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating user: {err_msg}', category='danger')
    return render_template("./webapp/static/register.html", form=form)


@app.route('/login',methods=['GET','POST'])
def login_page():
    from forms import LoginForm
    form=LoginForm()
    if form.validate_on_submit():
        attempted_user=Users.query.filter_by(email=form.email.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.email} ', category='success')
            return redirect(url_for('landingpage'))

        else:
            flash('Email or password do not match! Please try again', category='danger')

    return render_template("./webapp/static/login.html",form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('landingpage'))

@app.route("/wishlist",methods=['GET'])
def wishlist():
    if current_user.is_authenticated:
            wishlists= Wishlist.query.filter_by(user_id=current_user.id).all()
            return render_template("./webapp/static/wishlist.html", user=current_user.id, data=wishlists)
    return login_page()




