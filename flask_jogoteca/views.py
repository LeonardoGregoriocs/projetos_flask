import time
import os
from flask import render_template, request, redirect, send_from_directory, session, flash, url_for
from dao import JogoDao, UsuarioDao
from models import Jogo
from jogoteca import db, app
from helpers import recupera_imagem, deleta_arquivo

jogo_dao = JogoDao(db)
usuario_dao = UsuarioDao(db)

@app.route('/')
def index():
    #Lista todos os jogos que estão salvo no banco de dados. 
    lista = jogo_dao.listar()
    return render_template('lista.html', titulo='Jogos', jogos=lista)

@app.route('/novo')
def novo():
    #Verifica se o usuário está logado e direciona para a URL de criação de novo jogo para inserir as informações.
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('novo.html', titulo='Novo Jogo')

@app.route('/criar', methods=['POST',])
def criar():
    #Pega as informações que foram inseridas pelo usuário e salva no banco de dados. 
    nome = request. form['nome']
    categoria = request. form['categoria']
    console = request. form['console']
    jogo = Jogo(nome, categoria, console)
    jogo = jogo_dao.salvar(jogo)

    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']
    timestamp = time.time()
    arquivo.save(f'{upload_path}/capa{jogo.id}--{timestamp}.jpg')
    return redirect(url_for('index'))

@app.route('/editar/<int:id>')
def editar(id):
    #Verifica se o usuario está logado e direciona o para o URL de editar para poder alterar.
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('editar', id=id)))
    jogo = jogo_dao.busca_por_id(id)
    nome_imagem = recupera_imagem(id)
    return render_template('editar.html', titulo='Editando Jogo', jogo=jogo, capa_jogo=nome_imagem)

@app.route('/atualizar', methods=['POST',])
def atualizar():
    #Pega as alterações que foram feita pelo usuário e salva no banco de dados.
    nome = request. form['nome']
    categoria = request. form['categoria']
    console = request. form['console']
    jogo = Jogo(nome, categoria, console, id=request.form['id'])
    jogo_dao.salvar(jogo)

    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']
    timestamp = time.time()
    deleta_arquivo(jogo.id)
    arquivo.save(f'{upload_path}/capa{jogo.id}--{timestamp}.jpg')

    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    #Essa rota deleta as informações do banco de dados, conforme o ID informado pelo usuário.
    jogo_dao.deletar(id)
    flash('O jogo foi removido com sucesso!')
    return redirect(url_for('index'))


@app.route('/login')
def login():
    #Rota para o usuário logar. 
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)


@app.route('/autenticar', methods=['POST', ])
def autenticar():
    #Essa rota autentica as informações inseridas pelo usuário.
    usuario = usuario_dao.buscar_por_id(request.form['usuario'])
    if usuario:
        if usuario.senha == request.form['senha']:
            session['usuario_logado'] = usuario.id
            flash(usuario.nome + ' logou com sucesso!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)
    else:
        flash('Não logado, tente novamente!')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    #Rota para o usuário realizar o logout. 
    session['usuario_logado'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('index'))

@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)