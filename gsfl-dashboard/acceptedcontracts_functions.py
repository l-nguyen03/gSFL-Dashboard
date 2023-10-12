import json
import requests       
import uuid                
from flask import Flask  # , redirect
from flask import flash
from flask import request
from datetime import datetime
import time
#from json2html import *
#from ml.tools import XML


def convert_json_to_accepted(json_contracts):
    ac_contracts = []
    for contract in json_contracts:
        accepted = {
            #"name": item["properties"]["asset:prop:name"],
            "id": contract["id"],
            "assetId": contract["assetId"],
            "signdate": datetime.fromtimestamp(contract["contractSigningDate"]),
            "startdate": datetime.fromtimestamp(contract["contractStartDate"]),
            "enddate": datetime.fromtimestamp(contract["contractEndDate"])
        }
        ac_contracts.append(accepted)

    return ac_contracts


def getAccepted(path='http://localhost:9191'):
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    response = requests.get(f'{path}/api/v1/data/contractagreements', headers=headers)
    response_json_formatted = json.dumps(response.json(), indent=4)
    json_contracts = json.loads(response_json_formatted)
    ac_contracts = convert_json_to_accepted(json_contracts)
    print(ac_contracts)
    return ac_contracts

def transfer_status(path='http://localhost:9191'):
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    response = requests.get(f'{path}/api/v1/data/transferprocess', headers=headers)
    response = response.json()
    #print(response)
    return response

def transferNewContract(acceptedContract_id, assetID,  path='http://localhost:9191'):  # EDC
# Create new Artifact for complete FML4.0 Dataset in IDS Provider Connector
   headers = {'x-api-key': 'ApiKeyDefaultValue'}
   response = requests.get(f'{path}/api/v1/data/contractnegotiations', headers=headers)
   response_json = response.json()
   counterPartyAddress = ''
   for aggrement in response_json:
       if aggrement["contractAgreementId"] == acceptedContract_id:
           counterPartyAddress = aggrement["counterPartyAddress"]
   body = {
       "assetId": assetID,
       "connectorAddress": counterPartyAddress,
       "connectorId": "consumer",
       "contractId": acceptedContract_id,
       "dataDestination": {
           "properties": {
               "account": "company1assets",
               "type": "AzureStorage"
           }
       },
       "managedResources": True,
       "protocol": "ids-multipart",
       "transferType": {
           "contentType": "application/octet-stream",
           "isFinite": True
       }
}

   response = requests.post(f'{path}/api/v1/data/transferprocess', json=body, verify=False, headers=headers).json()
   aggrement_id = response["id"]
   max_attempts = 10
   wait_time = 2
   for attempt in range(max_attempts):
       state_response = requests.get(f'{path}/api/v1/data/transferprocess/{aggrement_id}/state', headers=headers).json()
       state = state_response["state"]
       if state == "COMPLETED":
           flash(f"Transfer completed.", 'success')
           break
       else:
           time.sleep(wait_time)

   print(state_response)

if __name__ == "__main__":
   transfer_lists = transfer_status()
   for transfer in transfer_lists:
       name = transfer["dataRequest"]["assetId"]
       status = transfer["state"]
       print(name)
       print(status)
