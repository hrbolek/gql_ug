import json

# from src.DBFeeder import get_demodata
# data = get_demodata()

with open("./systemdata.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def setAttributeOnItem(item, sourceAttributeName, destinationAttributeName):
    item[destinationAttributeName] = item[sourceAttributeName]

def setAttributeOnCollection(collection, sourceAttributeName, destinationAttributeName):
    for item in collection:
        setAttributeOnItem(item, sourceAttributeName, destinationAttributeName)

users = data["users"]
setAttributeOnCollection(users, "id", "rbacobject_id")
# for user in users:
#     user["rbacobject_id"] = user["id"]

groups = data["groups"]
setAttributeOnCollection(groups, "id", "rbacobject_id")
# for group in groups:
#     group["rbacobject_id"] = group["id"]    

roles = data["roles"]
for role in roles:
    role["rbacobject_id"] = role["group_id"]

forms = data["forms"]
setAttributeOnCollection(forms, "rbacobject", "rbacobject_id")
setAttributeOnCollection(forms, "rbacobject", "createdby_id")
setAttributeOnCollection(forms, "rbacobject", "changedby_id")
formsections = data["formsections"]
setAttributeOnCollection(formsections, "rbacobject", "rbacobject_id")
formparts = data["formparts"]
setAttributeOnCollection(formparts, "rbacobject", "rbacobject_id")
formitems = data["formitems"]
setAttributeOnCollection(formitems, "rbacobject", "rbacobject_id")
formrequests = data["formrequests"]
setAttributeOnCollection(formrequests, "rbacobject", "rbacobject_id")
formhistories = data["formhistories"]

formindex = {form["id"]: form for form in forms}
for history in formhistories:
    form = formindex[history["form_id"]]
    history["rbacobject_id"] = form["rbacobject_id"]
    history["createdby_id"] = form["rbacobject_id"]
    history["changedby_id"] = form["rbacobject_id"]



with open("./systemdata.2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

