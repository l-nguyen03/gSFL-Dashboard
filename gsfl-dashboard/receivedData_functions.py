import json
import requests       
import uuid

from azure.core.exceptions import ResourceExistsError
from flask import Flask  # , redirect
from flask import flash
from datetime import datetime
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def get_received_container_data():
    conn_str = "DefaultEndpointsProtocol=http;AccountName=company1assets;AccountKey=key1;BlobEndpoint=http://localhost:10000/company1assets;"
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    containers = blob_service_client.list_containers()

    container_names = []
    blob_names = []

    for container in containers:
        container_client = blob_service_client.get_container_client(container.name)
        blobs = container_client.list_blobs()
        #print(blobs)

        has_complete_blob = any(blob.name == ".complete" for blob in blobs)
        #print(has_complete_blob)
        has_other_blob = any(blob.name != ".complete" for blob in blobs)
        #print(has_other_blob)
        final_condition = has_complete_blob and has_other_blob
        print(final_condition)


        if final_condition:
            container_names.append(container.name)
            print("1")
            print(container.name)
            data = container_client.list_blobs()
            for item in data:
                print(item.name)
                if item.name != ".complete":
                  blob_names.append(item.name)

    #print("Container Names:", container_names)
    #print("Blob Names:", blob_names)

    combined_list = list(zip(container_names, blob_names))

    # 打印组合后的列表
    print(combined_list)

    return combined_list

def download_blob(item):
    connection_string = "DefaultEndpointsProtocol=http;AccountName=company1assets;AccountKey=key1;BlobEndpoint=http://localhost:10000/company1assets;"
    trimmed_str = item[2:-2]
    # 分割字符串为两部分
    container_name, blob_name = trimmed_str.split("', '")
    print(container_name)
    print(blob_name)

    downloaded_file_path = f"/Users/nptlinh/Desktop/gSFL_DashBoard/ReceivedData/{blob_name}"


    # 创建 BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # 创建 Blob 客户端
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # 下载 Blob
    with open(downloaded_file_path, "wb") as my_blob:
        download_stream = blob_client.download_blob()
        my_blob.write(download_stream.read())

    flash(f"Blob '{blob_name}' downloaded to {downloaded_file_path}", 'success')

    return

def delete_received_blob(item):
    connection_string = "DefaultEndpointsProtocol=http;AccountName=company1assets;AccountKey=key1;BlobEndpoint=http://localhost:10000/company1assets;"
    # 去掉首尾的括号和引号
    trimmed_str = item[2:-2]
    # 分割字符串为两部分
    container_name, blob_name_to_delete = trimmed_str.split("', '")
    print(container_name)
    print(blob_name_to_delete)

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # Get a reference to the blob to be deleted
    blob_client = container_client.get_blob_client(blob_name_to_delete)

    # Delete the specific blob
    blob_client.delete_blob()

    flash(f"Blob '{blob_name_to_delete}' has been deleted.", 'success')

if __name__ == "__main__":
    blobs = get_received_container_data()
    print(blobs)
