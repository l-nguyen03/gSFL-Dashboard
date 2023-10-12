import json
import requests       
import uuid                
from flask import Flask  # , redirect
from flask import flash
from flask import request
from json2html import *
#from ml.tools import XML


def convert_json_to_policies(json_data):
    policies = []
    for item in json_data:
        policy = {
            "permissions": item["policy"]["permissions"],
            "prohibitions": item["policy"]["prohibitions"],
            "obligations": item["policy"]["obligations"],
            "id": item["id"]
        }
        #print(policy)
        policies.append(policy)
    return policies


def getPolicies(path='http://localhost:9191'):
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    response = requests.get(f'{path}/api/v1/data/policydefinitions', headers=headers)
    #response_json_formatted = json.dumps(response.json(), indent=4)
    #json_data = json.loads(response_json_formatted)
    json_data = response.json()
    policies = convert_json_to_policies(json_data)
    
    return policies
        


def createPolicy(path='http://localhost:9191'):
    policy = {}

    name = request.form.get('policyNameInput')
    provider = request.form.get('assignerUrl')
    consumer = request.form.get('assigneeUrl')
    city_names = request.form.get('CityNames')
    partner_names = request.form.get('partnersNames')

    policy["edctype"] = "dataspaceconnector:permission"
    policy["uid"] = None
    policy["action"] = {"type":"USE", "includedIn":None, "constraint":None}
    policy["constraints"] = []
    policy["duties"] = []

    if provider != "":
        policy["assigner"] = provider
    else:
        policy["assigner"] = None
    
    if consumer != "":
        policy["assignee"] = consumer
    else:
        policy["assignee"] = None
    
    if city_names != "":
        city_names = city_names.replace(" ", "")
        city_names = city_names.split("/")
        if len(city_names) == 1: 
            operator = "EQ"
            city_name = city_names[0]
            city_constraint = {"edctype":"AtomicConstraint", "leftExpression": {"edctype": "dataspaceconnector:literalexpression", 
                                         "value":"city"}, "rightExpression": {"edctype": "dataspaceconnector:literalexpression", "value": city_name},
                                         "operator": operator}
        else:
            operator = "IN"
            city_constraint = {"edctype":"AtomicConstraint", "leftExpression": {"edctype": "dataspaceconnector:literalexpression", 
                                         "value":"city"}, "rightExpression": {"edctype": "dataspaceconnector:literalexpression", "value": city_names}, 
                                         "operator": operator}
        policy["constraints"].append(city_constraint)
    
    if partner_names != "":
        partner_names = partner_names.replace(" ", "")
        partner_names = partner_names.split("/")
        if len(partner_names) == 1: 
            operator = "EQ"
            partner_name = partner_names[0]
            partner_constraint = {"edctype":"AtomicConstraint", "leftExpression": {"edctype": "dataspaceconnector:literalexpression", 
                                         "value":"partner"}, "rightExpression": {"edctype": "dataspaceconnector:literalexpression", "value": partner_name},
                                         "operator": operator}
        else:
            operator = "IN"
            partner_constraint = {"edctype":"AtomicConstraint", "leftExpression": {"edctype": "dataspaceconnector:literalexpression", 
                                         "value":"partner"}, "rightExpression": {"edctype": "dataspaceconnector:literalexpression", "value": partner_names}, 
                                         "operator": operator}
        policy["constraints"].append(partner_constraint)
    
    response = createNewPolicy(name, policy, path)
    if response:
        flash(f"Policy {name} successfully created", 'success')
    else:
        flash(f"Policy {name} couldn't be created", 'danger')
           

def createNewPolicy(name, policy_content, path='http://localhost:9191'):
    policy = [policy_content]
    body = {
        "id": f"{name}",
        "policy": {
            "permissions": policy
        }
    }
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    response = requests.post(f'{path}/api/v1/data/policydefinitions', json=body, verify=False, headers=headers)
    return response 



def deletePolicy(policy_id, path='http://localhost:9191'):
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    response = requests.delete(f'{path}/api/v1/data/policydefinitions/{policy_id}', verify=False, headers=headers)

    if response.ok:
        flash(f"Policy was deleted successfully.", 'success') 
    else:
        flash("Failed to delete Policy.", 'danger')

if __name__ == "__main__":
    createPolicy()