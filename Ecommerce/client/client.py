import json
import time
import datetime
from multiprocessing import Process, Queue
import threading
from threading import Barrier
import random
import requests


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import logging
# Set the default logger to DEBUG to see the Requests library logging info.
#logging.basicConfig(level=logging.DEBUG)
import concurrent.futures

import requests

HOST = '0.0.0.0'
APIGATEWAY_PORT = 80

IS_MISSFIRE = False
IS_MISSFIRE_TOKEN = False

if IS_MISSFIRE:
    PROT = 'https'
else:
    PROT = 'http'


NUM_ORDER_PER_CLIENT = 1000

class Simulation():
    def __init__(self, procNum):
        self.client = EcommerceClient()
        self.customers = [{'username':str(procNum), 'pwd':'1234'},
                          {'username':str(procNum+1), 'pwd':'5678'}]
       
        self.barrier = threading.Barrier(2) 
        
        if len(self.customers) == 0:
            print ("No customers to add!")
            exit()

        print("Adding %s  customers." % (len(self.customers)))
        for customer in self.customers:
            userID = self.client.createUser(customer['username'],
                                             customer['pwd'])
            if userID:
                customer['userID'] = userID
            else:
                exit()

            if IS_MISSFIRE_TOKEN:
                token = self.client.login(customer['username'], customer['pwd'])
                if token:
                    customer['access_token'] = token
                else:
                    exit()
            else:
                customer['access_token'] = "notoken"

            accNum = self.client.openAccount(customer['userID'],
                                             customer['access_token'])
            
            if accNum:
                customer['accNum'] = accNum
            else:
                exit()

            #add account balance here 
            accBal = self.clinet.add_balance(customer['accNum'] ,customer['access_token'] ,  100000)
            if accBal : 
                customer['accBal'] = accBal 
            else : 
                exit()
            #add items to cart
            print(customer)

            customer["user_cart"] = [] 

            user_cart = self.client.add_items_to_cart_batch(customer['user_cart'] , customer['access_token'])
            if user_cart : 
                customer['user_cart'] = user_cart
            else : 
                exit()


            print(customer["user_cart"])




            

             

            


        


    def printPerformance(self):
        endTime = datetime.datetime.now()
        secondsPassed = float((endTime - self.startTime).total_seconds())
        return secondsPassed
    

    def runTest(self, queue):
        self.queue = queue
        print ("Start checking_out_cart.")
        self.startTime = datetime.datetime.now()
        x = 0
        y = 1

        for i in range(0,NUM_ORDER_PER_CLIENT+1):
            self.barrier.wait() # Wait for all threads to reach this point before proceeding
            #this needs to be changed 
            res1 = self.client.checout_cart(self.customers[x]['accNum'], 
                                  
                                  self.customers[x]['access_token'])
            res2 = self.client.checout_cart(self.customers[y]['accNum'], 
                                  
                                  self.customers[y]['access_token'])
            if  not res1 or not res2 :
                print ("Fail")
        self.queue.put(self.printPerformance())
        return

    

       


class EcommerceClient:
    def __init__(self):
        self.BASE_URL = "%s://%s:%s" % (PROT, HOST, APIGATEWAY_PORT)
        self.s = requests.Session()

    def createUser(self, username, pwd):
        userID = None
        try:
            url = self.BASE_URL + '/users'
            payload = {'username':username, 
                       'pwd':pwd}
            resp = self.s.post(url, json=payload, verify=False, allow_redirects=False, stream=False)

            # If the user already exist, request his id
            if 'User already exists' in resp.text:
                url += '?username=%s' % username
                resp = self.s.get(url, json=payload, verify=False, allow_redirects=False, stream=False)
            # Proceed with the id extraction
            if int(resp.status_code) >= 400:
                print("Fail to create user: %s; reason: %s; status: %s" \
                      % (username, resp.text, resp.status_code))
            elif 'id' not in resp.json():
                print("'id' not in response msg: %s" % resp.json())
            else:
                userID = resp.json()['id']
                return userID
        except requests.exceptions.ConnectionError as e:
            print("Connection error create user: %s" % e)
        

    def login(self, username, pwd):
        userID = None
        try:
            url = self.BASE_URL + '/login'
            payload = {'username':username, 
                       'pwd':pwd}
            resp = self.s.post(url, json=payload, verify=False, allow_redirects=False, stream=False)

            # Proceed with the access_token extraction
            if int(resp.status_code) >= 400:
                print("Fail to login user: %s; reason: %s; status: %s" \
                      % (username, resp.text, resp.status_code))
            elif 'access_token' not in resp.json():
                print("'access_token' not in response msg: %s" \
                      % resp.json())
            else:
                access_token = resp.json()['access_token']
                return access_token
        except requests.exceptions.ConnectionError as e:
            print("Connection error create user: %s" % e)
        

    def openAccount(self, userID, token):
        accNum = None
        url = '{}/users/{}/accounts'.format(self.BASE_URL, userID)
        try:
            payload = {'access_token': token}
            resp = self.s.post(url, json=payload, verify=False, allow_redirects=False, stream=False)

            if int(resp.status_code) >= 400:
                print("Fail to open account for user: %s; reason: %s; status: %s" \
                      % (userID, resp.text, resp.status_code))
            elif 'accNum' not in resp.json():
                print("'accNum' not in response msg: %s" % resp.json())
            else:
                accNum = resp.json()['accNum']

        except requests.exceptions.ConnectionError as e:
            print("Connection error open account: %s" % e)
        return accNum
    #written by me 
    def addBalance(self, userID, token, amount):
        url = '{}/users/{}/accounts/{}/add-balance'.format(self.BASE_URL, userID, accNum)
        try:
            payload = {
                'access_token': token,
                'amount': amount
            }
            resp = self.s.post(url, json=payload, verify=False, allow_redirects=False, stream=False)

            if int(resp.status_code) >= 400:
                print("Failed to add balance for user: %s; reason: %s; status: %s" % (userID, resp.text, resp.status_code))
            else:
                print("Successfully added balance of %s for user: %s" % (amount, userID))
        
        except requests.exceptions.ConnectionError as e:
            print("Connection error while adding balance: %s" % e)

    

    def add_item_to_cart(self, userId, token, item_name, item_price):
        res = False
        try:
            url = f"{self.BASE_URL}/users/{userId}/cart/add"
            payload = {
                'item_name': item_name,
                'item_price': item_price,
                'access_token': token
            }
            resp = requests.post(url, json=payload, verify=False, allow_redirects=False, stream=False)

            if resp.status_code == 200:
                res = True
            else:
                print(f"Failed to add item to cart: {payload}, status code: {resp.status_code}")

        except requests.exceptions.ConnectionError as e:
            print(f"Connection error while adding item to cart: {e}")

        return res

    def add_items_to_cart_batch(self, userId, token, num_items):
        for i in range(num_items):
            item_name = f"Item {i + 1}"
            item_price = round(random.uniform(1.0, 100.0), 2)
            success = self.add_item_to_cart(userId, token, item_name, item_price)
            if success:
                print(f"Added {item_name} to cart successfully.")
            else:
                print(f"Failed to add {item_name} to cart.")

        

    def get_account_balance(self , accNum) : 
        pass 

    

    def checkout_cart(self, accNum, accBal, Token, user_cart):
        try:
            for item in user_cart:
                if item["price"] <= accBal:
                    # Simulate a cart checkout request
                    checkout_url = 'https://example.com/checkout'  # Replace with your actual checkout URL
                    checkout_payload = {
                        'accNum': accNum,
                        'itemPrice': item["price"],
                        'access_token': Token
                    }
                    checkout_headers = {'Content-Type': 'application/json'}

                    # Send the cart checkout request
                    resp = requests.post(
                        checkout_url,
                        json=checkout_payload,
                        headers=checkout_headers,
                        verify=False,  # Disable SSL certificate verification (not recommended in production)
                        allow_redirects=False,
                        stream=False
                    )

                    if resp.status_code == 200:
                        print(f"Successful checkout for item: {item['name']}")
                        accBal -= item["price"]
                    else:
                        print(f"Failed checkout for item: {item['name']}. Status Code: {resp.status_code}")
                else:
                    print(f"Insufficient balance for item: {item['name']}")
        
        except requests.exceptions.ConnectionError as e:
            print("Connection error during cart checkout: %s" % e)
        except Exception as e:
            print("An error occurred during cart checkout: %s" % e)


    






    





def main():
    numProcesses = 1
    queueList = []
    processList = []
    for x in range(0,numProcesses):
        q = Queue()
        queueList.append(q)
        p = Process(target=Simulation(x*2).runTest, args=(q,))
        processList.append(p)

    startTime = datetime.datetime.now()
    for p in processList:
        p.start()

    totalTime = 0
    for q in queueList:
        timeElapsed = q.get()
        totalTime+=timeElapsed
        #print "Result", timeElapsed

    endTime = datetime.datetime.now()
    secondsPassed = float((endTime - startTime).total_seconds())
    
    # operationsPerSec = float(NUM_PAYMENTS_PER_CLIENT*numProcesses / totalTime)
    # print "Transactions per second (%d/%f): %f" \
    #      % (NUM_PAYMENTS_PER_CLIENT*numProcesses, totalTime, operationsPerSec)
    operationsPerSec = float(NUM_ORDER_PER_CLIENT*numProcesses / secondsPassed)
    print ("Transactions per second (%d/%f): %f" \
         % (NUM_ORDER_PER_CLIENT*numProcesses, secondsPassed, operationsPerSec))

    for p in processList:
        p.join()




if __name__ == "__main__":
    main()
    

