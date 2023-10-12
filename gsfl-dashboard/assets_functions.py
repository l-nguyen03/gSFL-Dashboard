import json
import requests       
import uuid                
from flask import Flask  # , redirect
from flask import flash
from flask import request
from azure.storage.blob import BlobServiceClient
from json2html import *
#from ml.tools import XML

#get src-container data from Azure account
def get_Azure_Data():
    conn_str = "DefaultEndpointsProtocol=http;AccountName=company1assets;AccountKey=key1;BlobEndpoint=http://localhost:10000/company1assets;"
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    container_name = "src-container"
    container_client = blob_service_client.get_container_client(container_name)
    blobs = container_client.list_blobs()
    return blobs



def list_all_containers():
    # Fetch the connection string securely, ideally from environment variables or Azure Key Vault.
    conn_str = "DefaultEndpointsProtocol=http;AccountName=company1assets;AccountKey=key1;BlobEndpoint=http://localhost:10000/company1assets;"

    try:
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        
        # This will return a generator with all container names.
        containers = blob_service_client.list_containers()
        container = [container for container in containers]
        return container
        ## Convert generator to a list of container names
        #container_names = [container['name'] for container in containers]
        #return container_names
    except Exception as e:
        print(f"An error occurred: {e}")
        return []



def convert_json_to_assets(json_data):
    assets = []
    for item in json_data:
        asset = {
            "id": item["id"],
            "prop_name": item["properties"]["asset:prop:name"],
            "prop_id": item["properties"]["asset:prop:id"]
        }
        assets.append(asset)
    return assets



def getAssets(path='http://localhost:9191'):
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    response = requests.get(f'{path}/api/v1/data/assets', headers=headers)
    response_json_formatted = json.dumps(response.json(), indent=4)

    assets = json.loads(response_json_formatted)
    
    return assets
        



def createAsset(path='http://localhost:9191'):
    name = request.form.get('assetNameInput')
    content_type = request.form.get('assetContentInput')
    blob_name = request.form.get('selectedAssets')
    prop_name = blob_name.split(".")[0]
    #blob_name = request.form.get('blobNameInput')
    response = createNewAsset(name, prop_name, blob_name, content_type, path)
    if response:
        flash(f"Asset {prop_name} successfully created", 'success')
    else: 
        flash(f"Asset {prop_name} couldn't be created", 'danger')
           
    

def createNewAsset(name, prop_name, blob_name, content_type, path='http://localhost:9191'):  # EDC
# Create new Artifact for complete FML4.0 Dataset in IDS Provider Connector
    body = {
    "asset": {
    "id": prop_name,
    "properties": {
      "asset:prop:name": name,
      "asset:prop:contenttype": content_type,
      "asset:prop:version": "2.0",
      "asset:prop:id": prop_name,
      "type": "AzureStorage"
    }
  },
    "dataAddress": {
    "properties": {
      "type": "AzureStorage",
      "account": "company1assets",
      "container": "src-container",
      "blobname": blob_name,
      "keyName": "company1assets-key1"
    }
  }
}
    
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    
    response = requests.post(f'{path}/api/v1/data/assets', json=body, verify=False, headers=headers)

    return response



def deleteAsset(asset_id, path='http://localhost:9191'):
    headers = {'x-api-key': 'ApiKeyDefaultValue'}
    
    response = requests.delete(f'{path}/api/v1/data/assets/{asset_id}', verify=False, headers=headers)

    if response.ok:
        flash(f"Asset was deleted successfully.", 'success') 
    else:
        flash("Failed to delete Asset.", 'danger')

if __name__ == "__main__":
    print(getAssets())