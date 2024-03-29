from flask import Blueprint, request, jsonify
from config import INDEX_PATH, MODEL_NAME
from flask_module.models import db, Preference
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

bp = Blueprint('preferences', __name__, url_prefix='/preferences')

@bp.route('/', methods=['POST'])
def create_preference():
    data = request.json
    new_pref = Preference(description=data['description'], updatedBy=data['updatedBy'])
    db.session.add(new_pref)
    db.session.commit()
    generate_index()
    return jsonify({'message': 'Preference created successfully'}), 201

@bp.route('/', methods=['GET'])
def get_preferences():
    prefs = Preference.query.all()
    return jsonify([{'id': p.id, 
                     'description': p.description, 
                     'createdAt': p.createdAt, 
                     'updatedAt': p.updatedAt,
                     'updatedBy': p.updatedBy,                      
                     } for p in prefs]), 200

@bp.route('/generate-index', methods=['POST'])
def generate_preferences_index():
    generate_index()
    return jsonify({'message': 'Index generated successfully'}), 200


@bp.route('/<int:id>', methods=['PUT'])
def update_preference(id):
    pref = Preference.query.get_or_404(id)
    data = request.json
    pref.description = data['description']
    pref.updatedBy = data['updatedBy']
    db.session.commit()
    generate_index()
    return jsonify({'message': 'Preference updated successfully'}), 200

@bp.route('/<int:id>', methods=['DELETE'])
def delete_preference(id):
    pref = Preference.query.get_or_404(id)
    db.session.delete(pref)
    db.session.commit()
    generate_index()
    return jsonify({'message': 'Preference deleted successfully'}), 200

def generate_index():
    prefs = Preference.query.all()
    prefDocs = [Document(page_content=p.description) for p in prefs]
    print(prefDocs)
    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    db = FAISS.from_documents(prefDocs, embeddings)
    db.save_local(INDEX_PATH)