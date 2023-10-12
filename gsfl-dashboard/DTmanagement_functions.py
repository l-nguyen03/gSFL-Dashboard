import json
import requests
import uuid

from azure.core.exceptions import ResourceExistsError
from flask import Flask  # , redirect
from flask import flash
from s3i import IdentityProvider, Directory, BrokerAMQP, UserMessage, TokenType, APP_LOGGER, setup_logger
from datetime import datetime
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

### show all dts' data in the folder to the webpage
def show_all_dts_data():
    folder_path = "/Users/nptlinh/Desktop/gSFL_DashBoard/DTdata"
    file_name = []
    file_path = []
    subfolders = os.listdir(folder_path)
    # print(subfolder)

    for subfolder in subfolders:
        if subfolder == ".DS_Store":
            continue
        subfolder_path = os.path.join(folder_path, subfolder)
        file_list = os.listdir(subfolder_path)
        # print(file_list)
        for filename in file_list:
            filepath = os.path.join(subfolder_path, filename)
            # 检查文件是否是文件而不是目录
            if os.path.isfile(filepath):
                file_name.append(filename)
                file_path.append(filepath)
    combined_list = list(zip(file_name, file_path))
    return combined_list

## get the local saved dt data
def get_chosen_dt_data(DT_names):
    print(DT_names)
    folder_path = "/Users/nptlinh/Desktop/gSFL_DashBoard/DTdata"
    file_names = []
    file_paths = []
    subfolders = DT_names

    for subfolder in subfolders:
        subfolder_path = os.path.join(folder_path, subfolder)
        file_list = os.listdir(subfolder_path)
        for filename in file_list:
            if filename == ".DS_Store":
                continue
            file_path = os.path.join(subfolder_path, filename)
            # 检查文件是否是文件而不是目录
            if os.path.isfile(file_path):
                file_names.append(filename)
                file_paths.append(file_path)
    combined_list = list(zip(file_names, file_paths))
    return combined_list


'''
def get_all_azure_data():
    conn_str = "DefaultEndpointsProtocol=http;AccountName=company1assets;AccountKey=key1;BlobEndpoint=http://192.168.100.9:10000/company1assets;"
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    container_name = "src-container"
    container_client = blob_service_client.get_container_client(container_name)
    blobs = container_client.list_blobs()
    print(blobs)
    #for blob in blobs:
    #    print(blob.name)
    return blobs
'''

def getDTList():
    DTList = [{"name": "Moisture1","id" : "s3i:5ed9a4ea-1b69-44c7-91af-5c4112d756fb"}, {"name" : "Moisture2", "id" : "s3i:4d199d88-a56b-4f42-9921-d22c3467f079"}]
    return DTList

def id_secret():
    s3i_DT = [
        {"name": "Moisture1", "id": "s3i:5ed9a4ea-1b69-44c7-91af-5c4112d756fb", "secret": "l85ZDRTmv63S33z7H7PsFGaqEt1YLvca"},
        {"name": "Moisture2", "id": "s3i:4d199d88-a56b-4f42-9921-d22c3467f079", "secret": "LQigwfydQF85iF5fRie48GCVzRleEEGU"}
    ]
    return s3i_DT


def authenticate(DT_id):
    print("--------------------------")
    print(DT_id)
    print("--------------------------")
    DT_list = id_secret()
    DT_secret = ""
    for DT in DT_list:
        if DT["id"] == DT_id:
            DT_secret = DT["secret"]
            print(f"DT secret {DT_secret}")
            idp = IdentityProvider(
            grant_type="client_credentials",
            identity_provider_url="https://idp.s3i.vswf.dev/",
            realm='KWH',
            client_id=DT_id,
            client_secret=DT_secret,)
            APP_LOGGER.info("Username and password are sent to S3I IdentityProvider.")
            return idp
    print("DT not found")
    return None


def get_token(idp):
    APP_LOGGER.info("Token obtained.")
    return idp.get_token(TokenType.ACCESS_TOKEN)



def check_latest_data(DT_name, DT_id,token):
    print(DT_name)
    print(DT_id)
    url = f"https://ditto.s3i.vswf.dev/api/2/things/{DT_id}"
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)
    output_filename = ""
    #print(response)

    ###check if the data is the latest
    if response.status_code == 200:
        # 获取响应内容
        content = response.json()
        test_time = content['attributes']['features'][1]['latestTime']
        test_time_transfer = test_time[:10]


        # 指定保存文件夹路径
        folder_path = f"/Users/nptlinh/Desktop/gSFL_DashBoard/DTdata/{DT_name}/"
        print(folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 列出文件夹中的所有文件
        all_files = os.listdir(folder_path)

        # 从文件名中提取时间并找到最新的文件
        latest_file_path = None
        latest_time = None

        for filename in all_files:
            if filename.startswith(f"{DT_name}_") and filename.endswith(".json"):
                time_str = filename.split(f"{DT_name}_", 1)[1].split(".json")[0]
                file_time = time_str.replace("_", ":")
                #print(file_time)

                if latest_time is None or file_time > latest_time:
                    print(file_time)
                    print(latest_time)
                    latest_time = file_time
                    latest_file_path = os.path.join(folder_path, filename)

        print(latest_time)
        print(test_time)
        if latest_file_path:
            if latest_time < test_time_transfer:
                output_filename = os.path.join(folder_path, f"{DT_name}_{test_time_transfer}.json")
                with open(output_filename, "w") as outfile:
                    json.dump(content, outfile, indent=4)
                print(f"data is saved to {output_filename}")
                flash(f"Got updated data", 'success')
            else:
                print("No updated data available")
                flash("No updated data available", 'danger')
        else:
            print("No data found")



### upload a data to the azure account
def upload_to_azure(DT_name, DT_path):
    # upload to azure storage
    conn_str = "DefaultEndpointsProtocol=http;AccountName=company1assets;AccountKey=key1;BlobEndpoint=http://localhost:10000/company1assets;"

    # 连接到存储帐户
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    container_name = "src-container"
    file_path = DT_path
    print(f"azure finds the file in {file_path}")
    if file_path == "":
        print("file_path is empty")
    else:
        blob_name = DT_name
        print(blob_name)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        try:
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=False)
            flash(f"Uploaded to Azure successfully", 'success')
        except ResourceExistsError:
            print(f"Blob '{blob_name}' already exists. Upload canceled.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    return

def delete_blob(blob_name):
    connection_string = "DefaultEndpointsProtocol=http;AccountName=company1assets;AccountKey=key1;BlobEndpoint=http://localhost:10000/company1assets;"
    container_name = "src-container"
    blob_name_to_delete = blob_name

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # Get a reference to the blob to be deleted
    blob_client = container_client.get_blob_client(blob_name_to_delete)

    # Delete the specific blob
    blob_client.delete_blob()

    print(f"Blob '{blob_name_to_delete}' has been deleted.")

if __name__ == "__main__":
    DT_name = 'Moisture1'
    DT_id = "s3i:5ed9a4ea-1b69-44c7-91af-5c4112d756fb"
    s3i_identity_provider = authenticate(DT_id)
    access_token = get_token(s3i_identity_provider)
    check_latest_data(DT_name, DT_id, access_token)
