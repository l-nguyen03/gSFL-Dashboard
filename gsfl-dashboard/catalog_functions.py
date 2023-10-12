import json
import requests
from flask import flash
import uuid                
from flask import Flask  # , redirect
from flask import render_template
from flask import request
from json2html import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
#from ml.tools import XML


def process_policy(policy):
    rule_types = ["permissions", "prohibitions", "obligations"]
    for rule_type, rules in policy.items():
        if rule_type in rule_types:
            for rule in rules:
                if rule["constraints"] is not None:
                    for constraint in rule["constraints"]:
                        if constraint["edctype"] == 'AtomicConstraint':
                            if constraint["operator"] == 'IN':
                                tmp = constraint["rightExpression"]["value"].strip("[]").strip(" ").split(",")
                                constraint["rightExpression"]["value"] = tmp
            
    return policy



def convert_json_to_catalogContracts(json_data, provider):
    catalogContracts = []
    contractOffers = json_data["contractOffers"]
    for contract in contractOffers:
        catalogContract = {
            "id": contract["id"],
            "provider": provider,
            "asset": contract["asset"]["id"]
        }
        catalogContracts.append(catalogContract)
    return catalogContracts



def convert_json_to_assetNames(json_data):
    assetID = []
    contractOffers = json_data["contractOffers"]
    for asset in contractOffers:
        asset_name = {
            "asset_name": asset["asset"]["properties"]["asset:prop:name"]
        }
        assetID.append(asset_name)
    return assetID



def getCatalogContracts(path = 'http://localhost:9191'):
    # body = {
    #     "edc:operandLeft": "", "edc:operandRight": "", "edc:operator": "", "edc:Criterion": ""
    # }
    companies = ["company1", "company2", "company3"]
    catalogContracts = []
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    for company in companies:
        response = requests.get(f'{path}/api/v1/data/catalog?providerUrl=http://{company}:8282/api/v1/ids/data', verify=False, headers=headers)
        contract_offers = response.json()
        contract_offers = response.json()["contractOffers"]
        #print(json.dumps(contract_offers, indent=4))
        for offer in contract_offers:
            offer["companyUrl"] = f'http://{company}:8282/api/v1/ids/data'
            catalogContracts.append(offer)
    for contract in catalogContracts:
        start = datetime.strptime(contract["contractStart"], '%Y-%m-%dT%H:%M:%S.%fZ')
        end = datetime.strptime(contract["contractEnd"], '%Y-%m-%dT%H:%M:%S.%fZ')
        delta = end - start
        total_seconds = delta.days * 24 * 60 * 60 + delta.seconds
        rel_delta = relativedelta(end, start)
        contract["validity"] = total_seconds
        contract["asset"]["properties"]["duration"] = f"{rel_delta.years} years, {rel_delta.months} months, {rel_delta.days} days, {rel_delta.hours} hours, {rel_delta.minutes} minutes, {rel_delta.seconds} seconds"
    return catalogContracts



def getAssetNames(path = 'http://localhost:9191'):
    headers = {'x-api-key': 'ApiKeyDefaultValue'}

    response1 = requests.get(f'{path}/api/v1/data/catalog?providerUrl=http://localhost:8282/api/v1/ids/data', headers=headers)
    response_json_formatted = json.dumps(response1.json(), indent=4)
    json_data1 = json.loads(response_json_formatted)
    #print(json_data1)
    assetName1 = convert_json_to_assetNames(json_data1)

    response2 = requests.get(f'{path}/api/v1/data/catalog?providerUrl=http://localhost:8283/api/v1/ids/data', headers=headers)
    json_data2 = response2.json()
    assetName2 = convert_json_to_assetNames(json_data2)

    response3 = requests.get(f'{path}/api/v1/data/catalog?providerUrl=http://localhost:8284/api/v1/ids/data', headers=headers)
    json_data3 = response3.json()
    assetName3 = convert_json_to_assetNames(json_data3)


    assetNames = assetName1 + assetName2 + assetName3
    #print(assetNames)
    return assetNames



### Noch nicht bearbeitet !!! ###
def negotiateCatalogContract(catalogContract_id, asset_id, provider, policy, validity, path='http://localhost:9191'):
    '''
    body = {
        "connectorAddress": provider, #f"http://{provider}:8282/api/v1/ids/data",
        "connectorId": "provider",
        "offer": {
            "assetId": asset_id,
            "offerId": catalogContract_id,
            "policy": {
                "permissions": [
                    {
                        "edctype": "dataspaceconnector:permission",
                        "uid": None,
                        "target": asset_id,
                        "action": {
                            "type": "USE",
                            "includedIn": None,
                            "constraint": None
                        },
                        "assignee": None,
                        "assigner": None,
                        "constraints": [],
                        "duties": []
                    }
                ],
                "prohibitions": [],
                "obligations": [],
                "extensibleProperties": {},
                "inheritsFrom": None,
                "assigner": None,
                "assignee": None,
                "target": None,
                "@type": {
                    "@policytype": "set"
                }
            },
            "validity": 31536000
        },
        "protocol": "ids-multipart"
    }
    '''
    # print("----------------------------------------")
    # print("This is the policy before transformation")
    # print(policy)
    # print("++++++++++++++++++++++++++++++++++++++++")
    # print("This is the policy after transformation")
    policy = process_policy(policy)
    # print(policy)


    body = {
        "connectorAddress": provider,  
        "connectorId": "provider",
        "offer": {
            "assetId": asset_id,
            "offerId": catalogContract_id,
            "policy": policy,
            "validity": validity
        },
        "protocol": "ids-multipart"
    }
    print("***************************************+")
    print("Body of request")
    print(body)
    print("----------------------------------------")
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    response = requests.post(f'{path}/api/v1/data/contractnegotiations', json=body, verify=False, headers=headers)
    print("Response of contract negotiation")
    # Flash a success or failure message

    print(response.json())
    print("---------------------------------------------")
    if response.ok:
        flash(f"Negotiation successfull.", 'success')
    else:
        flash("Negotiation failed", 'danger')



if __name__ == "__main__":
    catalogContracts = getCatalogContracts()
    #assetname= getAssetNames()


