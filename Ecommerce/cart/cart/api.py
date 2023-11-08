import os

from flask import Flask, request, abort
from requests import codes
from requests.exceptions import ConnectionError
from werkzeug.exceptions import NotFound, ServiceUnavailable

from general import log, getEnvVar, isDocker, niceJson, allLinks


# Use the name of the current directory as a service type
serviceType = os.path.basename(os.getcwd())
logger = log(serviceType).logger

# Setup MiSSFire
try:
    PROT = 'http'
    if getEnvVar('MTLS', False) or getEnvVar('TOKEN', False):
        from MiSSFire import Requests
        requests = Requests()
        if getEnvVar('MTLS', False):
            PROT = 'https'

        if getEnvVar('TOKEN', False):
            from MiSSFire import jwt_conditional
        else:
            def jwt_conditional(reqs):
                def real_decorator(f):
                    return f
                return real_decorator
    else:
        from general import Requests
        requests = Requests()
        def jwt_conditional(reqs):
            def real_decorator(f):
                return f
            return real_decorator
except ImportError:
    logger.error("Module MiSSFire is required. Terminating.")
    exit()


# Setup Flask
# FLASK_DEBUG = getEnvVar('FLASK_DEBUG', False)
# FLASK_HOST = '0.0.0.0'
if isDocker():
    FLASK_PORT = 80
    USERS_SERVICE_URL        = '%s://%s:%s/' % (PROT, "users", 80)
    ACCOUNTS_SERVICE_URL     = '%s://%s:%s/' % (PROT, "accounts", 80)
    INVENTORY_SERVICE_URL = '%s://%s:%s/' % (PROT, "INVENTORY", 80)
else:
    FLASK_PORT = 9084
    USERS_SERVICE_URL        = '%s://%s:%s/' % (PROT, '0.0.0.0', 9081)
    ACCOUNTS_SERVICE_URL     = '%s://%s:%s/' % (PROT, '0.0.0.0', 9082)
    INVENTORY_SERVICE_URL = '%s://%s:%s/' % (PROT, '0.0.0.0', 9083)

app = Flask(__name__)



@app.route("/", methods=['GET'])
def hello():
    return niceJson({"subresource_uris": allLinks(app)}, 200)




carts = {}

@app.route("/", methods=['GET'])
def hello():
    return niceJson({"subresource_uris": allLinks(app)}, 200)

@app.route("/carts/<user_id>/add_item", methods=['POST'])
@jwt_conditional(requests)
def addCartItem(user_id):
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        # Check if the product exists
        product = products.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404

        # Check if the user has a cart
        if user_id not in carts:
            carts[user_id] = {}

        # Add the item to the user's cart
        if product_id not in carts[user_id]:
            carts[user_id][product_id] = 0
        carts[user_id][product_id] += quantity

        return jsonify({'message': 'Item added to cart successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error adding item to cart', 'error': str(e)}), 500

@app.route("/carts/<user_id>/remove_item", methods=['POST'])
@jwt_conditional(requests)
def removeCartItem(user_id):
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        # Check if the user has a cart
        if user_id not in carts:
            return jsonify({'message': 'Cart not found'}), 404

        # Check if the item is in the user's cart
        if product_id not in carts[user_id]:
            return jsonify({'message': 'Item not found in cart'}), 404

        # Remove the item from the user's cart
        if carts[user_id][product_id] <= quantity:
            del carts[user_id][product_id]
        else:
            carts[user_id][product_id] -= quantity

        return jsonify({'message': 'Item removed from cart successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error removing item from cart', 'error': str(e)}), 500

@app.route("/carts/<user_id>/checkout", methods=['POST'])
@jwt_conditional(requests)
def checkoutCart(user_id):
    try:
        # Check if the user has a cart
        if user_id not in carts:
            return jsonify({'message': 'Cart not found'}), 404

        total_price = 0

        # Calculate the total price of items in the cart
        for product_id, quantity in carts[user_id].items():
            product = products.get(product_id)
            if not product:
                return jsonify({'message': f'Product {product_id} not found'}), 404

            if quantity <= 0 or product['stock'] < quantity:
                return jsonify({'message': f'Invalid quantity for product {product_id}'}), 400

            total_price += product['price'] * quantity

        # Check the user's balance from the account service (replace with actual API call)
        account_balance = get_account_balance_from_account_service(user_id)

        if account_balance is None:
            return jsonify({'message': 'Error checking user balance'}), 500

        if total_price > account_balance:
            return jsonify({'message': 'Insufficient balance'}), 400

        # Deduct the total price from the user's account balance (replace with actual API call)
        if not deduct_balance_from_account(user_id, total_price):
            return jsonify({'message': 'Error deducting balance'}), 500

        # Clear the user's cart after successful checkout
        carts[user_id] = {}

        return jsonify({'message': 'Checkout successful'}), 200

    except Exception as e:
        return jsonify({'message': 'Error during checkout', 'error': str(e)}), 500

# Helper functions for interacting with the account service (replace with actual implementation)
def get_account_balance_from_account_service(user_id):
    # Implement logic to retrieve the user's account balance from the account service
    # Return the balance or None if there was an error
    # Example: account_balance = make_api_call_to_account_service("/accounts/balance", user_id)
    # Replace make_api_call_to_account_service with your actual API call function
    return None

def deduct_balance_from_account(user_id, amount):
    # Implement logic to deduct the specified amount from the user's account
    # Return True if the balance was successfully deducted, False otherwise
    # Example: result = make_api_call_to_account_service("/accounts/deduct", {"user_id": user_id, "amount": amount})
    # Replace make_api_call_to_account_service with your actual API call function
    return False

if __name__ == "__main__":
    app.run(debug=True)
