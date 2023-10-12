import json
#import requests
#from flask import Flask  # , redirect
#from flask import render_template
from flask import request
from flask import Flask, render_template
from assets_functions import getAssets, createAsset, deleteAsset, get_Azure_Data
from policiy_functions import getPolicies, createPolicy, deletePolicy
from catalog_functions import getCatalogContracts, negotiateCatalogContract, getAssetNames
from contractdefinitions_functions import getContractDefinitions, getAssetList, getPolicyList, createContractDefinition, deleteContractDefinition
from DTmanagement_functions import getDTList, get_chosen_dt_data, check_latest_data, get_token, authenticate, delete_blob, show_all_dts_data, upload_to_azure
from acceptedcontracts_functions import getAccepted, transferNewContract, transfer_status
from receivedData_functions import get_received_container_data, delete_received_blob,download_blob


app = Flask(__name__)


def to_pretty_json(value):
    return json.dumps(value, indent=4)

app.jinja_env.filters['to_pretty_json'] = to_pretty_json
app.secret_key = 'your_secret_key_here'
path = 'http://localhost:9191'
currentUser = 'MMI'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form.get('action') == 'changeUser':
            data = request.form.get('ip')
            ip = data.split(",")[0]
            global currentUser
            currentUser = data.split(",")[1]
            global path
            path= f'http://localhost{str(ip)}'
    return render_template('home.html', currentUser=currentUser)



@app.route("/DTmanagement", methods=['GET', 'POST'])
def DTmanagement():
    item_list = []
    if request.method == 'POST':
        if request.form.get('action') == 'check':
            selectedDTs = json.loads(request.form.get('selectedDTs'))
            for selectedDT in selectedDTs:
                s3i_identity_provider = authenticate(selectedDT["id"])
                if s3i_identity_provider is not None:
                    access_token = get_token(s3i_identity_provider)
                    check_latest_data(selectedDT["name"], selectedDT["id"], access_token)
        elif request.form.get('action') == 'show':
            selectedDTs = json.loads(request.form.get('selectedDTs'))
            DT_names = [dt["name"] for dt in selectedDTs]
            item_list = get_chosen_dt_data(DT_names)
            return render_template('DTmanagement.html', DTList = getDTList(), list = item_list, currentUser=currentUser)
        elif request.form.get('action').startswith('azure'):
            DT = request.form.get('action')[5:]
            parts = DT.strip('()').split(', ')
            part1, part2 = parts
            DT_name = part1.strip("''")
            DT_path = part2.strip("''")
            upload_to_azure(DT_name, DT_path)
        elif request.form.get('action').startswith('delete'):
            blob_name = request.form.get('action')[6:]
            delete_blob(blob_name)
    return render_template('DTmanagement.html',  DTList = getDTList(), list = show_all_dts_data(), currentUser=currentUser) #data = show_all_dts_data(),


	
@app.route("/assets", methods=['GET', 'POST'])
def assets():
    if request.method == 'POST':
        if request.form.get('action') == 'create':
            createAsset(path)
        elif request.form.get('action').startswith('delete'):
            asset_id = request.form.get('action')[6:]
            deleteAsset(asset_id, path)
    return render_template('assets.html', assets=getAssets(path), currentUser=currentUser, dataList=get_Azure_Data())



@app.route("/policies", methods=['GET', 'POST'])
def policies():
    if request.method == 'POST':
        if request.form.get('action') == 'create':
            createPolicy(path)    
        elif request.form.get('action').startswith('delete'):
            policy_id = request.form.get('action')[6:]
            deletePolicy(policy_id, path)
    return render_template('policies.html', policies=getPolicies(path), currentUser=currentUser)



@app.route("/contractdefinitions", methods=['GET', 'POST'])
def contractdefinitions():
    if request.method == 'POST':
        if request.form.get('action') == 'create':
            contractName = request.form.get('contractID')
            selectedAssets = request.form.get('selectedAssets')
            selectedAccessPolicy = request.form.get('selectedAccessPolicy')
            selectedContractPolicy = request.form.get('selectedContractPolicy')
            contract_duration = request.form.get('duration')
            createContractDefinition(contractName, selectedAssets, selectedAccessPolicy, selectedContractPolicy, contract_duration, path)
        elif request.form.get('action').startswith('delete'):
            contractDefinition_id = request.form.get('action')[6:]
            deleteContractDefinition(contractDefinition_id, path)
    return render_template('contractdefinitions.html', contractDefinitions = getContractDefinitions(path), assetList = getAssetList(path), policyList = getPolicyList(path), currentUser=currentUser)



@app.route("/catalog", methods=['GET', 'POST'])
def catalog():
    if request.method == 'POST':
        catalogContract_id = request.form.get('catalogContractId')
        asset_id = request.form.get('assetId')
        provider = request.form.get('provider')
        validity = request.form.get('validity')
        policy_original = request.form.get('policy')
        policy_transfer = policy_original.replace("'", '"').replace("None", "null")
        policy = json.loads(policy_transfer)
        negotiateCatalogContract(catalogContract_id, asset_id, provider, policy, validity, path)
    return render_template('catalog.html', catalogContracts=getCatalogContracts(path), currentUser=currentUser)


@app.route("/acceptedcontracts", methods=['GET', 'POST'])
def acceptedcontracts():
    if request.method == 'POST':
        acceptedContract_id = request.form.get('agreementID')
        print(acceptedContract_id)
        assetID = request.form.get('assetID')
        print(assetID)
        transferNewContract(acceptedContract_id, assetID, path)
    return render_template('acceptedcontracts.html', ac_contracts = getAccepted(path), transfer_lists=transfer_status(), currentUser=currentUser)

@app.route("/receivedData", methods=['GET', 'POST'])
def receivedData():
    list = get_received_container_data()
    if request.method == 'POST':
        if request.form.get('action').startswith('download'):
            item = request.form.get('action')[8:]
            download_blob(item)
        elif request.form.get('action').startswith('delete'):
            item = request.form.get('action')[6:]
            print(item)
            delete_received_blob(item)
    return render_template('receivedData.html', list = list, currentUser=currentUser)


if __name__ == '__main__':
    app.run()