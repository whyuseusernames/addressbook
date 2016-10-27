from flask import Flask, jsonify, request
from db import Database

app = Flask(__name__)

@app.route('/api/<int:id>', methods=['GET'])
def get_id(id):
    db = Database()
    resp = db.get_by_field(field="id", param=id)[0]
    if id == 'does not exist':
        return jsonify(resp), 404
    return jsonify(resp) 

@app.route('/api/<int:id>/update', methods=['POST'])
def update_id(id):
    if request.headers['Content-Type'] == 'application/json':
        content = request.json
        print content
        db = Database()
        resp = db.update(id=id, params=content)
        db.close()
        print resp
        if 'id' in resp and resp['id'] == 'does not exist':
            return jsonify(resp), 404
        return jsonify(resp) 
    else:
        return jsonify({'response': 'failure, content-type should be application/json'})

@app.route('/api/<int:id>/delete', methods=['DELETE'])
def delete_id(id):
    db = Database()
    resp = db.delete(id)
    db.close()
    if resp['id'] == 'does not exist':
        return jsonify(resp), 404
    return jsonify(resp)

@app.route('/api/search', methods=['POST'])
def search_db():
    if request.headers['Content-Type'] == 'application/json':
        content = request.json
        db = Database()
        resp = db.search(content)
        db.close()
        return jsonify(resp)

@app.route('/api/all', methods=['GET'])
def get_all():
    db = Database()
    resp = db.dump()
    db.close()
    return jsonify(resp)

@app.route('/api/new', methods=['POST'])
def new_entry():
    if request.headers['Content-Type'] == 'application/json': 
        content = request.json
        if all(key in content for key in ("name", "address", "phone")):
            db = Database()
            resp = db.insert(name=content['name'], address=content['address'], phone=content['phone'])
            db.close()
        return jsonify(resp)

if __name__ == "__main__":
    app.run()
