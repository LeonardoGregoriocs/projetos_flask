from flask import Flask, Response, request, render_template
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/padaria'

db = SQLAlchemy(app)

class Produtos(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome_produto = db.Column(db.String(50))
    marca = db.Column(db.String(50), nullable=True)
    quantidade_produto = db.Column(db.Integer)
    preco = db.Column(db.Float)

    def to_json(self):
        return {"id":self.id,
                "nome_produto": self.nome_produto,
                "marca": self.marca,
                "quantidade_produto":self.quantidade_produto,
                "preco" : self.preco
        }

@app.route("/")
def index():
    return ("PADARIA")

@app.route("/produtos", methods=["GET"])
def lista_produtos():
    produtos = Produtos.query.all()
    produtos_json = [produto.to_json()for produto in produtos]
    return gera_response(200, "Produtos", produtos_json, "Ok")

@app.route("/produtos/<id>", methods=["GET"])
def lista_produtos_por_id(id):
    produto = Produtos.query.filter_by(id=id).first()
    if produto:
        produto_json = produto.to_json()
        return gera_response(200, "Produtos", produto_json, "OK")
    else:
        return("Produto não localizado!")

@app.route("/produtos/novo", methods=["POST", "GET",])
def cadastrar_novo_produto():
    body = request.get_json()

    try:
        novo_produto = Produtos(
            nome_produto=body['nome_produto'],
            marca=body['marca'],
            quantidade_produto=body['quantidade_produto'],
            preco=body['preco']
        )

        db.session.add(novo_produto)
        db.session.commit()
        return gera_response(201, "Produtos", novo_produto.to_json(), "Criado")

    except Exception as e:
        print(e)
        return gera_response(400, "Produtos", {}, "Erro ao cadastrar")

@app.route("/produtos/atualizar/<id>", methods=["PUT"])
def atualizar_produto(id):
    produto = Produtos.query.filter_by(id=id).first()
    body = request.get_json()

    try:
        if('nome_produto' in body):
            produto.nome_produto = body['nome_produto']
        if('marca' in body):
            produto.marca = body['marca']
        if('quantidade_produto' in body):
            produto.quantidade_produto = body['quantidade_produto']
        if('preco' in body):
            produto.preco = body['preco']

        db.session.add(produto)
        db.session.commit()
        return gera_response(200, "Produtos", produto.to_json(), "Produto atualizado!" )

    except Exception as e:
        print(e)
        return gera_response(400, "Produtos", {}, "Erro ao atualizar produto")

@app.route("/produtos/deletar/<id>", methods=["DELETE"])
def deletar_produto(id):
    produto = Produtos.query.filter_by(id=id).first()

    try:
        db.session.delete(produto)
        db.session.commit()
        return gera_response(200, "Produtos", produto.to_json(), "Produto deletado com sucesso!" )

    except Exception as e:
        print(e)
        return gera_response(400, "Produtos", {}, "Erro ao deletar produto")


def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")
