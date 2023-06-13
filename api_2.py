from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, Api
import mysql.connector
from mysql.connector import Error
import requests

app = Flask(__name__)
api = Api(app)

def ibancontrole(iban):
    iban.replace(" ","")
    if iban[:2] != "UK":    # vervang dit coorde juiste landcode
        return False
    if iban[2:6] != "PECI": # vervang dit voor de juiste iban 
        return False
    return True

try:
    connection = mysql.connector.connect(host= '145.24.222.207',
                                         database='bank',
                                         user='root' , 
                                         password='QpBB37k#',
                                         port=8000)

    cursor = connection.cursor()

    if connection.is_connected():

        class balance(Resource):
            def post(self):
                content = request.get_json(silent=True)
                account = content["account"] 
                if ibancontrole(account):
                    cursor.execute(f"SELECT g.balans FROM geld g, rekening r WHERE g.rekeningnr = r.rekeningnr AND r.rekeningnr = '{account}'")
                    record = cursor.fetchall()
                    message = jsonify(balance = record[0][0])
                    resp = make_response(message, 200)
                    return resp   
                else:
                    headers = {"Content-Type": "application/json"}
                    r = requests.post("https://145.24.222.51:8443/api/v1/route-data", verify = False, json={'head': { "fromCtry" : "UK" , "fromBank" : "PECI" , "toCtry" : account[:2] , "toBank" : account[2:6]}, 'body': { "account" : account}})
                    return r
        
        class withdraw(Resource):
            def post(self):
                content = request.get_json(silent=True)
                account = content["account"]
                amount = content["balance"]
                pincode = content["pincode"]
                if ibancontrole(account):
                    # haal de balans op en kijk of het pin bedrag er af zou kunnen
                    cursor.execute(f"SELECT g.balans, r.pincode FROM geld g, rekening r WHERE g.rekeningnr = r.rekeningnr AND r.rekeningnr = '{account}'")
                    record = cursor.fetchall()
                    if int(pincode) != int(record[0][1]):
                        message = jsonify(message = "pincode incorrect")
                        resp = make_response(message, 401)
                        return resp
                    # als het pinbedrag er af kan dan voeren we de update uit.               
                    if(int(record[0][0]) > int(amount)):
                        # print(int(record[0][0]) - amount)
                        cursor.execute(f"UPDATE geld SET balans = {int((int(record[0][0]) - int(amount)))} WHERE rekeningnr = '{account}';")
                        connection.commit()
                        message = jsonify(message = "geld opnemen gelukt")
                        resp = make_response(message, 200)
                        return resp
                    else:
                    # als het pinbedrag er niet af kan dan is de response anders, zodanig dat het aangeeft dat het pinbedrag er niet afkan
                        message = jsonify(message = "saldo te laag")
                        resp = make_response(message, 406)
                        return resp
                else:
                    headers = {"Content-Type": "application/json"}
                    r = requests.post("https://145.24.222.51:8443/api/v1/route-data", verify = False, json={'head': { "fromCtry" : "UK" , "fromBank" : "PECI" , "toCtry" : account[:2] , "toBank" : account[2:6]}, 'body': { "account" : account, "pincode" : pincode, "balance" : amount}}) #NOOB server
                    return r
        
        class login(Resource):
            def post(self):
                content = request.get_json(silent=True)
                account = content["account"]
                pincode = content["pincode"]
                print(pincode)
                if ibancontrole(account):
                    cursor.execute(f"SELECT pincode FROM rekening WHERE rekeningnr = '{account}'")
                    record = cursor.fetchall()
                    if not record:
                        message = jsonify(message = "verkeerde invoer")
                        resp = make_response(message, 403)
                        return resp
                    elif int(pincode) == int(record[0][0]):
                        message = jsonify(message = "pincode correct", status = True, pincode = f"{pincode}")
                        resp = make_response(message, 200)
                        return resp
                    else:
                        message = jsonify(message = "pincode incorrect", status = False, pincode = "0000")
                        resp = make_response(message, 401)
                        return resp
                else:
                    headers = {"Content-Type": "application/json"}
                    r = requests.post("https://145.24.222.51:8443/api/v1/route-data", verify = False, json={'head': { "fromCtry" : "UK" , "fromBank" : "PECI" , "toCtry" : account[:2] , "toBank" : account[2:6]}, 'body': { "account" : account, "pincode" : pincode}})
                    return r

except Error as e:
    print("Error while connecting to MySQL", e)


api.add_resource(login, '/login')
api.add_resource(balance, '/balance')
api.add_resource(withdraw, '/withdraw')


if __name__ == "__main__":
    app.run(host="145.24.222.207")