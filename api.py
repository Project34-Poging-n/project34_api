from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, Api
import mysql.connector
from mysql.connector import Error
import requests

app = Flask(__name__)
api = Api(app)

# def ibancontrole(iban):
#     iban.replace(" ","")
#     if iban[:2] != "NL":    # vervang dit coorde juiste landcode 
#         return False
#     if iban[4:8] != "RABO": # vervang dit voor de juiste iban 
#         return False
#     return True


try:
    connection = mysql.connector.connect(host= '145.24.222.207',
                                         database='bank',
                                         user='root' , 
                                         password='QpBB37k#',
                                         port=8000)

    cursor = connection.cursor()

    print(connection.is_connected())

    if connection.is_connected():

        class balance(Resource):
            def get(self, account): 
                # if ibancontrole(account):
                    #content = request.get_json(silent=True)
                    #print(content["message"])
                    cursor.execute(f"SELECT g.balans FROM geld g, rekening r WHERE g.rekeningnr = r.rekeningnr AND r.rekeningnr = '{account}'")
                    record = cursor.fetchall()
                    message = jsonify(balance = record[0][0])
                    resp = make_response(message, 200)
                    return resp   
                # else:
                #     r = requests.post("145.24.222.82:8443/test") #NOOB server
                #     print(r)
        
        class withdraw(Resource):
            def post(self, account):
                # if ibancontrole(account):
                    # haal de balans op en kijk of het pin bedrag er af zou kunnen
                    content = request.get_json(silent=True)
                    print(content)
                    amount = content["balance"]
                    cursor.execute(f"SELECT g.balans FROM geld g, rekening r WHERE g.rekeningnr = r.rekeningnr AND r.rekeningnr = '{account}'")
                    record = cursor.fetchall()
                    
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
                # else:
                #     r = requests.post("145.24.222.82:8443/test") #NOOB server
                #     print(r)
        
        class login(Resource):
            def get(self, account, pincode):
                #if ibancontrole(account):
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
                # else:
                #     r = requests.post("145.24.222.82:8443/test") #NOOB server
                #     print(r)
                #     if r.ok():
                #         return {r.json()}, 200
                #     else:
                #         return {}, 404   

except Error as e:
    print("Error while connecting to MySQL", e)


api.add_resource(login, '/login/<string:account>/<string:pincode>')
api.add_resource(balance, '/balance/<string:account>')
api.add_resource(withdraw, '/withdraw/<string:account>')


if __name__ == "__main__":
    app.run(host="145.24.222.207")