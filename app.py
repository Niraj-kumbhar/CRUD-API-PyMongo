from flask import Flask, jsonify, Response, request
import pymongo
import json
from bson.objectid import ObjectId
from bson import json_util

app = Flask(__name__)

class nullResponseErr(Exception):
    pass

try:
    mongo = pymongo.MongoClient(
        host="localhost", 
        port=27017, 
        serverSelectionTimeoutMS=1000)
    db = mongo.newdb
    mongo.server_info()

except:
    print("ERROR - Cannot connect to db")


##############Create User#################
@app.route("/users", methods=["POST"])
def create_user():
    try:
        user= {"name":request.form["name"],"username":request.form["username"]}
        dbResponse = db.users.insert_one(user)
        #print(f"normal: {dbResponse}")
        #print(f"id: {dbResponse.inserted_id}")

        return Response(
            response=json.dumps(
                {"message":"user created", 
                "id":f"{dbResponse.inserted_id}"}),
            status=200,
            mimetype="application/json"
        )
    except pymongo.errors.DuplicateKeyError:
        #print(ex)
        return Response(
            response=json.dumps(
                {"message":"username already exists, try different"}),
            status=500,
            mimetype="application/json"
        )
    
    except Exception as ex:
        #print(ex)
        return Response(
            response=json.dumps(
                {"message":"user not created"}),
            status=500,
            mimetype="application/json"
        )

################Read User###############

@app.route("/users/<u>", methods=["GET"])
def get_some_users(u):
    try:
        #user= {"username":request.form["username"]}
        user= {"username":u}
        #print(f"user: {user}")
        #user = str(user)
        data = db.users.find_one(user)
        #print(f"******\ndata:\n {data}")
        # for user in data:
        if data==None:
            raise nullResponseErr
        data = json.dumps(data,  default=str)

        return Response(
            response=data,
            status=200,
            mimetype="application/json"
        )
    except nullResponseErr:
        #print(f"Exeception: User not exists")
        return Response(
            response=json.dumps(
                {"message":"User not exists"}),status=500,mimetype="application/json")

    except Exception as ex:
        #print(f"Exeception: {ex}")
        return Response(
            response=json.dumps(
                {"message":"cannot read users"}),status=500,mimetype="application/json")

#################Update user##############
@app.route("/users/<u>", methods=["PATCH"])
def update_users(u):
    try:
        
        user= {"username":u}
        update = {"name":request.form["name"]}
        data = db.users.update_one(user,{"$set": update}, upsert=False)
        raw = dict(data.raw_result)
        if raw['updatedExisting'] ==False:
            return Response(
                response=json.dumps(
                    {"message":"user not exists"}),
                status=500,
                mimetype="application/json"
            ) 
        
        if data.modified_count==1:
            return Response(
                response=json.dumps(
                    {"message":"user info updated",
                    "Inserted":data.acknowledged}),
                status=200,
                mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps(
                    {"message":"nothing to update"}),
                status=200,
                mimetype="application/json"
            )

    except Exception as ex:
        print(f"Exeception: {ex}")
        return Response(
            response=json.dumps(
                {"message":"Error cannot read users"}),status=500,mimetype="application/json")

#################Delete user##############
@app.route("/users/<u>", methods=["DELETE"])
def delete_users(u):
    try:
        user= {"username":u}
        data = db.users.delete_one(user)

        if data.deleted_count ==0:
            return Response(
                response=json.dumps(
                    {"message":"user not exists",
                    "Deleted":data.deleted_count}),
                status=500,
                mimetype="application/json"
            )

        else:
            return Response(
                response=json.dumps(
                    {"message":"user deleted",
                    "Deleted":data.deleted_count}),
                status=200,
                mimetype="application/json"
                )
        
    except Exception as ex:
        #print(f"Exeception: {ex}")
        return Response(
            response=json.dumps(
                {"message":"Error cannot read users"}),status=500,mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True, port=8000)