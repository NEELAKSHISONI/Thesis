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

"""

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
        if not updateAccount(accNum, total_price):
            return jsonify({'message': 'Error deducting balance'}), 500

        # Clear the user's cart after successful checkout
        carts[user_id] = {}

        return jsonify({'message': 'Checkout successful'}), 200

    except Exception as e:
        return jsonify({'message': 'Error during checkout', 'error': str(e)}), 500

"""
cart = {}
@app.route("/cart/<product_id>", methods=['POST'])
@jwt_conditional(requests)
def add_to_cart(product_id):
    try:
        data = request.get_json()
        quantity = data.get('quantity', 1)

        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity

        return jsonify({'message': 'Item added to cart successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error adding item to cart', 'error': str(e)}), 500


@app.route("/cart/<product_id>", methods=['DELETE'])
@jwt_conditional(requests)
def remove_from_cart(product_id):
    try:
        if product_id in cart:
            del cart[product_id]
            return jsonify({'message': 'Item removed from cart successfully'}), 200
        else:
            return jsonify({'message': 'Item not found in cart'}), 404
    except Exception as e:
        return jsonify({'message': 'Error removing item from cart', 'error': str(e)}), 500


@app.route("/cart", methods=['GET'])
@jwt_conditional(requests)
def get_cart():
    return jsonify(cart), 200


@app.route("/cart/checkout", methods=['POST'])
@jwt_conditional(requests)
def checkout():
    try:
        # Calculate the total price of items in the cart
        total_price = 0.0
        for product_id, quantity in cart.items():
            # Fetch product details from the external inventory service
            product_details = fetch_product_details(product_id)
            
            if product_details:
                product_price = product_details['price']
                total_price += product_price * quantity
            else:
                return jsonify({'message': f'Product with ID {product_id} not found'}), 404

        # Update the account balance using your existing updateAccount function
        accNum = fetch_account_number(user_ID)
        updated_balance = updateAccount(accNum, -total_price)

        # Clear the cart after a successful checkout
        cart.clear()

        return jsonify({'message': 'Checkout successful', 'new_balance': updated_balance}), 200
    except Exception as e:
        return jsonify({'message': 'Error during checkout', 'error': str(e)}), 500
    

def fetch_account_number():
    try:
        # Construct the URL to request the account number from the account service
        account_url = f"{ACCOUNTS_SERVICE_URL}getAccountNumber"

        # Make a GET request to the account service's API
        response = requests.get(account_url)

        # Check the response status code
        if response.status_code == 200:
            # Successfully retrieved account number
            account_data = response.json()
            accNum = account_data.get('accNum')
            return accNum
        else:
            # Handle other response status codes as needed
            return None
    except Exception as e:
        return None


def fetch_product_details(product_id):
    try:
        # Construct the URL to request the product details from the external inventory service
        url = INVENTORY_SERVICE_URL + 'products/' + product_id

        # Make a GET request to the external service's API
        response = requests.get(url)

        # Check the response status code
        if response.status_code == 200:
            return response.json()  # Assuming the response is in JSON format
        elif response.status_code == 404:
            return None  # Product not found in the external service
        else:
            return None  # Handle other status codes as needed
    except Exception as e:
        return None






#updating the balance in teh account , sending accnum and amount 
def updateAccount(accNum, amount):
    try:
        url = ACCOUNTS_SERVICE_URL + 'accounts/%s' % accNum
        payload = {'amount':amount}
        res = requests.post(url, json=payload)
    except ConnectionError as e:
        raise ServiceUnavailable("Accounts service connection error: %s."%e)

    if res.status_code != codes.ok:
        raise NotFound("Cannot update account %s, resp %s, status code %s" \
                       % (accNum, res.text, res.status_code))
    else:
        return res.json()['balance']
# All APIs provided by this application, automatically generated
LOCAL_APIS = allLinks(app)
# All external APIs that this application relies on, manually created
KNOWN_REMOTE_APIS = [ACCOUNTS_SERVICE_URL + "accounts",
                    INVENTORY_SERVICE_URL + "inventory"]


"""
def main():
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
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)

"""



# if __name__ == "__main__":
#     main()   
if __name__ == "__main__":
    app.run(debug=True)


