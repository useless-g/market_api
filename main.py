from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_httpauth import HTTPBasicAuth
import pymongo

app = Flask(__name__)

auth = HTTPBasicAuth()


def connection_check():
    try:
        db_client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError as SSTE:
        print("Unable to connect to the DB.")
        return 1
    return 0


@auth.get_password
def get_password(login):
    if login == 'design':
        return 'smart'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route('/')
def index():
    return '<h4> leavem3here </h4>'


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def make_uri_product(product):
    new_product = dict()
    for key in product.keys():
        if key == '_id':
            new_product['uri'] = url_for('get_product', product_id=product['_id'], _external=True)
        else:
            new_product[key] = product[key]
    return new_product


@app.route('/market/api/v1.0/products', methods=['GET'])
@auth.login_required
def get_products():
    if connection_check():
        return jsonify({'ERROR': 'lost connection to database, restart DB and try again'})
    return jsonify({'all_products': list(map(make_uri_product, products.find({})))})


@app.route('/market/api/v1.0/products/<int:product_id>', methods=['GET'])
@auth.login_required
def get_product(product_id):
    if connection_check():
        return jsonify({'ERROR': 'lost connection to database, restart DB and try again'})
    product = products.find_one({'_id': product_id})
    if product:
        return jsonify({f'product {product_id}': make_uri_product(product)})
    abort(404)


@app.route('/market/api/v1.0/filter_products', methods=['GET'])
@auth.login_required
def search_product():
    if connection_check():
        return jsonify({'ERROR': 'lost connection to database, restart DB and try again'})
    product = list()
    if not request.json:
        abort(400)
    if 'title' in request.json:
        if type(request.json['title']) is not str:
            abort(400)
        title = request.json.get('title')
        for _ in products.find({'title': {'$regex': f'^(.*?){title}(.*?)'}}):
            product.append(_['title'])
        if product:
            return jsonify({f'search result for "{title}"': product})
        abort(404)

    elif 'parameters' in request.json:
        if type(request.json['parameters']) is not list:
            abort(400)
        parameters = sorted(request.json.get('parameters', []), key=(lambda x: x[0] if x else ''))
        if len(parameters) == 3:
            for _ in products.find({'parameters': parameters}):
                product.append(_['title'])
            if product:
                return jsonify({f'search with parameters result': product})
            abort(404)
        else:
            for _ in products.find({}):
                flag = False
                for parameter in parameters:
                    if parameter not in _['parameters']:
                        flag = True
                if flag:
                    continue
                product.append(_['title'])
            if product:
                return jsonify({f'search with parameters result': product})
            abort(404)


@app.route('/market/api/v1.0/products', methods=['POST'])
@auth.login_required
def create_product():
    if connection_check():
        return jsonify({'ERROR': 'lost connection to database, restart DB and try again'})
    if not request.json or 'title' not in request.json:
        abort(400)
    try:
        _id = (products.find({}).sort('_id', pymongo.DESCENDING)[0]['_id'] + 1)
    except IndexError:
        _id = 1
    product = {
        '_id': _id,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'parameters': sorted(request.json.get('parameters', []), key=(lambda x: x[0] if x else ''))
    }
    ins_result = products.insert_one(product)
    return jsonify({'new_product': make_uri_product(product)}), 201


@app.route('/market/api/v1.0/products/<int:product_id>', methods=['PUT'])
@auth.login_required
def update_product(product_id):
    if connection_check():
        return jsonify({'ERROR': 'lost connection to database, restart DB and try again'})
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) is not str:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not str:
        abort(400)
    if 'parameters' in request.json and type(request.json['parameters']) is not list:
        abort(400)
    product = products.find_one({'_id': product_id})
    if product:
        product['title'] = request.json.get('title', product['title'])
        product['description'] = request.json.get('description', product['description'])
        product['parameters'] = request.json.get('parameters', product['parameters'])
        upd_result = products.update_one({'_id': product_id}, {'$set': {**product}})
        return jsonify({'update_product': make_uri_product(product)})
    abort(404)


@app.route('/market/api/v1.0/products/<int:product_id>', methods=['DELETE'])
@auth.login_required
def delete_product(product_id):
    if connection_check():
        return jsonify({'ERROR': 'lost connection to database, restart DB and try again'})
    product = products.find_one({'_id': product_id})
    if product:
        products.delete_one({'_id': product_id})
        return jsonify({'result': True})
    abort(404)


if __name__ == '__main__':
    db_client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    if connection_check():
        exit(2)
    print("database connection established")
    product_db = db_client["product_db"]
    # product_db.products.drop()
    products = product_db["products"]
    app.run(debug=False)
