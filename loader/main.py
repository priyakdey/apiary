from collections import defaultdict
from dataclasses import dataclass
import json
from pprint import pprint
from re import match
from typing import Optional

import pymongo


@dataclass
class Description:
    """
        Description is a value class representing the list of APIs
        and its metadata for each category
    """
    api: str
    description: str
    auth: str
    https: str
    cors: str
    
    @staticmethod
    def parse_from_line(line: str) -> Optional["Description"]:
        if line.startswith("| API") or line.startswith("|:"):
            return None
        l = line.split("|")
        api   = Description._parse_api(l[1].strip(" ").strip("`").strip("\n"))
        desc  = l[2].strip(" ").strip("`").strip("\n")
        auth  = l[3].strip(" ").strip("`").strip("\n")
        https = l[4].strip(" ").strip("`").strip("\n")
        cors  = l[5].strip(" ").strip("`").strip("\n")

        return Description(api, desc, cors, auth, cors)
   
    @staticmethod
    def _parse_api(line: str) -> str:
        pattern = r"^\[.*\]\((.*)\)$"
        m = match(pattern, line)
        if m is not None:
            return m.groups()[0]
        print("ERROR: Something is wrong....", line)
        exit(1) 
    
    def toJSON(self):
        return self.__dict__ 


class DescriptionEncoder(json.JSONEncoder):
    """
        DescriptionEncoder is the custom json encoder for the class
        Description
    """
    def default(self, obj):
        if isinstance(obj, Description):
            return {key: str(obj.__dict__[key]) for key in obj.__dict__}

        return json.JSONENcoder.default(self, obj)

categories: dict[str, list[Description]] = defaultdict() 


with open("./README.md") as fd:
    category: str | None = None
    for line in fd.readlines():
        if line.startswith("### "):
            category = line[4:].strip()
        elif line.startswith("|"):
            if category not in categories:
                categories[category] = []
            desc = Description.parse_from_line(line)
            if desc is not None:
                categories[category].append(desc)

print("Dumping data into data.json...")

with open("data.json", "w") as fd:
    json.dump(categories, fd, cls=DescriptionEncoder, indent=4)

print("Dumping data into mongodb...")

# TODO: config driven 
db_url = "mongodb://root:password@localhost:27017"
client = pymongo.MongoClient(db_url)
db = client.public_api_data_db
collection = db.categories

if collection.count_documents({}) == 0:
    print("Inserting all categories")
    collection.insert_one({"categories": list(categories.keys())})

for key, value in categories.items():
    collection_name = key.replace(" & ", "_").replace(" ", "_").lower()
    collection = db[collection_name]
    if collection.count_documents({}) != 0:
        continue

    data: list[str] = []
    for d in value:
        data.append(d.toJSON())
    
    print(f"Inserting data for {key}")
    collection.insert_one({"data": data})

