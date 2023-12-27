from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from decouple import config
from pymongo import ReturnDocument

app = FastAPI()

# CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB Atlas
client = MongoClient(config("DATABASE_URL"))

# Select the database and collection
db = client[config("DB_NAME")]
collection = db[config("COLLECTION_NAME")]


# Pydantic model for your JSON data
class Item(BaseModel):
    image_string: str
    identification_number: str
    name: str
    last_name: str
    date_of_birth: str
    date_of_issue: str
    date_of_expiry: str
    status: bool


# CRUD Operations
@app.post("/data")
async def create_item(item: Item):
    received_image = item.dict()["image_string"]
    check = collection.find_one({"image_string": received_image})
    if check:
        return "Image Already Exists"
    result = collection.insert_one(item.dict())
    item_id = result.inserted_id
    return {"id": str(item_id)}


@app.get("/data")
async def read_item():
    # Retrieve the item from MongoDB
    cursor = collection.find()
    result = []
    for document in cursor:
        trimmed_document = {}
        for key in document:
            if key != "_id":
                trimmed_document[key] = document[key]
        result.append(trimmed_document)
    return {"list_of_records": result}


@app.put("/data")
async def update_item(item: Item):
    # Update the item in MongoDB
    cursor = collection.find_one_and_replace({"image_string": item.dict()["image_string"]}, item.dict(), return_document=ReturnDocument.AFTER)
    if cursor:
        return "Update Succesful"
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/data")
async def delete_item(item: Item):
    # Delete the item from MongoDB
    result = collection.delete_one(item.dict())
    if result.deleted_count == 1:
        return {"status": "success", "message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)