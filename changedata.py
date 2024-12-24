import json

# from src.DBFeeder import get_demodata
# data = get_demodata()

with open("./systemdata.json", "r", encoding="utf-8") as f:
    data = json.load(f)

users = data["users"]
for user in users:
    user["rbacobject_id"] = user["id"]

groups = data["groups"]
for group in groups:
    group["rbacobject_id"] = group["id"]    

roles = data["roles"]
for role in roles:
    role["rbacobject_id"] = role["group_id"]

with open("./systemdata.2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

