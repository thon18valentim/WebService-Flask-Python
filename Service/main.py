from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random
import hashlib

app = Flask(__name__)
app.debug = True

def saveLog(text):
    f = open("log.txt", 'a')
    f.write(text + "\n")
    f.close

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
        return f"Nome : {self.user}"

db.create_all()
class Transaction():
    def __init__(self, transaction_from, transaction_to, transaction_hash = ""):
        self.transaction_from = transaction_from
        self.transaction_to = transaction_to
        self.transaction_hash = transaction_hash

    def __repr__(self):
        return f"De: {self.transaction_from} | Para: {self.transaction_to} | Hash: {self.transaction_hash}"

transactions = []
for i in range(10):
    trans = Transaction(hex(random.randint(1000, 10000)), hex(random.randint(1000, 10000)))
    saveLog(f"Transacao gerada: {trans}")
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
        saveLog(f"{objeto} cadastrado com sucesso")
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
        saveLog(f"Staking gerado: {staking}")
        validator.stake = staking
        db.session.commit()
        return redirect("/")

@app.route('/choose', methods = ["GET"])
def choose():
    trans = None
    for i in transactions:
        if i.transaction_hash is None:
            trans = i

    validators = Validator.query.all()

    validatorsId = []
    validatorsStakes = []

    for i in validators:
        validatorsId.append(i.id)
        # Caso o stake nao tenha sido inicializado
        # ele deve ser igual a 1
        if(i.stake is None):
            i.stake = 1
        validatorsStakes.append(i.stake)

    chosenOne = random.choices(validatorsId, weights=validatorsStakes, k=1)

    inteiro = chosenOne[0]

    for i in validators:
        if i.id == inteiro:
            saveLog(f"{i.user} foi escolhido")
            validationHash = hashlib.sha256()
            num = str(random.randint(1,100))
            validationHash.update(bytes(num, encoding='utf8'))
            f = open("hash.txt", 'w')
            f.write(validationHash.hexdigest())
            f.close
            saveLog(f"Hash gerada: {validationHash.hexdigest()}")
            return f"<h4>{i.user} foi escolhido!</h4> </br>"

    return "Ué, ninguém foi escolhido!"

@app.route('/validate', methods = ["GET", "POST"])
def validate():
    f = open("hash.txt", 'r')
    validationHash = f.read()
    f.close
    if validationHash == "":
        return redirect("/")

    if request.method == "GET":
        return render_template("validate.html")
    else:
        hash = request.form['hash']

        if(validationHash == hash):
            f = open("hash.txt", 'r+')
            f.truncate(0)
            f.close
            return f"<h4>Bloco validado</h4> </br>"

        return f"<h4>Bloco nao validado</h4> </br>"

@app.route('/delete', methods = ["GET", "POST"])
def delete():
    if request.method == "GET":
        return render_template("delete.html")
    else:
        id=request.form['id']
        objeto = Validator.query.get(id)
        saveLog(f"{objeto} deletado")
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
        saveLog(f"{validators} validadores listados")
        return render_template("list.html", lista=validators)

app.run(debug=True)