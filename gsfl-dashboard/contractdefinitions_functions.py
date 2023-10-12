import json
import requests       
import uuid                
from flask import Flask  # , redirect
from flask import flash
from flask import request
from json2html import *
#from ml.tools import XML
from assets_functions import getAssets, convert_json_to_assets
from policiy_functions import getPolicies, convert_json_to_policies

def convert_json_to_contractDefinitions(json_data):
    contractDefinitions = []
    for item in json_data:
        contractDefinition = {
            #"name": item["properties"]["asset:prop:name"],
            "id": item["id"],
            "asset": item["criteria"]
        }
        contractDefinitions.append(contractDefinition)

    return contractDefinitions

def getAssetList(path='http://localhost:9191'):
    assetList = getAssets(path)
    print(assetList)
    return assetList

def getPolicyList(path='http://localhost:9191'):
    policyList = getPolicies(path)
    return policyList


def getContractDefinitions(path='http://localhost:9191'):
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    response = requests.get(f'{path}/api/v1/data/contractdefinitions', headers=headers)
    print(response.json())
    response_json_formatted = json.dumps(response.json(), indent=4)
    #print(response_json_formatted)
    
    json_data = json.loads(response_json_formatted)
    #contractDefinitions = convert_json_to_contractDefinitions(json_data)
    #print(contractDefinitions)

    contractDefinitions = json_data
    return contractDefinitions
        



def createContractDefinition(name, selectedAssets, selectedAccessPolicy, selectedContractPolicy, validity, path='http://localhost:9191'):
    contractsDefinitionId = name.replace(" ", "-")
    response = createNewContractDefinition(contractsDefinitionId, selectedAssets, selectedAccessPolicy, selectedContractPolicy, validity, path)
    #print(selectedPolicy)
    if response:
        flash(f"Contract Definition successfully created", 'success')
    else: 
        flash(f"Contract Definition couldn't be created", 'danger')
           
    

def createNewContractDefinition(contractsDefinitionId, selectedAssets, selectedAccessPolicy, selectedContractPolicy, validity, path='http://localhost:9191'):  # EDC
# Create new Artifact for complete FML4.0 Dataset in IDS Provider Connector
    
    body = {
    
    "accessPolicyId": f"{selectedAccessPolicy}",
    "contractPolicyId": f"{selectedContractPolicy}",
    "criteria": [
        {
            "operandLeft": "asset:prop:id",
            "operator": "=",
            "operandRight": selectedAssets
        }
    ],
    "id": f"{contractsDefinitionId}",
    "validity": validity
    }
    
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    response = requests.post(f'{path}/api/v1/data/contractdefinitions', json=body, verify=False, headers=headers)
    response_json = response.json()
    contractID = {"id": contractsDefinitionId, "content": response_json}

    return contractID



def deleteContractDefinition(contractDefinition_id, path='http://localhost:9191'):
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    response = requests.delete(f'{path}/api/v1/data/contractdefinitions/{contractDefinition_id}', verify=False, headers=headers)
    print(contractDefinition_id)
    if response.ok:
        flash(f"Contract Definition was deleted successfully.", 'success') 
    else:
        flash("Failed to delete Contract Definition.", 'danger')



if __name__ == "__main__":
    list = getAssetList()
    #print(list)
    #print(type(list))
    # for item in list:
    #     right = item['asset'][0]['operandRight']
    #     print(right)