#from urllib import response
import os
import msal
import requests
import xmltodict
import configuration
import tkinter as tk
from tkinter import filedialog

api_url = configuration.api_url
api_Key = configuration.api_Key

 
def acquire_microsoft_token(config):
    try:
        app = msal.ConfidentialClientApplication(
            client_id=config["Client ID"],
            authority=config["Authority"],
            client_credential=config["Client Secret"]
        )
 
        result = app.acquire_token_silent(config["Scope"], account=None)
 
        if not result:
            #print("No suitable token exists in cache. Getting a new one through Client App (AAD)")
            result = app.acquire_token_for_client(scopes=config["Scope"])
 
        if "access_token" in result:
            return result['access_token']
        else:
            print(result.get("error"))
            print(result.get("error_description"))
            print(result.get("correlation_id"))
            return None
 
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
 
token = acquire_microsoft_token(configuration.config)

def download_file(api_url , token , filename, api_Key):
    headers = {
        "Authorization": token,
        "Filename": filename,
        "api-Key": api_Key
    }
 
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            with open(filename, 'wb') as local_file:
                local_file.write(response.content)
            print(f"Downloaded {filename} successfully.")
        else:
            print(f"File download failed with status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def list_files(api_url, token, api_Key):
    headers = {
        "Authorization": token,
        #"Filename": filename,
        "api-Key": api_Key
    }

    data = requests.get(api_url + "/?method=list", headers=headers)

    try:
        obj = xmltodict.parse(data.content) 
        blobs = obj["EnumerationResults"]["Blobs"]["Blob"]

        for blob in blobs:
            filename = blob.get("Name","")
            print(filename) 

    except Exception as e:
        print("No files present") 


def upload_file(api_url, token,  api_Key):
    root = tk.Tk()
    root.withdraw()

    root.attributes('-topmost', 1)

    file_path = filedialog.askopenfilename(parent=root)

    #filename = input("Enter the filename to upload: ")

    if file_path:
        filename = os.path.basename(file_path)
        headers = {
        "Authorization": token,
         "Filename": filename,
        "api-key": api_Key
    }
 
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
            response = requests.put(api_url, headers=headers, data=file_content)

 
            if response.status_code == 201:
                print(f"Uploaded {filename} successfully.")
            else:
                print(f"File upload failed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    else:
        print("File selection cancelled.")


#method = input("Enter the method name (Download File, List Files, Upload File): ").strip().lower()
method = input("Choose an option:\n 1.Download file\n 2.List files\n 3.Upload file\n Enter the number of your choice: ").strip()


if method == "1":
    filename = input("Enter the filename to download: ").strip()
    download_file(api_url, token, filename, api_Key)

elif method == "2":
    list_files(api_url, token, api_Key)    

elif method == "3":
    upload_file(api_url, token, api_Key)
else:
    print("Invalid choice. Please enter 1, 2, or 3 to select an option")
