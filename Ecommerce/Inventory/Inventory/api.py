from flask import Flask, request, jsonify
from functools import wraps
import os
import sys
import datetime

from flask import Flask, request, abort

from general import log, getEnvVar, isDocker, niceJson, allLinks



# Use the name of the current directory as a service type
serviceType = os.path.basename(os.getcwd())
logger = log(serviceType).logger

# Setup MiSSFire
if getEnvVar('TOKEN', False):
    try:
        from MiSSFire import jwt_conditional, Requests
        requests = Requests()
    except ImportError:
        logger.error("Module MiSSFire is required. Terminating.")
        exit()
else:
    from general import Requests
    requests = Requests()
    def jwt_conditional(reqs):
        def real_decorator(f):
            return f
        return real_decorator


# Setup Flask
# FLASK_DEBUG = getEnvVar('FLASK_DEBUG', False)
# FLASK_HOST = '0.0.0.0'


if isDocker():
    FLASK_PORT = 80
else:
    FLASK_PORT = 9083

app = Flask(__name__)



# Simulated product data (replace with your actual data source)
products = {
    'product1': {'name': 'Product 1', 'price': 10.0, 'stock': 100},
    'product2': {'name': 'Product 2', 'price': 20.0, 'stock': 50},
    'product3': {'name': 'Product 3', 'price': 20.0, 'stock': 50},
    'product4': {'name': 'Product 4', 'price': 20.0, 'stock': 50},
    'product5': {'name': 'Product 5', 'price': 100.0, 'stock': 50},
    'product6': {'name': 'Product 6', 'price': 120.0, 'stock': 50},
    'product7': {'name': 'Product 7', 'price': 200.0, 'stock': 50},
    'product8': {'name': 'Product 8', 'price': 290.0, 'stock': 50},
    'product9': {'name': 'Product 9', 'price': 2000.0, 'stock': 50},
    # Add more products here
}

@app.route("/", methods=['GET'])
def hello():
    return niceJson({"subresource_uris": allLinks(app)}, 200)


"""
# Simulated authentication decorator (replace with your actual authentication logic)
def jwt_conditional(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Simulated JWT authentication logic (replace with your own)
        auth_header = request.headers.get('Authorization')
        if not auth_header or 'Bearer ' not in auth_header:
            return jsonify({'message': 'Authentication required'}), 401
        # You can decode and verify the JWT here if needed
        return func(*args, **kwargs)
    return decorated_function
"""

@app.route("/products/<product_id>", methods=['GET'])
@jwt_conditional(requests)
def getProduct(product_id):
    product = products.get(product_id)
    if product:
        print(jsonify(product))
        return jsonify(product), 200
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route("/products/<product_id>/stock", methods=['PUT'])
@jwt_conditional(requests)
def updateStock(product_id):
    product = products.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    try:
        data = request.get_json()
        new_stock = data.get('stock')
        if new_stock is not None:
            product['stock'] = new_stock
            return jsonify({'message': 'Stock updated successfully'}), 200
        else:
            return jsonify({'message': 'Invalid request data'}), 400
    except Exception as e:
        return jsonify({'message': 'Error updating stock', 'error': str(e)}), 500


# All APIs provided by this application, automatically generated
LOCAL_APIS = allLinks(app)
# All external APIs that this application relies on, manually created
KNOWN_REMOTE_APIS = []


def main():
    """
    logger.info("%s service starting now: MTLS=%s, Token=%s" % (SERVICE_TYPE, MTLS, TOKEN))
    # Start Flask web server
    if MTLS and serviceCert:
        # SSL configuration for Flask. Order matters!
        cert = serviceCert.getServiceCertFileName()
        key = serviceCert.getServiceKeyFileName()
        if cert and key:
            app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG, ssl_context=(cert, key))
        else:
            logger.error("Cannot serve API without SSL cert and key.")
            exit()
    else:
    """
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)





# if __name__ == "__main__":
#     main()   
if __name__ == "__main__":

    
    app.run(debug=True)
