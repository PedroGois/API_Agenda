from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy   
from datetime import datetime
from flask_cors import CORS
from flask_login import UserMixin as use
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chamados.db'
db = SQLAlchemy(app)

class Usuario(db.Model, use):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
class Agenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String, nullable=False)
    data = db.Column(db.DateTime, nullable=False)



    

#rota para adicionar um item na agenda
@app.route('/api/agenda/add',methods=['POST'])
def add_agenda_item():
    data=request.json
    if "nome" not in data or "categoria" not in data or "data" not in data:
        return jsonify({'error': 'invalid agenda parametters'}), 400
    dt=datetime.fromisoformat(data["data"])
    itemagenda=Agenda(nome=data["nome"],categoria=data["categoria"],data=dt)
    db.session.add(itemagenda)
    db.session.commit()
    return jsonify({'message': 'Agenda item added successfully'}), 201

#rota para deletar um item na agenda
@app.route('/api/agenda/delete/<int:item_id>',methods=['DELETE'])
def delete_agenda_item(item_id):
    itemagenda=Agenda.query.get(item_id)
    if itemagenda:
        db.session.delete(itemagenda)
        db.session.commit()
        return jsonify({'message': 'Agenda item deleted successfully'}), 200    
    return jsonify({'error': 'Agenda item not found'}), 404   

#rota para atualizar item na agenda
@app.route('/api/agenda/update/<int:item_id>',methods=['PUT'])
def update_agenda_item(item_id):
    itemagenda=Agenda.query.get(item_id)
    if not itemagenda:
        return jsonify({'error': 'Agenda item not found'}), 404
    data=request.json
    if "nome" in data:
        itemagenda.nome=data["nome"]
    if "categoria" in data:
        itemagenda.categoria=data["categoria"]
    if "data" in data:
        itemagenda.data=datetime.fromisoformat(data["data"])
    db.session.commit()
    return jsonify({'message': 'Agenda item updated successfully'}), 200


#rota para detalhes de um item na agenda
@app.route('/api/agenda/<int:item_id>',methods=['GET'])
def get_agenda_item(item_id):
    itemagenda=Agenda.query.get(item_id)
    if itemagenda:
        return jsonify({
            'id': itemagenda.id,
            'nome': itemagenda.nome,
            'categoria': itemagenda.categoria,
            'data': itemagenda.data.isoformat()
        }), 200
    return jsonify({'error': 'Agenda item not found'}), 404

#rota de listagem de todos os itens na agenda
@app.route('/api/agenda',methods=['GET'])
def get_all_agenda_items():
    items=Agenda.query.all()
    print(items)
    result=[]
    for item in items:
        result.append({
            'id': item.id,
            'nome': item.nome,
            'categoria': item.categoria,
            'data': item.data.isoformat()
        })
    return jsonify(result), 200

#sempre defino uma rota raiz e a função
@app.route('/')
def Home():
    return "Agenda de Conserto API!"

if __name__ == '__main__':
    app.run(debug=True)
