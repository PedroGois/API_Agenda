# ============================================================================
# IMPORTS
# ============================================================================
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import (
    UserMixin, LoginManager, login_user, logout_user, 
    login_required, current_user
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO
# ============================================================================
app = Flask(__name__)

# Configurações do banco de dados e segurança
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
app.config['SECRET_KEY'] = '15998313957'

# Inicializações
db = SQLAlchemy(app)
CORS(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ============================================================================
# MODELOS DO BANCO DE DADOS
# ============================================================================
class Usuario(db.Model, UserMixin):
    """Modelo de usuário do sistema"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

    def set_password(self, senha):
        """Define a senha com hash"""
        self.senha = generate_password_hash(senha)

    def check_password(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha, senha)


class Agenda(db.Model):
    """Modelo de itens da agenda"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String, nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)


# ============================================================================
# CONFIGURAÇÃO DE AUTENTICAÇÃO
# ============================================================================
@login_manager.user_loader
def load_user(user_id):
    """Callback para recarregar o usuário da sessão"""
    return Usuario.query.get(int(user_id))


# ============================================================================
# ROTAS DE AUTENTICAÇÃO
# ============================================================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Registra um novo usuário no sistema.
    
    Body: {
        "nome": "string",
        "email": "string",
        "senha": "string"
    }
    """
    data = request.json
    if not data or not data.get('email') or not data.get('senha') or not data.get('nome'):
        return jsonify({'error': 'Email, senha e nome são obrigatórios'}), 400

    # Verifica se o usuário já existe
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Usuário já existe'}), 400

    # Cria novo usuário
    novo_usuario = Usuario(nome=data['nome'], email=data['email'])
    novo_usuario.set_password(data['senha'])

    try:
        db.session.add(novo_usuario)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao registrar usuário', 'detail': str(e)}), 500

    # Retorna dados do usuário criado e qual arquivo DB está sendo usado (ajuda no diagnóstico)
    return jsonify({
        'message': 'Usuário registrado com sucesso',
        'usuario': {
            'id': novo_usuario.id,
            'nome': novo_usuario.nome,
            'email': novo_usuario.email
        },
        'db_path': db.engine.url.database
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Realiza login de um usuário.
    
    Body: {
        "email": "string",
        "senha": "string"
    }
    """
    data = request.json
    if not data or not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    usuario = Usuario.query.filter_by(email=data['email']).first()

    if usuario and usuario.check_password(data['senha']):
        login_user(usuario)
        return jsonify({
            'message': 'Login realizado com sucesso',
            'usuario': {
                'id': usuario.id,
                'nome': usuario.nome,
                'email': usuario.email
            }
        }), 200

    return jsonify({'error': 'Email ou senha inválidos'}), 401


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """Realiza logout do usuário autenticado"""
    logout_user()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200


# ============================================================================
# ROTAS DA AGENDA
# ============================================================================
@app.route('/api/agenda', methods=['GET'])
@login_required
def get_all_agenda_items():
    """Lista todos os itens da agenda do usuário autenticado"""
    items = Agenda.query.filter_by(usuario_id=current_user.id).all()
    result = []
    for item in items:
        result.append({
            'id': item.id,
            'nome': item.nome,
            'categoria': item.categoria,
            'data': item.data.isoformat()
        })
    return jsonify(result), 200


@app.route('/api/agenda/<int:item_id>', methods=['GET'])
@login_required
def get_agenda_item(item_id):
    """Retorna os detalhes de um item específico da agenda"""
    item = Agenda.query.get(item_id)
    if not item:
        return jsonify({'error': 'Agenda item not found'}), 404

    # Verifica se o item pertence ao usuário autenticado
    if item.usuario_id != current_user.id:
        return jsonify({'error': 'Você não tem permissão para visualizar este item'}), 403

    return jsonify({
        'id': item.id,
        'nome': item.nome,
        'categoria': item.categoria,
        'data': item.data.isoformat()
    }), 200


@app.route('/api/agenda/add', methods=['POST'])
@login_required
def add_agenda_item():
    """
    Adiciona um novo item à agenda do usuário.
    
    Body: {
        "nome": "string",
        "categoria": "string",
        "data": "ISO format datetime (YYYY-MM-DDTHH:MM:SS)"
    }
    """
    data = request.json
    if "nome" not in data or "categoria" not in data or "data" not in data:
        return jsonify({'error': 'invalid agenda parametters'}), 400

    dt = datetime.fromisoformat(data["data"])
    item = Agenda(
        nome=data["nome"],
        categoria=data["categoria"],
        data=dt,
        usuario_id=current_user.id
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Agenda item added successfully'}), 201


@app.route('/api/agenda/update/<int:item_id>', methods=['PUT'])
@login_required
def update_agenda_item(item_id):
    """
    Atualiza um item da agenda.
    
    Body: {
        "nome": "string (opcional)",
        "categoria": "string (opcional)",
        "data": "ISO format datetime (opcional)"
    }
    """
    item = Agenda.query.get(item_id)
    if not item:
        return jsonify({'error': 'Agenda item not found'}), 404

    # Verifica se o item pertence ao usuário autenticado
    if item.usuario_id != current_user.id:
        return jsonify({'error': 'Você não tem permissão para atualizar este item'}), 403

    data = request.json
    if "nome" in data:
        item.nome = data["nome"]
    if "categoria" in data:
        item.categoria = data["categoria"]
    if "data" in data:
        item.data = datetime.fromisoformat(data["data"])

    db.session.commit()
    return jsonify({'message': 'Agenda item updated successfully'}), 200


@app.route('/api/agenda/delete/<int:item_id>', methods=['DELETE'])
@login_required
def delete_agenda_item(item_id):
    """Deleta um item da agenda"""
    item = Agenda.query.get(item_id)
    if not item:
        return jsonify({'error': 'Agenda item not found'}), 404

    # Verifica se o item pertence ao usuário autenticado
    if item.usuario_id != current_user.id:
        return jsonify({'error': 'Você não tem permissão para deletar este item'}), 403

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Agenda item deleted successfully'}), 200


# ============================================================================
# ROTA RAIZ
# ============================================================================
@app.route('/')
def Home():
    """Rota raiz da API"""
    return "Agenda de Conserto API!"


# ============================================================================
# INICIALIZAÇÃO DO BANCO DE DADOS
# ============================================================================
with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()


# ============================================================================
# EXECUÇÃO DA APLICAÇÃO
# ============================================================================
    
if __name__ == '__main__':
    app.run(debug=True)
