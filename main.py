## -----------------------------------------##
## Important libraries used in this project ##
## -----------------------------------------##
from fastapi import FastAPI, Header, Depends, HTTPException, Response, Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, validator
import uuid
from typing import List
import csv
import pymongo
import bson
import json
import uvicorn

## -----------------------------------------##
##              Fast API Object             ##
## -----------------------------------------##
app = FastAPI()


## -----------------------------------------##
##              Global MongoDB              ##
## -----------------------------------------##
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["candidate_db"]


## -----------------------------------------##
##                API TESTOR                ##
## -----------------------------------------##
@app.get("/")
async def root():
    return {"message": "Hello World! API is running"}


## -----------------------------------------##
##              Global MongoDB              ##
## -----------------------------------------##
class User(BaseModel):
    """
    This is User Collection which will be used with required end point
    Create /user End-point to populate user collection with these fields:
    - first_name
    - last_name
    - email
    - UUID
    
    Arguments: Inherited from BaseModel
    Return: Nothing
    """
    first_name: str
    last_name: str
    email: str

        
## -----------------------------------------##
##          Candidate Collection            ##
## -----------------------------------------##
class Candidate(BaseModel):
    """
    Create /candidate CRUD End-points to add, update, delete, and view the candidate profile, the profile should have these fields:
    
    Note: Validator is used to check gender values
    
    Arguments: Inherited from BaseModel
    Return: Nothing
    """
    first_name: str
    last_name: str
    email: str
    UUID: str
    career_level: str
    job_major: str
    years_of_experience: int
    degree_type: str
    skills: List[str]
    nationality: str
    city: str
    salary: float
    gender: str
        
    @validator("gender")
    def gender_check(cls, v):
        if v not in ["Male", "Female", "Not Specific"]:
            raise ValueError("Gender must be Male, Female, or Not Specific")
        return v

## -----------------------------------------##
##          Create User Collection          ##
## -----------------------------------------##
@app.post("/user")
async def create_user(user: User):
    """
    This is required End Point
    Create /user End-point to populate user collection with these fields:
    - first_name
    - last_name
    - email
    - UUID
    
    Argument: user collection
    Return: user_object (user information)
    """
    user_id = str(uuid.uuid1())
    user_data = user.dict()
    user_data["user_id"] = user_id
    result = db.users.insert_one(user_data)
    return {"user_id": str(result.inserted_id), "user": user.dict()}


## -----------------------------------------##
##     Create Candidate Collection          ##
## -----------------------------------------##
@app.post("/candidate")
async def create_candidate(candidate: Candidate, authorization: str = Header(None)):
    
    """
    This function is used to create candidate and add to collection
    This can only be performed by Authorized users
    
    Argument: 
        user_id
        candidate collection
    Return: message or exception
    """
        
    # Connect to the database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["candidate_db"]
    users = db["users"]
    candidates = db["candidates"]
    
    # Check if the user is authorized
    user = users.find_one({"user_id": authorization})
    if not user:
        raise HTTPException(status_code=400, detail="Not authorized")
    
    # Insert the candidate into the database
    try:
        candidates.insert_one(candidate.dict())
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Candidate created successfully"}


## -----------------------------------------##
##         Return all Candidates            ##
## -----------------------------------------##
@app.get("/all-candidates")
async def get_all_candidates(query: str = None, field: str = None, authorization: str = Header(None)):
    """
    This function is used to return all candidates using keywords, one or more fields
    This can only be performed by Authorized users
    
    Argument: 
        query: textual data
        user_id for auth
    Return: List of all candidates
    """
        
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["candidate_db"]
    candidates = db["candidates"]
    users = db['users']
    
    candidates.create_index([("skills", "text")])
    
    # Check if the user is authorized
    user = users.find_one({"user_id": authorization})
    
    if not user:
        raise HTTPException(status_code=400, detail="Not authorized")
       
    query_filter = {}
    if query:
        query_filter = {"$text": {"$search": query}}
    
    all_candidates = []
    for candidate in candidates.find(query_filter):
        del candidate["_id"]
        all_candidates.append(candidate)

    return {"candidates": all_candidates}



## -----------------------------------------##
##         Search Candidate by ID           ##
## -----------------------------------------##
@app.get("/candidate/{candidate_id}")
async def read_candidate(candidate_id: str, authorization: str = Header(None)):
    """
    This function is used to return candidate using ID
    This can only be performed by Authorized users
    
    Argument: 
        candidate_id
        user_id for auth
    Return: candidate
    """
    # Connect to the database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["candidate_db"]
    users = db["users"]
    candidates = db["candidates"]
    
    # Check if the user is authorized
    user = users.find_one({"user_id": authorization})
    
    if not user:
        raise HTTPException(status_code=400, detail="Not authorized")
    
    # Retrieve the candidate from the database
    candidate = candidates.find_one({"_id": bson.ObjectId(candidate_id)})
    
    candidate['_id'] = str(candidate['_id'])
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate


## -----------------------------------------##
##         Update Candidate by ID           ##
## -----------------------------------------##
@app.put("/candidate/{candidate_id}")
async def update_candidate(candidate_id: str, request: Request, authorization: str = Header(None)):
    """
    This function is used to update candidate's fields using ID
    This can only be performed by Authorized users
    
    Argument: 
        candidate_id
        fields want to update
        user_id for auth
    Return: Response Message
    """
    # Connect to the database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["candidate_db"]
    users = db["users"]
    candidates = db["candidates"]
    
    # Check if the user is authorized
    user = users.find_one({"user_id": authorization})
    js = await request.body()
    
    if not user:
        raise HTTPException(status_code=400, detail="Not authorized")
    
    # Update the candidate in the database
    try:
        result = candidates.update_one({"_id": bson.ObjectId(candidate_id)}, {"$set": json.loads(js)})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=400, detail=str(e))


## -----------------------------------------##
##         Delete Candidate by ID           ##
## -----------------------------------------##
@app.delete("/candidate/{candidate_id}")
async def delete_candidate(candidate_id: str, authorization: str = Header(None)):
    """
    This function is used to delete candidate using ID
    This can only be performed by Authorized users
    
    Argument: 
        candidate_id
        user_id for auth
    Return: Message or Exception
    """
    # Connect to the database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["candidate_db"]
    users = db["users"]
    candidates = db["candidates"]
    
    # Check if the user is authorized
    user = users.find_one({"user_id": authorization})
    if not user:
        raise HTTPException(status_code=400, detail="Not authorized")
    
    # Delete the candidate from the database
    try:
        result = candidates.delete_one({"_id": bson.ObjectId(candidate_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=400, detail="Candidate not found")
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Candidate deleted successfully"}


## -----------------------------------------##
##       Get list of all candidates - CSV   ##
## -----------------------------------------##
@app.get("/generate-report")
async def generate_report():
    
    """
    This function is used to download CSV of records
   
    Argument: None 
    Return: Download CSV File or View Records
    """
        
    fieldnames = ['first_name', 'last_name', 'email', 'UUID', 'career_level', 'job_major', 'years_of_experience', 'degree_type', 'skills', 'nationality', 'city', 'salary', 'gender']
    with open('candidates_report.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        # Add code here to retrieve all candidate data from database
        
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["candidate_db"]
        users = db["users"]
        candidates = db["candidates"]

        # Retrieve all candidates
        all_candidates = []
        for candidate in candidates.find():
            del candidate["_id"]
            del candidate["UUID"]
            candidate["skills"] = ", ".join(candidate['skills'])
            writer.writerow(candidate)
        
    # Return the generated CSV file
    with open("candidates_report.csv", mode='rb') as file:
        response = Response(content=file.read(), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename = candidates_report.csv"
        return response
    
## uvicorn main:app --reload

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)