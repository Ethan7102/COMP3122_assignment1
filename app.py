from flask import Flask, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from bson.json_util import loads
import os
import pymongo
from urllib.parse import quote_plus

# get mongodb's username, pwd, host name and port number from environment variables
username = os.getenv('MONGO_USERNAME')
password = os.getenv('MONGO_PASSWORD')
host = os.getenv('MONGO_SERVER_HOST')
port = os.getenv('MONGO_SERVER_PORT')

# The flask API will print an error message and exit if the environment variables about MongoDB are not provided
if username is None or password is None or host is None or port is None:
    print('The environment variables about MongoDB are not provided.')
    exit()

# set url
uri = "mongodb://%s:%s@%s:%s" % (quote_plus(username),
                                 quote_plus(password), quote_plus(host), quote_plus(port))

# connect mongodb
try:
    client = MongoClient(uri)
    client.server_info()  # connect to mongoDB to get the server info
# MongoDB will be accessed unsuccessfully if the environment variables about MongoDB are incorrect.
except pymongo.errors.ServerSelectionTimeoutError:
    print('Access failed. The environment variables about MongoDB are incorrect or the MongoDB server is not available.')
    exit()

# get the University DB
db = client['university']
students = db['student']
takes = db['takes']

app = Flask(__name__)

# Return a JSON object with my Student ID and Name.
@app.route('/me', methods=['GET'])
def get_me():
    # return my student information by JSON format
    return jsonify({"student_id": "20035673D", "name": "Wong Ming Yuen"}), 200

# Return a JSON object with all the students’ attributes
@app.route('/students', methods=['GET'])
def get_students():
    # get all student data, disable _id coolumn and sort the students in ascending order of student_id
    cursor = students.find({}, {'_id': 0}).sort('student_id', 1)
    # iterate over to get a list of dicts
    dicts = [doc for doc in cursor]
    if len(dicts):  # if it is not empty
        return jsonify(dicts), 200
    else:  # print error message if no student records are found
        return jsonify({'error': 'not found'}), 404

# Return a JSON object with the specified student
@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    # get student data by student ID, disable _id coolumn
    cursor = students.find({'student_id': {'$eq': student_id}}, {'_id': 0})
    # iterate over to get a list of dicts
    dicts = [doc for doc in cursor]
    if len(dicts):  # if it is not empty
        return jsonify(dicts), 200
    else:  # print error message if /no student with the specified student ID is found
        return jsonify({'error': 'not found'}), 404

# Return the attributes of all the students with the courses they are taking
@app.route('/takes', methods=['GET'])
def get_students_with_courses():
    # aggregate two collection, the students were sorted in ascending order of student_id, the courses were sorted in ascending order of course_id
    cursor = students.aggregate([{'$lookup': {'from': 'takes', 'let': {'student_id': '$student_id'}, 'pipeline': [{'$match': {'$expr': {'$and': [{'$eq': ['$student_id', '$$student_id']}]}}}, {
                                '$project': {'_id': 0, 'student_id': 0}}, {'$sort': {'course_id': 1}}], 'as': 'student_takes'}}, {'$project': {'_id': 0}}, {'$sort': {'student_id': 1}}])
    # iterate over to get a list of dicts
    dicts = [doc for doc in cursor]
    if len(dicts):  # if it is not empty
        return jsonify(dicts), 200
    else:  # print error message if no student records are found
        return jsonify({'error': 'not found'}), 404

# Return a JSON object for the specified student
@app.route('/takes/<student_id>', methods=['GET'])
def get_student_with_courses(student_id):
    # aggregate two collection, select the student by student_id,the students were sorted in ascending order of student_id, the courses were sorted in ascending order of course_id
    cursor = students.aggregate([{'$match': {'student_id': student_id}}, {'$lookup': {'from': 'takes', 'let': {'student_id': '$student_id'}, 'pipeline': [{'$match': {'$expr': {'$and': [{'$eq': [
                                '$student_id', '$$student_id']}]}}}, {'$project': {'_id': 0, 'student_id': 0}}, {'$sort': {'course_id': 1}}], 'as': 'student_takes'}}, {'$project': {'_id': 0}}, {'$sort': {'student_id': 1}}])
    # iterate over to get a list of dicts
    dicts = [doc for doc in cursor]
    if len(dicts):  # if it is not empty
        return jsonify(dicts), 200
    else:  # print error message if no student record with the specified student ID is found
        return jsonify({'error': 'not found'}), 404


# start flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15000, debug=True)