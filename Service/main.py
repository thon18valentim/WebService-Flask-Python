from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random

app = Flask(__name__)
app.debug = True

# =-=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-= DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
def split(word):
    return [char for char in word]

class Validator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(30))
    stake = db.Column(db.Float)
  
    def __repr__(self):
        return f"Nome : {self.nome}"

db.create_all()
class Transaction():
    def __init__(self, transaction_from, transaction_to, transaction_hash = ""):
        self.transaction_from = transaction_from
        self.transaction_to = transaction_to
        self.transaction_hash = transaction_hash
        

transactions = []
for i in range(10):
    trans = Transaction(hex(random.randint(1000, 10000)), hex(random.randint(1000, 10000)))
    transactions.append(trans)


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/cadastro', methods = ["GET", "POST"])
def cadastro():
    if request.method == "GET":
        return render_template("cadastro.html")
    else:
        nome=request.form['nome']

        objeto = Validator(user=nome)
        db.session.add(objeto)
        db.session.commit()
        return redirect("/")

@app.route('/staking', methods = ["GET", "POST"])
def staking():
    if request.method == "GET":
        validators = Validator.query.all()
        return render_template("staking.html", lista=validators)
    else:
        id = request.form['id']
        staking = request.form['stake']

        validator = Validator.query.filter_by(id=id).first()
        db.session.commit()
        validator.stake = staking
        db.session.commit()
        return redirect("/")

@app.route('/validate', methods = ["GET"])
def validate():
    trans = None
    for i in transactions:
        if i.transaction_hash is None:
            trans = i

    validators = Validator.query.all()

    validatorsId = []
    validatorsStakes = []

    for i in validators:
        validatorsId.append(i.id)
        validatorsStakes.append(i.stake)

    chosenOne = random.choices(validatorsId, weights=validatorsStakes, k=1)

    inteiro = ""

    for i in chosenOne:
        inteiro+=str(i)

    for i in validators:
        if i.id == int(inteiro):
            return f"<h4>{i.user} foi escolhido!</h4> </br>"

    return "Ué, ninguém foi escolhido!"


@app.route('/delete', methods = ["GET", "POST"])
def delete():
    if request.method == "GET":
        return render_template("delete.html")
    else:
        id=request.form['id']
        objeto = Validator.query.get(id)
        db.session.delete(objeto)
        db.session.commit()
        return redirect('/')


@app.route('/<string:nome>')
def error(nome):
    variavel = f'Pagina { nome } não existe'
    return render_template("error.html" , variavel_nome = variavel)

@app.route('/list')
def list():
    if request.method == "GET":
        validators = Validator.query.all()
        return render_template("list.html", lista=validators)

app.run(debug=True)