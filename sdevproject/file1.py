from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)
CORS(app)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prepped_amount = db.Column(db.Integer, default=0)
    required_amount = db.Column(db.Integer, default=0)
    prepped_by = db.Column(db.String(100), nullable=False)
    waste_amount = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    ingredients = Ingredient.query.all()
    return render_template('index.html', ingredients=ingredients)

@app.route('/ingredients', methods=['GET', 'POST'])
def manage_ingredients():
    if request.method == 'GET':
        return jsonify([ingredient_to_dict(i) for i in Ingredient.query.all()])
    elif request.method == 'POST':
        data = request.json
        new_ingredient = Ingredient(
            name=data['name'],
            prepped_amount=data['prepped_amount'],
            required_amount=data['required_amount'],
            prepped_by=data['prepped_by'],
            waste_amount=data['waste_amount']
        )
        db.session.add(new_ingredient)
        db.session.commit()
        return jsonify({"message": "Ingredient added"}), 201

@app.route('/ingredients/<int:id>', methods=['PUT', 'DELETE'])
def update_or_delete_ingredient(id):
    ingredient = Ingredient.query.get(id)
    if not ingredient:
        return jsonify({"error": "Ingredient not found"}), 404
    
    if request.method == 'PUT':
        data = request.json
        ingredient.prepped_amount = data.get('prepped_amount', ingredient.prepped_amount)
        db.session.commit()
        return jsonify({"message": "Ingredient updated"})
    
    elif request.method == 'DELETE':
        db.session.delete(ingredient)
        db.session.commit()
        return jsonify({"message": "Ingredient deleted"})

@app.before_request
def create_tables():
    db.create_all()

def ingredient_to_dict(ingredient):
    return {
        "id": ingredient.id,
        "name": ingredient.name,
        "prepped_amount": ingredient.prepped_amount,
        "required_amount": ingredient.required_amount,
        "prepped_by": ingredient.prepped_by,
        "waste_amount": ingredient.waste_amount
    }

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
