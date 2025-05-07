import json
import re
import requests
import os
from typing import List, Dict, Any, Union
import difflib
from langchain_core.tools import tool
from langchain.tools import Tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.tools import BaseTool
from langchain.tools import BaseTool
from typing import  List
from pydantic import  Field
from software_and_issue_dict import software_devices
from datetime import datetime, timedelta
from dateutil import parser as date_parser
# from dotenv import load_dotenv
from llm import load_llm
import time
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import sql
import html2text
import json
import requests
h = html2text.HTML2Text()
h.ignore_links = True
# load_dotenv()
id_var=''
x=False
# id_var=''
# user_name=os.getenv("USERNAME")
# password=os.getenv("PASSWORD")
# USERNAME = user_name
# PASSWORD = password
# print(USERNAME)
# print(PASSWORD)
USERNAME = "teams.bot"
PASSWORD = "Teams.bot#$123"

global_tool_data = {}
 
# @tool
# def retrieve_tool(key_name: str) -> str:
#     """
#     Retrieve stored data based on the given key.
    
#     This tool retrieves data from the global tool data based on the key provided.
#     If the key refers to a service name, it retrieves the service details from `json_search_tool`.
#     """
    
#     global global_tool_data
#     print("Available keys in global_tool_data:", list(global_tool_data.keys()))
#     print("Looking for key:", key_name)

#     if key_name :
#         print("in if condition and key name :",key_name)
#         return global_tool_data.get(key_name, f"No data found for the key: {key_name}")
#     # If the key name is not "json_search_tool" or "identify_profile_tool", search for the service
#     # if key_name != "json_search_tool" and key_name != "identify_profile_tool":
#     #     # Try to get the latest search results from json_search_tool
#     #     data = global_tool_data.get("json_search_tool", [])
        
#     #     # Look for the service in the results
#     #     for service in data:
#     #         if service.get("subservice name") == key_name:
#     #             return service
        
#     #     return f"No service found with name: {key_name}"
    
#     # # If the key name is found, return the corresponding data from global_tool_data
#     # return global_tool_data.get(key_name, f"No data found for the key: {key_name}")



@tool
def retrieve_tool(key_name: str) -> str:
    """
    Retrieve stored data based on the given key.
    
    This tool retrieves data from the global tool data based on the key provided.
    If the key refers to a service name or subservice name, it retrieves the service details from `json_search_tool`.
    """
    
    global global_tool_data
    print("Available keys in global_tool_data:", list(global_tool_data.keys()))
    print("Looking for key:", key_name)

    if key_name in global_tool_data:
        print("Key name:", key_name)
        return global_tool_data.get(key_name, f"No data found for the key: {key_name}")

    elif key_name and "json_search_tool" in global_tool_data:
        data = global_tool_data.get("json_search_tool", [])
        # Look for the service in the results
        for service in data:
            if service.get("subservice name") == key_name:
                return service
        
        return f"No service found with name: {key_name}"
    
    elif "identify_profile_tool" in global_tool_data:
        return global_tool_data.get("identify_profile_tool", [])



    elif "selected_device_name" in global_tool_data :
        print("in if condition and key name :",key_name)
        return global_tool_data.get(key_name, f"No data found for the key: {key_name}")
    
    return "Invalid key or no matching data found."

# ---------------------------------------------------------------------------------------------------------------------------------------------------------

@tool
def all_service_family_tool() -> dict:
    """This tool retrieves all ServiceFamily names and their corresponding keys from the external service."""
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
   
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "ServiceFamily",
        "key": "SELECT ServiceFamily",
        "output_fields": "name"
    }
    print("===============json ============", json_data.get("key"))
    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()
        
        # Assuming the response is a JSON with the incident details
        result_dict = {}
        for v in data["objects"].values():
            result_dict[v["fields"]["name"]] = v["key"]
        
        return result_dict
    else:
        return "Sorry, there was an issue fetching the Service_Family details."




# ************************************************ CREATE TOOL*******************************************************
 
@tool
def create_incident_with_service_and_subservice(org_id: int, contactid: int, incident_title: str, 
                                                incident_description: str, service_id: int, 
                                                servicesubcategory_id: int) -> str:
    """This tool creates an incident/event in the system if the user provides the necessary details."""

    # API URL
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload for creating the incident
    json_data = {
        "operation": "core/create",
        "comment": " Created by Teamsbot",
        "class": "Incident",
        "output_fields": "ref,title, origin",
        "fields": {
            "org_id": org_id,
            "caller_id": contactid,
            "origin": "teamsbot",
            "title": incident_title,
            "description": incident_description,
            "service_id": service_id,
            "servicesubcategory_id": servicesubcategory_id
        }
    }

    json_string = json.dumps(json_data)

    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)

    # Make the POST request
    response = requests.post(url, data={
        "version": "1.0",
        "json_data": json_string
    }, auth=auth)

    # Handle the response
    if response.status_code == 200:
        data = response.json()
        incident_data = data.get("objects", [])
        
        if incident_data:
            for incident_key, incident in incident_data.items():
                friendly_name = incident.get('fields', {}).get('ref', 'Unknown')
            return f"Incident Created: {friendly_name}"
        else:
            return "Failed to create the incident. Please try again."
    else:
        return "Sorry, there was an issue creating the incident."





@tool
def create_incident_without_sub(org_id: int, contactid: int, incident_title: str, 
                                incident_description: str, service_id: int) -> str:
    """This tool creates an incident when the service name is available, but the subservice is N/A."""
    
    # API URL
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload for creating the incident
    json_data = {
        "operation": "core/create",
        "comment": " Created by Teamsbot",
        "class": "Incident",
        "output_fields": "ref,title, origin",
        "fields": {
            "org_id": org_id,
            "caller_id": contactid,
            "origin": "teamsbot",
            "title": incident_title,
            "description": incident_description,
            "service_id": service_id
        }
    }

    json_string = json.dumps(json_data)

    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)

    # Make the POST request
    response = requests.post(url, data={
        "version": "1.0",
        "json_data": json_string
    }, auth=auth)

    # Handle the response
    if response.status_code == 200:
        data = response.json()
        incident_data = data.get("objects", [])
        
        if incident_data:
            for incident_key, incident in incident_data.items():
                friendly_name = incident.get('fields', {}).get('ref', 'Unknown')
            return f"Incident Created: {friendly_name}"
        else:
            return "Failed to create the incident. Please try again."
    else:
        return "Sorry, there was an issue creating the incident."






@tool
def create_incident_without_service_and_sub(org_id: int, contactid: int, 
                                            incident_title: str, incident_description: str) -> str:
    """This tool creates an incident when there is no service and subservice."""

    # API URL
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload for creating the incident
    json_data = {
        "operation": "core/create",
        "comment": " Created by Teamsbot",
        "class": "Incident",
        "output_fields": "ref,title, origin",
        "fields": {
            "org_id": org_id,
            "caller_id": contactid,
            "origin": "teamsbot",
            "title": incident_title,
            "description": incident_description
        }
    }

    json_string = json.dumps(json_data)

    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)

    # Make the POST request
    response = requests.post(url, data={
        "version": "1.0",
        "json_data": json_string
    }, auth=auth)

    # Handle the response
    if response.status_code == 200:
        data = response.json()
        incident_data = data.get("objects", [])
        
        if incident_data:
            for incident_key, incident in incident_data.items():
                friendly_name = incident.get('fields', {}).get('ref', 'Unknown')
            return f"Incident Created: {friendly_name}"
        else:
            return "Failed to create the incident. Please try again."
    else:
        return "Sorry, there was an issue creating the incident."

 
 
# ************************************************ GET TOOL*******************************************************
  
@tool
def get_incident_details_with_public_log(ticket_id: str) -> str:
    """Retrieves and returns structured incident details for a given ticket ID."""
    global id_var

    if not ticket_id:
        return "Please provide a valid Ticket ID."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE ref='{ticket_id}'",
        "output_fields": "*"
    }

    response = requests.get(
        url,
        params={"version": "1.0", "json_data": json.dumps(json_data)},
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code != 200:
        return "Sorry, there was an issue fetching the incident details."

    data = response.json()
    incident_data = data.get("objects", {})

    if not incident_data:
        return "No details found for this incident."

    for _, incident in incident_data.items():
        fields = incident.get("fields", {})

        # Basic field extraction
        status = fields.get("status", "N/A")
        title = fields.get("title", "N/A")
        description = fields.get("description", "N/A").replace("<p>", "").replace("</p>", "")
        origin = fields.get("origin", "N/A")
        service_name = fields.get("service_name", "N/A")
        subcategory = fields.get("servicesubcategory_name", "N/A")
        team_name = fields.get("team_id_friendlyname", "N/A")
        start_date = fields.get("start_date", "N/A")
        public_log = fields.get("public_log", {}).get("entries", [])
        public_entries = [
            f"Date - {entry.get('date', 'N/A')}  Message - {entry.get('message', 'N/A')}"
            for entry in public_log
        ]
        formatted_public_logs = "\n".join(public_entries)

        # Override origin if it's lowercase
        if origin.lower() == "teamsbot":
            origin = "TEAMS BOT"

        # Dynamic device name from global
        functionalci_name = id_var or "Unknown"
        device_name = "No CI needed" if functionalci_name == "Unknown" else functionalci_name

        # Final structured message (no regex)
        structured_message = (
            f"🚩 **Incident:** {ticket_id}\n"
            f"🟢 **Status:** {status}\n"
            f"📝 **Title:** {title}\n"
            f"📄 **Description:** {description}\n"
            f"🌐 **Origin:** {origin}\n"
            f"🛠️ **Service Name:** {service_name}\n"
            f"🔧 **Service Sub Category:** {subcategory}\n"
            f"👥 **Assigned Team:** {team_name}\n"
            f"📅 **Start Date:** {start_date}\n"
            f"💻 **Device Name:** {device_name}\n"
            f"📝 **Public log:** {formatted_public_logs}"
        )

        id_var = ""  # Reset after use
        return structured_message
 

@tool 
def get_incident_details_with_public_and_private_log(ticket_id: str) -> str:
    """Retrieves and returns structured incident details for a given ticket ID."""
    global id_var

    if not ticket_id:
        return "Please provide a valid Ticket ID."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE ref='{ticket_id}'",
        "output_fields": "*"
    }

    response = requests.get(
        url,
        params={"version": "1.0", "json_data": json.dumps(json_data)},
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code != 200:
        return "Sorry, there was an issue fetching the incident details."

    data = response.json()
    incident_data = data.get("objects", {})

    if not incident_data:
        return "No details found for this incident."

    for _, incident in incident_data.items():
        fields = incident.get("fields", {})

        # Basic field extraction
        status = fields.get("status", "N/A")
        title = fields.get("title", "N/A")
        description = fields.get("description", "N/A").replace("<p>", "").replace("</p>", "")
        origin = fields.get("origin", "N/A")
        service_name = fields.get("service_name", "N/A")
        subcategory = fields.get("servicesubcategory_name", "N/A")
        team_name = fields.get("team_id_friendlyname", "N/A")
        start_date = fields.get("start_date", "N/A")
        public_log = fields.get("public_log", {}).get("entries", [])
        public_entries = [
            f"Date - {entry.get('date', 'N/A')}  Message - {entry.get('message', 'N/A')}"
            for entry in public_log
        ]
        formatted_public_logs = "\n".join(public_entries)
        
        private_log = fields.get("private_log", {}).get("entries", [])
        private_entries = [
            f"Date - {entry.get('date', 'N/A')}  Message - {entry.get('message', 'N/A')}"
            for entry in private_log
        ]
        formatted_private_logs = "\n".join(private_entries)

        # Override origin if it's lowercase
        if origin.lower() == "teamsbot":
            origin = "TEAMS BOT"

        # Dynamic device name from global
        functionalci_name = id_var or "Unknown"
        device_name = "No CI needed" if functionalci_name == "Unknown" else functionalci_name

        # Final structured message (no regex)
        structured_message = (
            f"🚩 **Incident:** {ticket_id}\n"
            f"🟢 **Status:** {status}\n"
            f"📝 **Title:** {title}\n"
            f"📄 **Description:** {description}\n"
            f"🌐 **Origin:** {origin}\n"
            f"🛠️ **Service Name:** {service_name}\n"
            f"🔧 **Service Sub Category:** {subcategory}\n"
            f"👥 **Assigned Team:** {team_name}\n"
            f"📅 **Start Date:** {start_date}\n"
            f"💻 **Device Name:** {device_name}\n"
            f"📝 **Public log:** {formatted_public_logs}\n"
            f"📝 **Private log:** {formatted_private_logs}"
        )

        id_var = ""  # Reset after use
        return structured_message


@tool
def get_service_details_with_public_log(ticket_id: str) -> str:
    """Retrieves and returns structured service request details for a given ticket ID."""
    global id_var

    if not ticket_id:
        return "Please provide a valid Ticket ID."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE ref='{ticket_id}'",
        "output_fields": "*"
    }

    response = requests.get(
        url,
        params={"version": "1.0", "json_data": json.dumps(json_data)},
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code != 200:
        return "Sorry, there was an issue fetching the service request details."

    data = response.json()
    service_data = data.get("objects", {})

    if not service_data:
        return "No details found for this service request."

    for _, item in service_data.items():
        fields = item.get("fields", {})

        # Extract fields safely
        status = fields.get("status", "N/A")
        title = fields.get("title", "N/A")
        description = fields.get("description", "N/A").replace("<p>", "").replace("</p>", "")
        origin = fields.get("origin", "N/A")
        service_name = fields.get("service_name", "N/A")
        subcategory = fields.get("servicesubcategory_name", "N/A")
        team_name = fields.get("team_id_friendlyname", "N/A")
        start_date = fields.get("start_date", "N/A")
        public_log = fields.get("public_log", {}).get("entries", [])
        public_entries = [
            f"Date - {entry.get('date', 'N/A')}  Message - {entry.get('message', 'N/A')}"
            for entry in public_log
        ]
        formatted_public_logs = "\n".join(public_entries)

        # Normalize origin
        if origin.lower() == "teamsbot":
            origin = "TEAMS BOT"

        # Dynamic CI name from global
        functionalci_name = id_var or "Unknown"
        device_name = "No CI needed" if functionalci_name == "Unknown" else functionalci_name

        # Final structured message
        structured_message = (
            f"📦 **Service Request:** {ticket_id}\n"
            f"🟢 **Status:** {status}\n"
            f"📝 **Title:** {title}\n"
            f"📄 **Description:** {description}\n"
            f"🌐 **Origin:** {origin}\n"
            f"🛠️ **Service Name:** {service_name}\n"
            f"🔧 **Service Sub Category:** {subcategory}\n"
            f"👥 **Assigned Team:** {team_name}\n"
            f"📅 **Start Date:** {start_date}\n"
            f"💻 **Device Name:** {device_name}\n"
            f"📝 **Public log:** {formatted_public_logs}"
        )

        id_var = ""  # Reset global after use
        return structured_message

 
@tool 
def get_service_details_with_public_and_private_log(ticket_id: str) -> str:
    """Retrieves and returns structured incident details for a given ticket ID."""
    global id_var

    if not ticket_id:
        return "Please provide a valid Ticket ID."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE ref='{ticket_id}'",
        "output_fields": "*"
    }

    response = requests.get(
        url,
        params={"version": "1.0", "json_data": json.dumps(json_data)},
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code != 200:
        return "Sorry, there was an issue fetching the incident details."

    data = response.json()
    incident_data = data.get("objects", {})

    if not incident_data:
        return "No details found for this incident."

    for _, incident in incident_data.items():
        fields = incident.get("fields", {})

        # Basic field extraction
        status = fields.get("status", "N/A")
        title = fields.get("title", "N/A")
        description = fields.get("description", "N/A").replace("<p>", "").replace("</p>", "")
        origin = fields.get("origin", "N/A")
        service_name = fields.get("service_name", "N/A")
        subcategory = fields.get("servicesubcategory_name", "N/A")
        team_name = fields.get("team_id_friendlyname", "N/A")
        start_date = fields.get("start_date", "N/A")
        public_log = fields.get("public_log", {}).get("entries", [])
        public_entries = [
            f"Date - {entry.get('date', 'N/A')}  Message - {entry.get('message', 'N/A')}"
            for entry in public_log
        ]
        formatted_public_logs = "\n".join(public_entries)
        
        private_log = fields.get("private_log", {}).get("entries", [])
        private_entries = [
            f"Date - {entry.get('date', 'N/A')}  Message - {entry.get('message', 'N/A')}"
            for entry in private_log
        ]
        formatted_private_logs = "\n".join(private_entries)

        # Override origin if it's lowercase
        if origin.lower() == "teamsbot":
            origin = "TEAMS BOT"

        # Dynamic device name from global
        functionalci_name = id_var or "Unknown"
        device_name = "No CI needed" if functionalci_name == "Unknown" else functionalci_name

        # Final structured message (no regex)
        structured_message = (
            f"🚩 **Incident:** {ticket_id}\n"
            f"🟢 **Status:** {status}\n"
            f"📝 **Title:** {title}\n"
            f"📄 **Description:** {description}\n"
            f"🌐 **Origin:** {origin}\n"
            f"🛠️ **Service Name:** {service_name}\n"
            f"🔧 **Service Sub Category:** {subcategory}\n"
            f"👥 **Assigned Team:** {team_name}\n"
            f"📅 **Start Date:** {start_date}\n"
            f"💻 **Device Name:** {device_name}\n"
            f"📝 **Public log:** {formatted_public_logs}\n"
            f"📝 **Private log:** {formatted_private_logs}"
        )

        id_var = ""  # Reset after use
        return structured_message



# ************************************************ UPDATE TOOL*******************************************************
 
@tool
def update_incident_public_log(ticket_id: str, log: str) -> str:
    """This tool helps to update the generated ticket according to the given ticket ID."""
    
    # Step 1: Ask for incident ID if not provided
    if not ticket_id:
        return "Please provide a valid incident ID."

    # Step 2: Prepare the URL and data for the GET request
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload for the update operation
    json_data = {
        "operation": "core/update",
        "comment": "Public log updated by Teamsbot.",
        "class": "Incident",
        "key": f"SELECT Incident WHERE ref='{ticket_id}'",
        "output_fields": "ref,public_log",
        "fields": {
            "public_log": {
                "items": [{"message": "Test API"}]
            }
        }
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request to fetch incident details
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response for GET request
    if response.status_code == 200:
        data = response.json()
        
        incident_data = data.get("objects", [])
        
        if incident_data:
            for incident_key, incident in incident_data.items():
                incident_id = incident_key.split('::')[1] if '::' in incident_key else 'Unknown'
            
            # Prepare the data for the POST request to update the log
            json_data = {
                "operation": "core/update",
                "comment": "Synchronization from Teamsbot.",
                "class": "Incident",
                "key": incident_id,
                "output_fields": "*",
                "fields": {
                    "public_log": log
                }
            }

            json_string = json.dumps(json_data)
            
            # Make the POST request to update the log
            response = requests.post(url, data={
                "version": "1.0",
                "json_data": json_string
            }, auth=auth)
            
            # Handle the response for POST request
            if response.status_code == 200:
                data = response.json()
                return "Public log has been successfully updated."
            else:
                return "Sorry, there was an issue creating the incident log."
    
    return "Failed to retrieve the incident details."

@tool
def update_UserRequest_public_log(ticket_id: str, log: str) -> str:
    """This tool helps to update the generated ticket according to the given ticket ID."""
    
    # Step 1: Ask for incident ID if not provided
    if not ticket_id:
        return "Please provide a valid incident ID."

    # Step 2: Prepare the URL and data for the GET request
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload for the update operation
    json_data = {
        "operation": "core/update",
        "comment": "Public log updated by Teamsbot.",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE ref='{ticket_id}'",
        "output_fields": "ref,public_log",
        "fields": {
            "public_log": {
                "items": [{"message": "Test API"}]
            }
        }
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request to fetch incident details
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response for GET request
    if response.status_code == 200:
        data = response.json()
        
        incident_data = data.get("objects", [])
        
        if incident_data:
            for incident_key, incident in incident_data.items():
                incident_id = incident_key.split('::')[1] if '::' in incident_key else 'Unknown'
            
            # Prepare the data for the POST request to update the log
            json_data = {
                "operation": "core/update",
                "comment": "Synchronization from Teamsbot.",
                "class": "UserRequest",
                "key": incident_id,
                "output_fields": "*",
                "fields": {
                    "public_log": log
                }
            }

            json_string = json.dumps(json_data)
            
            # Make the POST request to update the log
            response = requests.post(url, data={
                "version": "1.0",
                "json_data": json_string
            }, auth=auth)
            
            # Handle the response for POST request
            if response.status_code == 200:
                data = response.json()
                return "Public log has been successfully updated."
            else:
                return "Sorry, there was an issue creating the incident log."
    
    return "Failed to retrieve the incident details."


#Updated by Abhishek arya on 18th April 2025
@tool
def update_incident_private_log(ticket_id: str, log: str) -> str:
    """This tool helps to update the generated ticket according to the given ticket ID."""
    
    # Check if ticket_info is a dictionary and contains expected data
    ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)
    # Check if ticket_info is a dictionary and contains expected data
    if not isinstance(ticket_info, dict):
        return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
    
    # Directly extract the ticket details since your structure doesn't have 'objects'
    team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
    agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
    key = ticket_info.get("key")  # Assuming key is at the top level as well
    
    # Ensure team_id and agent_id are found in ticket_info
    if not team_id or not agent_id:
        return {"status": "error", "message": "team_id or agent_id not found in incident details"}

    # Step 2: Prepare the URL and data for the GET request
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload for the update operation
    json_data = {
            "operation": "core/update",
            "comment": "Public log updated by Teamsbot. ",
            "class": "Incident",
            "key": key,
            "output_fields": "ref,private_log",
            "fields": {
            "private_log":
            {
            "items": [
            {
            "message": "Test APIs"}]
        }
    }
}
    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request to fetch incident details
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response for GET request
    if response.status_code == 200:
        data = response.json()
        
        incident_data = data.get("objects", [])
        
        if incident_data:
            for incident_key, incident in incident_data.items():
                incident_id = incident_key.split('::')[1] if '::' in incident_key else 'Unknown'
            
            # Prepare the data for the POST request to update the log
            json_data = {
                "operation": "core/update",
                "comment": "Synchronization from Teamsbot.",
                "class": "Incident",
                "key": incident_id,
                "output_fields": "*",
                "fields": {
                    "private_log": log
                }
            }

            json_string = json.dumps(json_data)
            
            # Make the POST request to update the log
            response = requests.post(url, data={
                "version": "1.0",
                "json_data": json_string
            }, auth=auth)
            
            # Handle the response for POST request
            if response.status_code == 200:
                data = response.json()
                return "Private log has been successfully updated."
            else:
                return "Sorry, there was an issue creating the incident log."
    
    return "Failed to retrieve the incident details."



#Updated by Abhishek arya on 18th April 2025
@tool
def update_UserRequest_private_log(ticket_id: str, log: str) -> str:
    """This tool helps to update the generated ticket according to the given ticket ID."""
    
    # Check if ticket_info is a dictionary and contains expected data
    ticket_info = get_complete_UserRequest_details.invoke({"ticket_id": ticket_id})
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)
    # Check if ticket_info is a dictionary and contains expected data
    if not isinstance(ticket_info, dict):
        return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
    
    # Directly extract the ticket details since your structure doesn't have 'objects'
    team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
    agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
    key = ticket_info.get("key")  # Assuming key is at the top level as well
    
    # Ensure team_id and agent_id are found in ticket_info
    if not team_id or not agent_id:
        return {"status": "error", "message": "team_id or agent_id not found in incident details"}

    # Step 2: Prepare the URL and data for the GET request
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload for the update operation
    json_data = {
            "operation": "core/update",
            "comment": "Public log updated by Teamsbot. ",
            "class": "UserRequest",
            "key": key,
            "output_fields": "ref,private_log",
            "fields": {
            "private_log":
            {
            "items": [
            {
            "message": "Test APIs"}]
        }
    }
}
    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request to fetch incident details
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response for GET request
    if response.status_code == 200:
        data = response.json()
        
        incident_data = data.get("objects", [])
        
        if incident_data:
            for incident_key, incident in incident_data.items():
                incident_id = incident_key.split('::')[1] if '::' in incident_key else 'Unknown'
            
            # Prepare the data for the POST request to update the log
            json_data = {
                "operation": "core/update",
                "comment": "Synchronization from Teamsbot.",
                "class": "UserRequest",
                "key": incident_id,
                "output_fields": "*",
                "fields": {
                    "private_log": log
                }
            }

            json_string = json.dumps(json_data)
            
            # Make the POST request to update the log
            response = requests.post(url, data={
                "version": "1.0",
                "json_data": json_string
            }, auth=auth)
            
            # Handle the response for POST request
            if response.status_code == 200:
                data = response.json()
                return "Private log has been successfully updated."
            else:
                return "Sorry, there was an issue creating the incident log."
    
    return "Failed to retrieve the incident details."



# ************************************************ RAG TOOL******************************************************* 


DB_FAISS_PATH = 'faissdb/'
 
def user_input(user_question: str) -> list:
    
    # Initialize embeddings
    # embeddings = HuggingFaceEmbeddings(model="models/embedding-001")
    embeddings = HuggingFaceEmbeddings(
        # model_name="sentence-transformers/paraphrase-MiniLM-L6-v2",
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    # embeddings=OpenAIEmbeddings(
    #     model="text-embedding-3-large"
    # )
    
    # Load the FAISS vector store
    new_db = FAISS.load_local(DB_FAISS_PATH,
                            embeddings,
                            allow_dangerous_deserialization=True)
    
    # Perform similarity search
    docs = new_db.similarity_search(user_question,k=10)
    
    # Extract sentences from the documents
    sentences = [doc.page_content for doc in docs]
    global x
    x=True
    print("turned true")
    return sentences
    
    
 
 
 
@tool
def Rag_tool(user_query: str) -> str:
    """
    RAG (Retrieval-Augmented Generation) tool to generate query answer from available data in similar_data.
    Returns a structured response with emojis and bullets.
    """
    similar_data = user_input(user_query)

    if not similar_data:
        return "⚠️ No relevant information found."

    # If similar_data is a list, format each item as a bullet point
    if isinstance(similar_data, list):
        formatted_lines = [f"🔹 {item.strip()}" for item in similar_data if item.strip()]
        return "\n".join(formatted_lines)

    # If it's a string, fall back to splitting by bullet if needed
    if isinstance(similar_data, str):
        lines = similar_data.split("• ")
        formatted_lines = [f"🔹 {line.strip()}" for line in lines if line.strip()]
        return "\n".join(formatted_lines)

    return "⚠️ Unexpected data format received."


 
#=================================================web search tool=================================================================================
 
@tool
def web_search_tool(query: str) -> str:
    """
    Simulates a web search and returns structured output using bullet points and emojis.
    Handles both string and list responses.
    """
    response = load_llm().invoke(query)

    if not response:
        return "❗ No information found."

    global x
    x = True
    print("Web is here")

    # If response is a list of items
    if isinstance(response, list):
        formatted_lines = [f"🔸 {item.strip()}" for item in response if item.strip()]
        return "\n".join(formatted_lines)

    # If response is a string, try to split using bullet markers
    if isinstance(response, str):
        lines = response.split("• ")
        formatted_lines = [f"🔸 {line.strip()}" for line in lines if line.strip()]
        return "\n".join(formatted_lines)

    return "⚠️ Unexpected data format received."


def web_check():
    global x
 
    print("check for true false")
    print(x)
    return x
def web_change():
    global x
    print("turned to false")
    x=False
# Create the tool for the agent

 


 

# ================================================CI tool=========================================================================================



# @tool
# def get_device_list_by_email(email: str) -> dict:
#     """This tool retrieves a list of devices associated with the provided email, categorizing them into laptops and VMs."""
    
#     if not email:
#         return {"error": "Please provide a valid email."}
 
#     url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
#     # Prepare the payload
#     json_data = {
#         "operation": "core/get",
#         "class": "Person",
#         "key": f"SELECT Person WHERE email='{email}'",
#         "output_fields": "cis_list"
#     }
    
#     json_string = json.dumps(json_data)
    
#     # Prepare headers for Basic Auth
#     auth = (USERNAME, PASSWORD)
    
#     # Make the GET request
#     response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
#     # Handle the response
#     if response.status_code == 200:
#         data = response.json()
        
#         ci_data = data.get("objects", [])
        
#         # Optionally save the response to a file
#         with open("ci_data.json", 'w') as file:
#             file.write(json.dumps(ci_data, indent=4))
 
#         if ci_data:
#             laptops = []
#             vms = []
#             other =[]
            
#             for incident_key, incident in ci_data.items():
#                 cis_list = incident.get('fields', {}).get('cis_list', [])
                
#                 if cis_list and isinstance(cis_list, list):
#                     for device in cis_list:
#                         functionalci_type = device.get("functionalci_id_finalclass_recall", "No functionalci_name found")
#                         functionalci_name = device.get("functionalci_name", "No functionalci_name found")
#                         functionalci_id = device.get("functionalci_id", "No functionalci_id found")
                        
#                         if functionalci_type.lower() == "pc":
#                             laptops.append({
#                                 "functionalci_id": functionalci_id,
#                                 "functionalci_name": functionalci_name
#                             })           
#                         elif functionalci_type.lower() == "virtualmachine":
#                             vms.append({
#                                 "functionalci_id": functionalci_id,
#                                 "functionalci_name": functionalci_name
#                             })
#                         else:
#                             other.append({
#                                 "functionalci_id": functionalci_id,
#                                 "functionalci_name": functionalci_name
#                             })
                    
#             # Return the categorized devices
#             response = {}
#             response['laptops'] = laptops
#             response['vms'] = vms 
#             if len(other)!= 0 :
#                 response['other'] = other
#             # return {
#             #     "laptops": laptops,
#             #     "vms": vms
#             # }
#             return response
#         else:
#             return {"No data found for the given email."}
    
#     else:
#         return {"error": "Sorry, there was an issue fetching the incident details."}

 
# @tool
# def get_device_list_by_email(email: str , require_device_list_type :str) -> dict:
#     """This tool retrieves a list of devices associated with the provided email, categorizing them into laptops and VMs."""
    
#     if not email:
#         return {"error": "Please provide a valid email."}
 
#     url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
#     # Prepare the payload
#     json_data = {
#         "operation": "core/get",
#         "class": "Person",
#         "key": f"SELECT Person WHERE email='{email}'",
#         "output_fields": "cis_list"
#     }
    
#     json_string = json.dumps(json_data)
    
#     # Prepare headers for Basic Auth
#     auth = (USERNAME, PASSWORD)
    
#     # Make the GET request
#     response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
#     # Handle the response
#     if response.status_code == 200:
#         data = response.json()
        
#         ci_data = data.get("objects", [])
        
#         # Optionally save the response to a file
#         with open("ci_data.json", 'w') as file:
#             file.write(json.dumps(ci_data, indent=4))
 
#         if ci_data:
#             laptops = []
#             vms = []
#             other =[]
            
#             for incident_key, incident in ci_data.items():
#                 cis_list = incident.get('fields', {}).get('cis_list', [])
                
#                 if cis_list and isinstance(cis_list, list):
#                     for device in cis_list:
#                         functionalci_type = device.get("functionalci_id_finalclass_recall", "No functionalci_name found")
#                         functionalci_name = device.get("functionalci_name", "No functionalci_name found")
#                         functionalci_id = device.get("functionalci_id", "No functionalci_id found")
                        
#                         # Classify as laptop or VM based on the functionalci_name
#                         # if 'dell' in functionalci_name.lower():
#                         #     laptops.append({
#                         #         "functionalci_id": functionalci_id,
#                         #         "functionalci_name": functionalci_name
#                         #     })
#                         # elif 'sa' in functionalci_name.lower() or 'gpn' in functionalci_name.lower():
#                         #     vms.append({
#                         #         "functionalci_id": functionalci_id,
#                         #         "functionalci_name": functionalci_name
#                         #     })
#                         if functionalci_type.lower() == "pc":
#                             laptops.append({
#                                 "functionalci_id": functionalci_id,
#                                 "functionalci_name": functionalci_name
#                             })           
#                         elif functionalci_type.lower() == "virtualmachine":
#                             vms.append({
#                                 "functionalci_id": functionalci_id,
#                                 "functionalci_name": functionalci_name
#                             })
#                         else:
#                             other.append({
#                                 "functionalci_id": functionalci_id,
#                                 "functionalci_name": functionalci_name
#                             })
                    
#             # Return the categorized devices
#             response = {}
#             response['laptop'] = laptops
#             response['vm'] = vms
#             if len(other)!= 0 :
#                 response['other'] = other
#             # return {
#             #     "laptops": laptops,
#             #     "vms": vms
#             # }
#             final_answer = response[require_device_list_type]
#             return final_answer
#         else:
#             return {"No data found for the given email."}
    
#     else:
#         return {"error": "Sorry, there was an issue fetching the incident details."}
 
 
 
 

@tool
def get_device_list_by_email(email: str, system:str) -> dict:
    """This tool retrieves a list of devices associated with the provided email, categorizing them into laptops and VMs."""
    print("device==================>",system)
    print("email+++++++++++++++++++>",email)
    if not email:
        return {"error": "Please provide a valid email."}
 
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Person",
        "key": f"SELECT Person WHERE email='{email}'",
        "output_fields": "cis_list"
    }
    
    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()
        
        ci_data = data.get("objects", [])
        
        # Optionally save the response to a file
        with open("ci_data.json", 'w') as file:
            file.write(json.dumps(ci_data, indent=4))
 
        if ci_data:
            laptops = []
            vms = []
            other =[]
            
            for incident_key, incident in ci_data.items():
                cis_list = incident.get('fields', {}).get('cis_list', [])
                
                if cis_list and isinstance(cis_list, list):
                    for device in cis_list:
                        functionalci_type = device.get("functionalci_id_finalclass_recall", "No functionalci_name found")
                        functionalci_name = device.get("functionalci_name", "No functionalci_name found")
                        functionalci_id = device.get("functionalci_id", "No functionalci_id found")
                        
                        if functionalci_type.lower() == "pc":
                            laptops.append({
                                "functionalci_id": functionalci_id,
                                "functionalci_name": functionalci_name
                            })           
                        elif functionalci_type.lower() == "virtualmachine":
                            vms.append({
                                "functionalci_id": functionalci_id,
                                "functionalci_name": functionalci_name
                            })
                        else:
                            other.append({
                                "functionalci_id": functionalci_id,
                                "functionalci_name": functionalci_name
                            })
                    
            # Return the categorized devices
            response = {}
            response['laptops'] = laptops
            response['vms'] = vms 
            if len(other)!= 0 :
                response['other'] = other
            # return {
            #     "laptops": laptops,
            #     "vms": vms
            # }
            if system.lower()=="laptop":
                return response['laptops']
            elif system.lower()=="vm":
                return response['vms']
            else:
                return "No data found for the given email."
        else:
            return {"No data found for the given email."}
    
    else:
        return {"error": "Sorry, there was an issue fetching the incident details."}
 


#  ------------------------------------------------------------------------------------------------------------------- #



# ================================================identify_profile_tool tool=========================================================================================
 
 
@tool
def identify_user_profile(email: str) -> dict:
    """This tool uses the user's email to determine if they are a **user** or an **agent** and retrieve their **contact ID**."""
    
    if not email:
        return "Please provide a valid email."

    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "User",
        "key": f"SELECT User WHERE email='{email}'",
        "output_fields": "*"
    }
    
    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()
        result_dict = {}

        for v in data["objects"].values():
            profile_list = v["fields"].get("profile_list", [])
            if profile_list and isinstance(profile_list, list):
                profile_id_list = [profile_list[i].get("profileid", "No profile found") for i in range(len(profile_list))]

        if '5' in profile_id_list:
            profile_name = 'Agent'
        else:
            profile_name = 'User'

        result_dict['contactid'] = v["fields"]["contactid"]
        result_dict['org_id'] = v["fields"]["org_id"]
        result_dict['profile_name'] = profile_name
        
        # Optionally store this in global_tool_data if necessary
        # global_tool_data["identify_profile_tool"] = result_dict

        return result_dict
    else:
        return "Sorry, there was an issue fetching the details for the user."


# ================================================profile_based_incident_tool_all_tickets=========================================================================================


# Updated by Abhishek arya on April 16th 2025
@tool
def get_incident_ids_by_contact(email: str) -> list:
    """This tool retrieves all associated incident IDs for a given **contact ID** and **status**."""
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."

    


@tool
def get_incident_ids_for_agent(email: str) -> list:
    """This tool retrieves all associated incident IDs for a given **agent_id**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE agent_id = {contactid}",
        "output_fields": "ref, caller_id"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."

    


# ================================================profile_based_incident_tool tool_user=========================================================================================
 
 
# Updated by Abhishek arya on April 16th 2025
@tool
def get_incident_ids_by_contact_and_status(email: str, status: str) -> list:
    """This tool retrieves all associated incident IDs for a given **contact ID** and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE status = '{status}' AND caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."





# ================================================profile_based_incident_tool tool_agent=========================================================================================




@tool
def get_service_incident_ids_by_contact(email: str) -> list:
    """This tool retrieves all associated **UserRequest** incident IDs for a given **contact ID**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."




@tool
def get_service_incident_ids_for_agent(email: str) -> list:
    """This tool retrieves all associated **UserRequest** incident IDs for a given **contact ID**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE agent_id = {contactid}",
        "output_fields": "ref, caller_id"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


# ================================================profile_based_incident_tool tool_user=========================================================================================
 
 
 
@tool
def get_service_incident_ids_by_status(email: str, status: str) -> list:
    """This tool retrieves all associated **UserRequest** incident IDs for a given **contact ID** and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE status = '{status}' AND caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."



#pdated by Abhishek arya on 16th April 2025
@tool
def get_agent_incident_ids_by_status(email: str, status: str) -> list:
    """This tool retrieves all associated **Incident** IDs for a given **contact ID** (agent) and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE status = '{status}' AND agent_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."







@tool
def get_service_incident_ids_by_agent_with_status(email: str, status: str) -> list:
    """This tool retrieves all associated **UserRequest** IDs for a given **contact ID** (agent) and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE status = '{status}' AND agent_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."




@tool
def get_incidents_by_date_range(email: str, from_date: str, to_date: str) -> list:
    """This tool retrieves all incidents for a given **contact ID** and **status** within the specified **date range**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' AND start_date <= '{to_date} 23:59:59' AND caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or empty, return "NO TICKETS"
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"

        return {
            "incident_count": len(incidents),
            "recent_incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_incidents_by_date_for_user(email: str, date: str) -> dict:
    """
    This tool retrieves all incidents for a given agent (based on their email) for a specific date (YYYY-MM-DD or natural language like '16th July 2024').
    """
    if not email:
        return "Please provide an email."

    try:
        parsed_date = date_parser.parse(date)
        date_str = parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Invalid date format. Error: {str(e)}"

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    if not contactid:
        return "Contact ID not found for the given email."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE start_date >= '{date_str} 00:00:00' AND start_date <= '{date_str} 23:59:59' AND caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"
        return {
            "incident_count": len(incidents),
            "date": date_str,
            "incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_incidents_by_date_with_status_for_user(email: str, date: str, status: str) -> dict:
    """
    Fetches recent incidents for a given contact ID and status within the specified date.
    Returns the count of incidents and details if available; otherwise, returns 'NO TICKETS'.
    """
    if not email:
        return "Please provide an email."

    try:
        parsed_date = date_parser.parse(date)
        date_str = parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Invalid date format. Error: {str(e)}"

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    if not contactid:
        return "Contact ID not found for the given email."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE start_date >= '{date_str} 00:00:00' AND start_date <= '{date_str} 23:59:59' AND caller_id = {contactid} AND status = '{status}'",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"
        return {
            "incident_count": len(incidents),
            "date": date_str,
            "status": status,
            "incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_incidents_by_date_for_agent(email: str, date: str) -> dict:
    """
    This tool retrieves all incidents for a given agent (based on their email) for a specific date (YYYY-MM-DD or natural language like '16th July 2024').
    """
    if not email:
        return "Please provide an email."

    try:
        parsed_date = date_parser.parse(date)
        date_str = parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Invalid date format. Error: {str(e)}"

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    if not contactid:
        return "Contact ID not found for the given email."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE start_date >= '{date_str} 00:00:00' AND start_date <= '{date_str} 23:59:59' AND agent_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"
        return {
            "incident_count": len(incidents),
            "date": date_str,
            "incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_incidents_by_date_with_status_for_agent(email: str, date: str, status: str) -> dict:
    """
    Fetches recent incidents for a given contact ID and status within the specified date.
    Returns the count of incidents and details if available; otherwise, returns 'NO TICKETS'.
    """
    if not email:
        return "Please provide an email."

    try:
        parsed_date = date_parser.parse(date)
        date_str = parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Invalid date format. Error: {str(e)}"

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    if not contactid:
        return "Contact ID not found for the given email."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE start_date >= '{date_str} 00:00:00' AND start_date <= '{date_str} 23:59:59' AND agent_id = {contactid} AND status = '{status}'",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"
        return {
            "incident_count": len(incidents),
            "date": date_str,
            "status": status,
            "incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_UserRequest_by_date_for_user(email: str, date: str) -> dict:
    """
    This tool retrieves all incidents for a given agent (based on their email) for a specific date (YYYY-MM-DD or natural language like '16th July 2024').
    """
    if not email:
        return "Please provide an email."

    try:
        parsed_date = date_parser.parse(date)
        date_str = parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Invalid date format. Error: {str(e)}"

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    if not contactid:
        return "Contact ID not found for the given email."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE start_date >= '{date_str} 00:00:00' AND start_date <= '{date_str} 23:59:59' AND caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"
        return {
            "incident_count": len(incidents),
            "date": date_str,
            "incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_UserRequest_by_date_with_status_for_user(email: str, date: str, status: str) -> dict:
    """
    Fetches recent incidents for a given contact ID and status within the specified date.
    Returns the count of incidents and details if available; otherwise, returns 'NO TICKETS'.
    """
    if not email:
        return "Please provide an email."

    try:
        parsed_date = date_parser.parse(date)
        date_str = parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Invalid date format. Error: {str(e)}"

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    if not contactid:
        return "Contact ID not found for the given email."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE start_date >= '{date_str} 00:00:00' AND start_date <= '{date_str} 23:59:59' AND caller_id = {contactid} AND status = '{status}'",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"
        return {
            "incident_count": len(incidents),
            "date": date_str,
            "status": status,
            "incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_UserRequest_by_date_for_agent(email: str, date: str) -> dict:
    """
    This tool retrieves all incidents for a given agent (based on their email) for a specific date (YYYY-MM-DD or natural language like '16th July 2024').
    """
    if not email:
        return "Please provide an email."

    try:
        parsed_date = date_parser.parse(date)
        date_str = parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Invalid date format. Error: {str(e)}"

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    if not contactid:
        return "Contact ID not found for the given email."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE start_date >= '{date_str} 00:00:00' AND start_date <= '{date_str} 23:59:59' AND agent_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"
        return {
            "incident_count": len(incidents),
            "date": date_str,
            "incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_UserRequest_by_date_with_status_for_agent(email: str, date: str, status: str) -> dict:
    """
    Fetches recent incidents for a given contact ID and status within the specified date.
    Returns the count of incidents and details if available; otherwise, returns 'NO TICKETS'.
    """
    if not email:
        return "Please provide an email."

    try:
        parsed_date = date_parser.parse(date)
        date_str = parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Invalid date format. Error: {str(e)}"

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    if not contactid:
        return "Contact ID not found for the given email."

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE start_date >= '{date_str} 00:00:00' AND start_date <= '{date_str} 23:59:59' AND agent_id = {contactid} AND status = '{status}'",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"
        return {
            "incident_count": len(incidents),
            "date": date_str,
            "status": status,
            "incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_incidents_by_date_range_for_agent(email: str, from_date: str, to_date: str) -> list:
    """This tool retrieves all incidents for a given **contact ID** and **status** within the specified **date range**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' AND start_date <= '{to_date} 23:59:59' AND agent_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or empty, return "NO TICKETS"
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"

        return {
            "incident_count": len(incidents),
            "recent_incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}


    

@tool
def get_incidents_by_date_range_with_status(email: str, from_date: str, to_date: str, status: str) -> dict:
    """Fetches recent incidents for a given contact ID and status within the specified date range.
    
    Returns the count of incidents and details if available; otherwise, returns 'NO TICKETS'.
    """

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or empty, return "NO TICKETS"
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"

        return {
            "incident_count": len(incidents),
            "recent_incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_incidents_by_date_range_with_status_for_agent(email: str, from_date: str, to_date: str, status: str) -> dict:
    """Fetches recent incidents for a given contact ID and status within the specified date range.
    
    Returns the count of incidents and details if available; otherwise, returns 'NO TICKETS'.
    """

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or empty, return "NO TICKETS"
        incidents = data.get("objects", [])
        if not incidents:
            return "NO TICKETS"

        return {
            "incident_count": len(incidents),
            "recent_incidents": incidents
        }

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_recent_incidents(email: str, days: int = 1) -> dict:
    """Fetches recent incidents for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Dynamic date calculation
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid}"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects")
        if not incidents:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


#Updated bu abhishek Arya on 16th April 2025
@tool
def get_recent_incidents_for_agent(email: str, days: int = 1) -> dict:
    """Fetches recent incidents for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Dynamic date calculation
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid}"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects")
        if not incidents:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}




@tool
def get_monthly_incidents(email: str, days: int = 30) -> dict:
    """Fetches recent incidents for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Set from_date as the first day of the current month
    today = datetime.today()
    from_date = today.replace(day=1).strftime("%Y-%m-%d")  # First day of current month
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid}"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_random_monthly_incidents(email: str, months: int) -> dict:
    """Fetches incidents for a given contact ID within the last `months` months."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    # Calculate from_date as the first day of the month 'months' ago
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    from_date = (first_day_of_current_month - timedelta(days=30 * months)).replace(day=1).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid}"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"
    

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_monthly_incidents_for_agent(email: str, days: int = 30) -> dict:
    """Fetches recent incidents for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Set from_date as the first day of the current month
    today = datetime.today()
    from_date = today.replace(day=1).strftime("%Y-%m-%d")  # First day of current month
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid}"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_random_monthly_incidents_for_agent(email: str, months: int) -> dict:
    """Fetches incidents for a given contact ID within the last `months` months."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    
    # Calculate from_date as the first day of the month 'months' ago
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    from_date = (first_day_of_current_month - timedelta(days=30 * months)).replace(day=1).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid}"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"
    

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_monthly_incidents_with_status(email: str, status: str, days: int = 30) -> dict:
    """Fetches recent incidents for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Set from_date as the first day of the current month
    today = datetime.today()
    from_date = today.replace(day=1).strftime("%Y-%m-%d")  # First day of current month
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_random_monthly_incidents_with_status(email: str, months: int, status: str) -> dict:
    """Fetches incidents for a given contact ID within the last `months` months."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    
    # Calculate from_date as the first day of the month 'months' ago
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    from_date = (first_day_of_current_month - timedelta(days=30 * months)).replace(day=1).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"
    

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_monthly_incidents_with_status_for_agent(email: str, status: str, days: int = 30) -> dict:
    """Fetches recent incidents for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")


    # Set from_date as the first day of the current month
    today = datetime.today()
    from_date = today.replace(day=1).strftime("%Y-%m-%d")  # First day of current month
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}

@tool
def get_random_monthly_incidents_with_status_for_agent(email: str, months: int, status: str) -> dict:
    """Fetches incidents for a given contact ID within the last `months` months."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    
    # Calculate from_date as the first day of the month 'months' ago
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    from_date = (first_day_of_current_month - timedelta(days=30 * months)).replace(day=1).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"
    

    return {"error": "Sorry, there was an issue fetching the incident details."}


    

@tool
def get_UserRequest_by_date_range(email: str, from_date: str, to_date: str) -> list:
    """This tool retrieves all incidents for a given **contact ID** within the specified **date range**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' AND start_date <= '{to_date} 23:59:59' AND caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()
        user_profile_incident = data.get("objects", [])
        
        # Optionally write the data to a file for review (you may remove this in production)
        with open("Date_Wise_incidents.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))
        
        return user_profile_incident
    else:
        return "Sorry, there was an issue fetching the incident details."



@tool
def get_UserRequest_by_date_range_for_agent(email: str, from_date: str, to_date: str) -> list:
    """This tool retrieves all incidents for a given **contact ID** within the specified **date range**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' AND start_date <= '{to_date} 23:59:59' AND agent_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()
        user_profile_incident = data.get("objects", [])
        
        # Optionally write the data to a file for review (you may remove this in production)
        with open("Date_Wise_incidents.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))
        
        return user_profile_incident
    else:
        return "Sorry, there was an issue fetching the incident details."




@tool
def get_UserRequest_by_date_range_with_status(email: str, from_date: str, to_date: str, status: str) -> list:
    """This tool retrieves all incidents for a given **contact ID** and **status** within the specified **date range**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' AND start_date <= '{to_date} 23:59:59' AND caller_id = {contactid} AND status = {status}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


#Update by Abhishek Arya on 16th April 2025
@tool
def get_UserRequest_by_date_range_with_status_for_agent(email: str, from_date: str, to_date: str, status: str) -> list:
    """This tool retrieves all UserRequest for a given **contact ID** and **status** within the specified **date range**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' AND start_date <= '{to_date} 23:59:59' AND agent_id = {contactid} AND status = {status}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


# @tool
# def count_UserRequest_by_date_range_with_status(contactid: int, from_date: str, to_date: str, status: str) -> dict:
#     """Retrieves the count of UserRequest for a given contact ID and STATUS within the specified date range."""

#     if not contactid or not from_date or not to_date or not status:
#         return {"error": "Please provide contact ID, from_date, to_date, and status."}

#     url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

#     # Fix: Ensure `status` is enclosed in single quotes
#     query = (
#         f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
#         f"AND start_date <= '{to_date} 23:59:59' "
#         f"AND caller_id = {contactid} AND status = '{status}'"
#     )

#     json_data = {
#         "operation": "core/get",
#         "class": "UserRequest",
#         "key": query,
#         "output_fields": "ref"
#     }

#     response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

#     if response.status_code == 200:
#         data = response.json()
#         incidents = data.get("objects", [])

#         # Get count of incidents
#         if len(incidents) > 1:
#             incident_count = len(incidents)
#         else:
#             print("NO Tickets")

#         # Save response to a file (optional)
#         with open("Date_Wise_incidents.json", "w") as file:
#             json.dump(incidents, file, indent=4)

#         return {"incident_count": incident_count}

#     return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_recent_UserRequest(email: str, days: int = 1) -> dict:
    """Fetches recent UserRequest for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Dynamic date calculation
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid}"
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_recent_UserRequest_for_agent(email: str, days: int = 1) -> dict:
    """Fetches recent UserRequest for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Dynamic date calculation
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid}"
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_monthly_UserRequest(email: str, days: int = 30) -> dict:
    """Fetches recent incidents for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Set from_date as the first day of the current month
    today = datetime.today()
    from_date = today.replace(day=1).strftime("%Y-%m-%d")  # First day of current month
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid} "
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}

@tool
def get_random_monthly_UserRequest(email: str, months: int) -> dict:
    """Fetches incidents for a given contact ID within the last `months` months."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    # Calculate from_date as the first day of the month 'months' ago
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    from_date = (first_day_of_current_month - timedelta(days=30 * months)).replace(day=1).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid} "
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_monthly_UserRequest_for_agent(email: str, days: int = 30) -> dict:
    """Fetches recent incidents for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    # Set from_date as the first day of the current month
    today = datetime.today()
    from_date = today.replace(day=1).strftime("%Y-%m-%d")  # First day of current month
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid} "
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_random_monthly_UserRequest_for_agent(email: str, months: int) -> dict:
    """Fetches incidents for a given contact ID within the last `months` months."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    # Calculate from_date as the first day of the month 'months' ago
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    from_date = (first_day_of_current_month - timedelta(days=30 * months)).replace(day=1).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} "
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"
    

    return {"error": "Sorry, there was an issue fetching the incident details."}




@tool
def get_monthly_UserRequest_with_status(email: str, status: str, days: int = 30) -> dict:
    """Fetches recent incidents for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Set from_date as the first day of the current month
    today = datetime.today()
    from_date = today.replace(day=1).strftime("%Y-%m-%d")  # First day of current month
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_random_monthly_UserRequest_with_status(email: str, months: int, status: str) -> dict:
    """Fetches incidents for a given contact ID within the last `months` months."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    # Calculate from_date as the first day of the month 'months' ago
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    from_date = (first_day_of_current_month - timedelta(days=30 * months)).replace(day=1).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"
    

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_monthly_UserRequest_with_status_for_agent(email: str, status: str, days: int = 30) -> dict:
    """Fetches recent incidents for a given contact ID and status within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Set from_date as the first day of the current month
    today = datetime.today()
    from_date = today.replace(day=1).strftime("%Y-%m-%d")  # First day of current month
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if len(incidents) >= 1:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_random_monthly_UserRequest_with_status_for_agent(email: str, months: int, status: str) -> dict:
    """Fetches incidents for a given contact ID within the last `months` months."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    # Calculate from_date as the first day of the month 'months' ago
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    from_date = (first_day_of_current_month - timedelta(days=30 * months)).replace(day=1).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")  # Today's date

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"
    

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_UserRequest_tickets_for_random_days(email: str, days: int) -> dict:
    """Fetches UserRequest for a given contact ID within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Calculate date range based on user input
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid} "
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}




@tool
def get_UserRequest_tickets_with_status_for_random_days(email: str, days: int, status: str) -> dict:
    """Fetches UserRequest for a given contact ID within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Calculate date range based on user input
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_Incident_tickets_for_random_days(email: str, days: int) -> dict:
    """Fetches incidents for a given contact ID within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Calculate date range based on user input
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND caller_id = {contactid} "
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_Incident_tickets_with_status_for_random_days(email: str, days: int, status: str) -> dict:
    """Fetches incidents for a given contact ID within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Calculate date range based on user input
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}




@tool
def get_Incident_tickets_for_random_days_for_agent(email: str, days: int) -> dict:
    """Fetches incidents for a given contact ID within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Calculate date range based on user input
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} "
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_Incident_tickets_with_status_for_random_days_for_agent(email: str, days: int, status: str) -> dict:
    """Fetches incidents for a given contact ID within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Calculate date range based on user input
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT Incident WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}


@tool
def get_UserRequest_tickets_for_random_days_for_agent(email: str, days: int) -> dict:
    """Fetches UserRequest for a given contact ID within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Calculate date range based on user input
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} "
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}



@tool
def get_UserRequest_tickets_with_status_for_random_days_for_agent(email: str, days: int, status: str) -> dict:
    """Fetches UserRequest for a given contact ID within the last `days` days."""

    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")

    # Calculate date range based on user input
    to_date = datetime.today().strftime("%Y-%m-%d")  # Today's date
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")  # N days ago

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = (
        f"SELECT UserRequest WHERE start_date >= '{from_date} 00:00:00' "
        f"AND start_date <= '{to_date} 23:59:59' "
        f"AND agent_id = {contactid} AND status = '{status}'"
    )

    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": query,
        "output_fields": "ref, title, start_date, status"
    }

    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        data = response.json()
        incidents = data.get("objects", [])
        if incidents:
            return {
                "incident_count": len(incidents),
                "recent_incidents": incidents
            }
        else:
            return "NO TICKETS"

    return {"error": "Sorry, there was an issue fetching the incident details."}




@tool
def create_incident_with_ci(org_id: int, contactid: int, incident_title: str, 
                            incident_description: str, service_id: int, servicesubcategory_id: int, 
                            functionalci_id: int) -> str:
    """Tool to create an Incident with associated CI details.
    This tool sends a create request using JSON and returns the incident reference, title, and origin.
    """
    # print("org_id type",type(org_id))
    # print("contactid type", contactid)
    

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Prepare the payload for creating the incident
        json_data = {
            "operation": "core/create",
            "comment": "Created by Teamsbot",
            "class": "Incident",
            "output_fields": "ref,title,origin",
            "fields": {
                "org_id": org_id,
                "caller_id": contactid,
                "origin": "teamsbot",
                "title": incident_title,
                "description": incident_description,
                "service_id": service_id,
                "servicesubcategory_id": servicesubcategory_id,
                "functionalcis_list": [{"functionalci_id": functionalci_id}]
            }
        }

        # Convert the payload to a JSON string
        json_string = json.dumps(json_data)

        # Make the POST request
        auth = (USERNAME, PASSWORD)
        response = requests.post(url, data={"version": "1.0", "json_data": json_string}, auth=auth)

        # Handle the response
        if response.status_code == 200:
            data = response.json()
            print(data, "============>>>>>>>>>>>>>>>>>>>>>>>.")

            incident_data = data.get("objects", {})  # Ensure this is a dictionary
            
            if incident_data:
                for incident_key, incident in incident_data.items():
                    friendly_name = incident.get('fields', {}).get('ref', 'Unknown')
                    return f"Incident Created: {friendly_name}"
                
            return "Failed to create the incident. Please try again."
        else:
            return "Sorry, there was an issue creating the incident."
    
    except Exception as e:
        return f"Error while creating incident: {str(e)}"






@tool
def create_incident_with_ci_without_sub(org_id: int, contactid: int, incident_title: str, 
                                        incident_description: str, service_id: int, functionalci_id: int) -> str:
    """Tool to create an Incident with associated CI details and without subservice.
    This tool sends a create request using JSON and returns the incident reference, title, and origin.
    """
    print("description===============>",incident_description)
    print("title+++++++++++++++++++++>",incident_title)
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    
    try:
        # Prepare the payload for creating the incident
        json_data = {
            "operation": "core/create",
            "comment": "Created by Teamsbot",
            "class": "Incident",
            "output_fields": "ref,title,origin",
            "fields": {
                "org_id": org_id,
                "caller_id": contactid,
                "origin": "teamsbot",
                "title": incident_title,
                "description": incident_description,
                "service_id": service_id,
                "functionalcis_list": [{"functionalci_id": functionalci_id}]
            }
        }

        # Convert the payload to a JSON string
        json_string = json.dumps(json_data)

        # Make the POST request
        auth = (USERNAME, PASSWORD)
        response = requests.post(url, data={"version": "1.0", "json_data": json_string}, auth=auth)

        # Handle the response
        if response.status_code == 200:
            data = response.json()
            print(data, "============>>>>>>>>>>>>>>>>>>>>>>>.")

            incident_data = data.get("objects", {})  # Ensure this is a dictionary
            
            if incident_data:
                for incident_key, incident in incident_data.items():
                    friendly_name = incident.get('fields', {}).get('ref', 'Unknown')
                    return f"Incident Created: {friendly_name}"
                
            return "Failed to create the incident. Please try again."
        else:
            return "Sorry, there was an issue creating the incident."
    
    except Exception as e:
        return f"Error while creating incident: {str(e)}"


# ************************************************ Service TOOL*******************************************************
 
@tool
def create_service_request(org_id: int, contactid: int, incident_title: str, incident_description: str, 
                           service_id: int, servicesubcategory_id: int) -> str:
    """Creates a service request ticket with type of org_id as int."""
    
    # API URL
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Prepare the payload for creating the service request
        json_data = {
            "operation": "core/create",
            "comment": "Created by Teamsbot.",
            "class": "UserRequest",
            "output_fields": "ref,title,origin",
            "fields": {
                "org_id": org_id,
                "caller_id": contactid,
                "origin": "teamsbot",
                "title": incident_title,
                "description": incident_description,
                "service_id": service_id,
                "servicesubcategory_id": servicesubcategory_id
            }
        }

        json_string = json.dumps(json_data)

        # Prepare headers for Basic Auth
        auth = (USERNAME, PASSWORD)  

        # Make the POST request
        response = requests.post(url, data={"version": "1.0", "json_data": json_string}, auth=auth)

        # Handle the response
        if response.status_code == 200:
            data = response.json()
            print(data, "============>>>>>>>>>>>>>>>>>>>>>>>.")
            
            incident_data = data.get("objects", [])
            
            if incident_data:
                for incident_key, incident in incident_data.items():
                    friendly_name = incident.get('fields', {}).get('ref', 'Unknown')
                    print(f"Incident Created~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~: {friendly_name}")
                return f"Incident Created: {friendly_name}"
            else:
                return "Failed to create the incident. Please try again."
        else:
            return "Sorry, there was an issue creating the incident."

    except Exception as e:
        return f"Error while creating service request: {str(e)}"





@tool
def create_service_request_without_sub(org_id: int, contactid: int, incident_title: str, 
                                       incident_description: str, service_id: str) -> str:
    """Creates an incident/event in the system if the user gives a command/order to create an incident without subservice."""

    # API URL
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    try:
        # Prepare the payload for creating the service request
        json_data = {
            "operation": "core/create",
            "comment": "Created by Teamsbot.",
            "class": "UserRequest",
            "output_fields": "ref,title,origin",
            "fields": {
                "org_id": org_id,
                "caller_id": contactid,
                "origin": "teamsbot",
                "title": incident_title,
                "description": incident_description,
                "service_id": service_id
            }
        }

        json_string = json.dumps(json_data)

        # Prepare headers for Basic Auth
        auth = (USERNAME, PASSWORD)

        # Make the POST request
        response = requests.post(url, data={"version": "1.0", "json_data": json_string}, auth=auth)

        # Handle the response
        if response.status_code == 200:
            data = response.json()
            print(data, "============>>>>>>>>>>>>>>>>>>>>>>>.")
            
            incident_data = data.get("objects", [])

            if incident_data:
                for incident_key, incident in incident_data.items():
                    friendly_name = incident.get('fields', {}).get('ref', 'Unknown')
                    print(f"Incident Created~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~: {friendly_name}")
                return f"Incident Created: {friendly_name}"
            else:
                return "Failed to create the incident. Please try again."
        else:
            return "Sorry, there was an issue creating the incident."

    except Exception as e:
        return f"Error while creating service request: {str(e)}"


@tool
def create_user_request_with_ci(org_id: int, contactid: int, incident_title: str, 
                                incident_description: str, service_id: str, 
                                servicesubcategory_id: int, functionalci_id: int) -> str:
    """Tool to create a service request with associated CI details, using JSON, and returns the incident reference, title, and origin."""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    try:
        # Prepare the payload for creating the user request
        json_data = {
            "operation": "core/create",
            "comment": "Created by Teamsbot",
            "class": "UserRequest",
            "output_fields": "ref,title,origin",
            "fields": {
                "org_id": org_id,
                "caller_id": contactid,
                "origin": "teamsbot",
                "title": incident_title,
                "description": incident_description,
                "service_id": service_id,
                "servicesubcategory_id": servicesubcategory_id,
                "functionalcis_list": [{"functionalci_id": functionalci_id}]
            }
        }

        # Convert the payload to a JSON string
        json_string = json.dumps(json_data)

        # Prepare headers for Basic Auth
        auth = (USERNAME, PASSWORD)

        # Make the POST request
        response = requests.post(url, data={"version": "1.0", "json_data": json_string}, auth=auth)

        # Handle the response
        if response.status_code == 200:
            data = response.json()
            print(data, "============>>>>>>>>>>>>>>>>>>>>>>>.")

            incident_data = data.get("objects", {})

            if incident_data:
                for incident_key, incident in incident_data.items():
                    friendly_name = incident.get('fields', {}).get('ref', 'Unknown')
                    return f"Incident Created: {friendly_name}"
            else:
                return "Failed to create the incident. Please try again."
        else:
            return "Sorry, there was an issue creating the incident."

    except Exception as e:
        return f"Error while creating incident: {str(e)}"



@tool
def create_user_request_with_ci_without_sub(org_id: int, contactid: int, incident_title: str, 
                                            incident_description: str, service_id: int, 
                                            functionalci_id: int) -> str:
    """Tool to create a service request with associated CI details, without subservice, using JSON, and returns the incident reference, title, and origin."""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    try:
        # Prepare the payload for creating the user request
        json_data = {
            "operation": "core/create",
            "comment": "Created by Teamsbot",
            "class": "UserRequest",
            "output_fields": "ref,title,origin",
            "fields": {
                "org_id": org_id,
                "caller_id": contactid,
                "origin": "teamsbot",
                "title": incident_title,
                "description": incident_description,
                "service_id": service_id,
                "functionalcis_list": [{"functionalci_id": functionalci_id}]
            }
        }

        # Convert the payload to a JSON string
        json_string = json.dumps(json_data)

        # Prepare headers for Basic Auth
        auth = (USERNAME, PASSWORD)

        # Make the POST request
        response = requests.post(url, data={"version": "1.0", "json_data": json_string}, auth=auth)

        # Handle the response
        if response.status_code == 200:
            data = response.json()
            print(data, "============>>>>>>>>>>>>>>>>>>>>>>>.")

            incident_data = data.get("objects", {})

            if incident_data:
                for incident_key, incident in incident_data.items():
                    friendly_name = incident.get('fields', {}).get('ref', 'Unknown')
                    return f"Incident Created: {friendly_name}"
            else:
                return "Failed to create the incident. Please try again."
        else:
            return "Sorry, there was an issue creating the incident."

    except Exception as e:
        return f"Error while creating incident: {str(e)}"


##################################json_search_tool###################################################################################




@tool
def json_search(word: str) -> list:
    """
    Search function that looks through the JSON and finds matches based on the query word.
    Returns a list of relevant service details or an empty list if no match is found.
    This function can now handle direct subservice name queries.
    """
    print("**************user_query***************************")
    print(word)
    final_results = []

    try:
        # Load the JSON data
        with open('services_data_new.json', 'r') as json_file:
            data = json.load(json_file)

        # Loop through service families
        for sf_key, sf_val in data.items():
            # Log the structure
            # print(f"service_family_infos: {sf_val.get('service_family_infos', 'No service_family_infos found')}")

            if "service_family_name" in sf_val and word.lower() in sf_val["service_family_name"].lower():
                final_results.append({
                    "service family name": sf_val["service_family_name"],
                    "service_family_id": sf_val.get("service_family_id", "N/A"),
                    "has_subservices": True
                })

            # Loop through services (inside the family)
            if "service_family_infos" in sf_val:
                for s_key, s_val2 in sf_val["service_family_infos"].items():
                    # print(f"Service Name: {s_key}, Details: {s_val2}")

                    if "service_name" in s_val2 and word.lower() in s_val2["service_name"].lower():
                        result = {
                            "service family name": sf_key,
                            "service_family_id": sf_val.get("service_family_id", "N/A"),
                            "service name": s_key,
                            "service_id": s_val2.get("service_id"),
                            "has_subservices": True
                        }

                        # Check if the service has subservices
                        if "service_infos" in s_val2 and "objects" in s_val2["service_infos"]:
                            objects = s_val2["service_infos"]["objects"]
                            print(f"Objects found: {objects}")  # Debugging log
                            if isinstance(objects, dict):  # Check if it's a dictionary
                                result["subservices"] = [{"name": obj["fields"]["name"], "key": obj["key"]} for obj in objects.values()]
                            elif isinstance(objects, list):  # If it's a list, handle accordingly
                                print(f"List of objects: {objects}")
                                for obj in objects:
                                    result["subservices"] = [{"name": obj.get("fields", {}).get("name", "N/A"), "key": obj.get("key", "N/A")} for obj in objects]

                            else:
                                result["has_subservices"] = False
                        else:
                            result["has_subservices"] = False
                        final_results.append(result)

        # If no results were found in the above, we will search directly in the subservices (objects)
        if not final_results:
            # Loop through the services again to search for the subservice name directly
            for sf_key, sf_val in data.items():
                # Check if the service family has subservices
                if "service_family_infos" in sf_val:
                    for s_key, s_val2 in sf_val["service_family_infos"].items():
                        if "service_infos" in s_val2 and "objects" in s_val2["service_infos"]:
                            objects = s_val2["service_infos"]["objects"]
                            for obj_key, obj_val in objects.items():
                                subservice_name = obj_val['fields']['name']
                                if word.lower() in subservice_name.lower():
                                    result = {
                                        "service family name": sf_key,
                                        "service_family_id": sf_val.get("service_family_id", "N/A"),
                                        "service name": s_key,
                                        "service_id": s_val2.get("service_id"),
                                        "subservice name": subservice_name,
                                        "servicesubcategory_id": obj_val.get("key"),
                                        "has_subservices": True,
                                        "fields_information": obj_val['fields']
                                    }
                                    final_results.append(result)

        global_tool_data["json_search_tool"] = final_results
        return final_results

    except Exception as e:
        print(f"json_search tool ERROR: {e}")
        return []

# A function that simulates chatbot handling the user query

def handle_user_query(query: str) -> str:
    results = json_search(query)
    
    if results:
        response = "Here are the matching results:\n"
        for result in results:
            service_family_name = result.get("service family name", "N/A")
            service_family_id = result.get("service_family_id", "N/A")
            service_name = result.get("service name", "N/A")
            service_id = result.get("service_id", "N/A")
            subservice_info = result.get('subservices', [])
            
            response += (
                f"\nService Family: {service_family_name} (ID: {service_family_id})\n"
                f"Service Name: {service_name} (ID: {service_id})\n"
            )
            
            if subservice_info:
                for subservice in subservice_info:
                    subservice_name = subservice.get('name', 'N/A')
                    subservice_key = subservice.get('key', 'N/A')
                    response += (
                        f"  Subservice Name: {subservice_name} (Key: {subservice_key})\n"
                    )
            else:
                response += "No subservices available.\n"
            
        return response
    else:
        return "Sorry, I couldn't find any relevant services for your query. Could you please provide more details?"

# Example tool definition
json_search_tool = Tool(
    name="JsonSearch",
    description="This tool helps fetch and get the important information about user's issue if the user mentions their issue in the query. It retrieves the service family name, service name, service_id, servicesubcategory_id, service_family_id, and fields information and also whether the search has subservices or not. Use this tool whenever the user mentions a specific issue.",
    func=json_search
)




def normalize_user_input(query: str) -> str:
    # Dictionary to normalize known variations
    normalization_map = {
    # IT Services
    "it services": "IT Services",
    "information technology services": "IT Services",
    "it support": "IT Services",
    "it assistance": "IT Services",
    "it help": "IT Services",
    "it department": "IT Services",
    "technical services": "IT Services",
    "computer support": "IT Services",
    "network support": "IT Services",
    "system support": "IT Services",
    

    # DevOps Services
    "devops services": "DevOps Services",
    "dev ops services": "DevOps Services",
    "devops": "DevOps Services",
    "devops support": "DevOps Services",
    "ci cd": "DevOps Services",
    "continuous integration": "DevOps Services",
    "continuous deployment": "DevOps Services",
    "automation services": "DevOps Services",
    "ci services": "DevOps Services",
    "deployment services": "DevOps Services",
    "devops": "DevOps Services",

    # Infra Services
    "infra services": "Infra Services",
    "infrastructure services": "Infra Services",
    "it infrastructure": "Infra Services",
    "infrastructure support": "Infra Services",
    "server management": "Infra Services",
    "network infrastructure": "Infra Services",
    "cloud infrastructure": "Infra Services",
    "data center services": "Infra Services",
    "infrastructure management": "Infra Services",
    "system infrastructure": "Infra Services",
    "infra": "Infra Services",

    # HR Service Family
    "hr service family": "HR Service Family",
    "human resources services": "HR Service Family",
    "hr services": "HR Service Family",
    "hr support": "HR Service Family",
    "employee services": "HR Service Family",
    "payroll services": "HR Service Family",
    "benefits services": "HR Service Family",
    "hr department": "HR Service Family",
    "employee support": "HR Service Family",
    "hr assistance": "HR Service Family",
    

    # Computers and Peripherals
    "computers and peripherals": "Computers and Peripherals",
    "pc and peripherals": "Computers and Peripherals",
    "computers": "Computers and Peripherals",
    "desktop computers": "Computers and Peripherals",
    "laptop and peripherals": "Computers and Peripherals",
    "laptop": "Computers and Peripherals",
    "desktop": "Computers and Peripherals",
    "computer hardware": "Computers and Peripherals",
    "peripherals": "Computers and Peripherals",
    "printer and peripherals": "Computers and Peripherals",

    # Software
    "software": "Software",
    "software services": "Software",
    "software installation": "Software",
    "software support": "Software",
    "software troubleshooting": "Software",
    "application services": "Software",
    "programming services": "Software",
    "software upgrades": "Software",
    "software maintenance": "Software",
    "enterprise software": "Software",

    # Telecom and Connectivity
    "telecom and connectivity": "Telecom and Connectivity",
    "telecommunications services": "Telecom and Connectivity",
    "networking services": "Telecom and Connectivity",
    "telecom services": "Telecom and Connectivity",
    "internet services": "Telecom and Connectivity",
    "network connectivity": "Telecom and Connectivity",
    "mobile services": "Telecom and Connectivity",
    "network support": "Telecom and Connectivity",
    "wireless services": "Telecom and Connectivity",
    "internet connectivity": "Telecom and Connectivity",

    # Project Related
    "project related": "Project Related",
    "project management": "Project Related",
    "project services": "Project Related",
    "project support": "Project Related",
    "project planning": "Project Related",
    "project development": "Project Related",
    "project execution": "Project Related",
    "project consulting": "Project Related",
    "project coordination": "Project Related",
    "project design": "Project Related",

    # Organization
    "organization": "Organization",
    "organization services": "Organization",
    "company services": "Organization",
    "corporate services": "Organization",
    "company support": "Organization",
    "company management": "Organization",
    "organization management": "Organization",
    "corporate management": "Organization",
    "business services": "Organization",
    "business management": "Organization",

    # Repository
    "repository": "Repository",
    "version control": "Repository",
    "source code repository": "Repository",
    "code repository": "Repository",
    "git repository": "Repository",
    "git services": "Repository",
    "repository services": "Repository",
    "repository management": "Repository",
    "repository support": "Repository",
    "repository hosting": "Repository",

    # VM1
    "vm1": "VM1",
    "virtual machine 1": "VM1",
    "vm1 services": "VM1",
    "virtualization 1": "VM1",
    "vm one": "VM1",
    "vm one services": "VM1",
    "virtual server 1": "VM1",
    "vm services": "VM1",
    "vm hosting 1": "VM1",
    "virtual machine services": "VM1",

    # VM Provisioning
    "vm provisioning": "VM Provisioning",
    "virtual machine provisioning": "VM Provisioning",
    "vm creation": "VM Provisioning",
    "virtual machine creation": "VM Provisioning",
    "vm setup": "VM Provisioning",
    "vm configuration": "VM Provisioning",
    "virtual machine configuration": "VM Provisioning",
    "vm deployment": "VM Provisioning",
    "virtual server provisioning": "VM Provisioning",
    "vm setup services": "VM Provisioning",

    # VM
    "vm": "VM",
    "virtual machine": "VM",
    "vm services": "VM",
    "virtual machine services": "VM",
    "vm support": "VM",
    "vm hosting": "VM",
    "vm maintenance": "VM",
    "virtual machine hosting": "VM",
    "virtual machine maintenance": "VM",
    "vm troubleshooting": "VM",

    # Storage Allocation
    "storage allocation": "Storage Allocation",
    "data storage": "Storage Allocation",
    "disk space allocation": "Storage Allocation",
    "cloud storage": "Storage Allocation",
    "storage management": "Storage Allocation",
    "storage support": "Storage Allocation",
    "file storage": "Storage Allocation",
    "storage provisioning": "Storage Allocation",
    "data storage services": "Storage Allocation",
    "disk allocation": "Storage Allocation",

    # Server Provisioning
    "server provisioning": "Server Provisioning",
    "server setup": "Server Provisioning",
    "server configuration": "Server Provisioning",
    "server deployment": "Server Provisioning",
    "server installation": "Server Provisioning",
    "server management": "Server Provisioning",
    "server services": "Server Provisioning",
    "server support": "Server Provisioning",
    "server hosting": "Server Provisioning",
    "server setup services": "Server Provisioning",

    # Security Access
    "security access": "Security Access",
    "access control": "Security Access",
    "user access": "Security Access",
    "authentication services": "Security Access",
    "authorization services": "Security Access",
    "login access": "Security Access",
    "security services": "Security Access",
    "user authentication": "Security Access",
    "security management": "Security Access",
    "account access": "Security Access",

    # PC
    "pc": "PC",
    "personal computer": "PC",
    "desktop pc": "PC",
    "laptop pc": "PC",
    "computer pc": "PC",
    "workstation pc": "PC",
    "pc support": "PC",
    "pc services": "PC",
    "pc troubleshooting": "PC",
    "pc management": "PC",

    # Network Configuration
    "network configuration": "Network Configuration",
    "network setup": "Network Configuration",
    "network services": "Network Configuration",
    "network management": "Network Configuration",
    "network troubleshooting": "Network Configuration",
    "network installation": "Network Configuration",
    "network administration": "Network Configuration",
    "network support": "Network Configuration",
    "network maintenance": "Network Configuration",
    "network monitoring": "Network Configuration",

    # Monitoring and Alerts
    "monitoring and alerts": "Monitoring and Alerts",
    "network monitoring": "Monitoring and Alerts",
    "system monitoring": "Monitoring and Alerts",
    "alert services": "Monitoring and Alerts",
    "alerting services": "Monitoring and Alerts",
    "service monitoring": "Monitoring and Alerts",
    "performance monitoring": "Monitoring and Alerts",
    "uptime monitoring": "Monitoring and Alerts",
    "alert system": "Monitoring and Alerts",
    "alert configuration": "Monitoring and Alerts",

    # Infrastructure Upgrades
    "infrastructure upgrades": "Infrastructure Upgrades",
    "it upgrades": "Infrastructure Upgrades",
    "server upgrades": "Infrastructure Upgrades",
    "network upgrades": "Infrastructure Upgrades",
    "system upgrades": "Infrastructure Upgrades",
    "software upgrades": "Infrastructure Upgrades",
    "hardware upgrades": "Infrastructure Upgrades",
    "cloud upgrades": "Infrastructure Upgrades",
    "data center upgrades": "Infrastructure Upgrades",
    "virtualization upgrades": "Infrastructure Upgrades",

    # Hardware/Software
    "hardware/software": "Hardware/Software",
    "hardware and software": "Hardware/Software",
    "hardware services": "Hardware/Software",
    "software services": "Hardware/Software",
    "hardware support": "Hardware/Software",
    "software support": "Hardware/Software",
    "hardware maintenance": "Hardware/Software",
    "software maintenance": "Hardware/Software",
    "hardware and software support": "Hardware/Software",
    "hardware/software troubleshooting": "Hardware/Software",

    # Docker
    "docker": "Docker",
    "docker services": "Docker",
    "containerization": "Docker",
    "docker containers": "Docker",
    "docker deployment": "Docker",
    "docker configuration": "Docker",
    "docker setup": "Docker",
    "docker management": "Docker",
    "docker support": "Docker",
    "docker troubleshooting": "Docker",
}

    # Normalize the query based on the dictionary
    normalized_query = query.lower()  # Convert to lowercase for case-insensitivity
    for key, value in normalization_map.items():
        normalized_query = normalized_query.replace(key, value)

    return normalized_query

def remove_articles(service_list: List[str]) -> List[str]:
    """
    Function to remove articles like 'a', 'an', 'the' from anywhere in service names.
    """
    cleaned_list = []
    articles = ['a', 'an', 'the']
    
    for service in service_list:
        service_words = service.split()
        # Remove articles from anywhere in the service name
        cleaned_service = [word for word in service_words if word.lower() not in articles]
        cleaned_list.append(' '.join(cleaned_service))
    
    return cleaned_list



@tool
def find_required_service_tool(user_query: str) -> List[str]:
    """
    A tool to process user queries and find matching services.
    This tool takes a user query and returns a list of available services or sub-services
    based on matching the service family name, service name, and sub-service name.
    """
    
    stop_words = set([
        'their', 'down', 'didn', 'so', 'most', 'will', 'theirs', 'been', 'can', 'these', 'over', 'myself',
        'weren', 'any', 'now', 'am', 'why', 'more', "shan't", 'do', 'o', 'haven', 'are', 'does', 'y',
        'where', 'hasn', "wouldn't", 'doesn', 'or', 'further', 'yourself', 'mightn', 'then', 'while',
        'our', "aren't", 've', 'isn', 'how', 'itself', 'his', 'ma', 'nor', 'very', 'himself', 'him', 'here',
        'until', 'into', 'an', 'doing', 'there', 'we', "mightn't", 'you', "didn't", 'than', 'shan',
        "you'll", 'they', 'needn', 'my', 'about', 'this', 'not', 'don', 'who', 'should', 'couldn', "that'll",
        'off', 'is', 'them', 'being', "shouldn't", 'both', 'before', 'wasn', 'and', 'themselves', 'when',
        'm', 'ain', 'ourselves', 'aren', 'on', 'shouldn', 're', 'won', 'were', 'having', 'facing', 'same',
        'herself', "it's", 'hadn', "weren't", "you'd", 'own', 'between', 'through', 'yourselves', 'up', 'no',
        'the', 'ours', 'a', 'again', "needn't", 'll', 'whom', "doesn't", 'had', 'too', 't', 'she', 'which',
        'but', 'be', 'those', "wasn't", 'out', 'some', 'have', 'd', 'has', 'against', 'by', 'yours', 'just',
        'during', 'other', 'for', 'its', 'after', 'of', 'from', "hasn't", 'few', 'above', 'did', 'in', 'all',
        'was', 'below', "you've", 'as', "won't", "she's", 'with', 'he', 'mustn', 's', 'that', "don't", 'once',
        "mustn't", 'wouldn', "you're", "should've", 'such', 'each', 'hers', 'under', "haven't", 'because', 
        'your', 'if', 'to', 'only', "isn't", 'me', 'at', "hadn't", 'what', "couldn't", 'her', 'servicesh', 
        'wit', 'issues', 'need', 'want', 'desire', 'wish', 'require', 'urge', 'demand', 'i', 'laptop', 'vms', 'vm', 'device', 'laptops'
    ])
    
    stop_words.update(["issue", "installation"])

    def save_service_list():
        try:
            with open('services_data_new.json', 'r') as json_file:
                data = json.load(json_file)
            
            service_families = {}

            for sf_key, sf_val in data.items():
                service_families[sf_key] = {
                    'services': [],
                    'sub_services': []
                }
                for s_key, s_val in sf_val['service_family_infos'].items():
                    service_families[sf_key]['services'].append(s_key)
                    if isinstance(s_val['service_infos'], dict):
                        for sub_key, sub_val in s_val['service_infos'].items():
                            if sub_key == "objects":
                                for obj_key, obj_val in sub_val.items():
                                    sub_service_name = obj_val['fields']['name'].lower()
                                    service_families[sf_key]['sub_services'].append(sub_service_name)
            return service_families
        except Exception as e:
            print(f"Error: {e}")
            return {}

    user_query = user_query.lower()
    query_words = user_query.split()
    filtered_query = [word for word in query_words if word not in stop_words]

    print("Filtered Query:", filtered_query)

    service_families = save_service_list()
    # print("Extracted Service Families:", json.dumps(service_families, indent=2))

    matching_service_families = [family_name for family_name in service_families if any(
        query_word in family_name.lower() for query_word in filtered_query)]
    
    if matching_service_families:
        # print("Matched Service Families:", matching_service_families)
        return matching_service_families

    matching_services = []
    for family_name, family_data in service_families.items():
        for service_name in family_data['services']:
            if all(query_word in service_name.lower() for query_word in filtered_query):
                matching_services.append(service_name)
    
    if matching_services:
        # print("Matched Services:", matching_services)
        return matching_services

    matching_sub_services = []
    for family_name, family_data in service_families.items():
        for sub_service_name in family_data['sub_services']:
            if " ".join(filtered_query) in sub_service_name:
                matching_sub_services.append(sub_service_name)

    if matching_sub_services:
        # print("Matched Sub-Services:", matching_sub_services)
        return matching_sub_services

    return []



@tool
def all_subservice_tool(service_family_name :str )->List:
    """ tool that provided all available sub services name for the given service_family_name"""
    try:
        
        with open('services_data_new.json', 'r') as json_file:
            data = json.load(json_file)
        if data :
            print("data is available " , service_family_name)
        sub_services_list = []
 
        for sf_key , sf_val in data.items():
            # print("sf key :",sf_key)
            if sf_key.lower() == service_family_name.lower():
                for s_key , s_val in sf_val['service_family_infos'].items():
                    # print("s key :",s_key)
                    if type(s_val['service_infos']) == dict:
                        for sub_key , sub_val in s_val['service_infos'].items():
 
                            if sub_key == "objects":
                                for obj_key , obj_val in sub_val.items():
 
                                    sub_service_name = obj_val['fields']['name']
                                    sub_services_list.append(sub_service_name)
                    else:
                        print("this is not dict")
        return sub_services_list
    except:
        return "save_service_list function is not working "

# ------------------------------------------------------------------------------------------------------------------------------#


 
# @tool
# def get_device_list_by_email(email: str, system:str) -> dict:
#     """This tool retrieves a list of devices associated with the provided email, categorizing them into laptops and VMs."""
#     print("device==================>",system)
#     print("email+++++++++++++++++++>",email)
#     if not email:
#         return {"error": "Please provide a valid email."}
 
#     url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
#     # Prepare the payload
#     json_data = {
#         "operation": "core/get",
#         "class": "Person",
#         "key": f"SELECT Person WHERE email='{email}'",
#         "output_fields": "cis_list"
#     }
    
#     json_string = json.dumps(json_data)
    
#     # Prepare headers for Basic Auth
#     auth = (USERNAME, PASSWORD)
    
#     # Make the GET request
#     response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
#     # Handle the response
#     if response.status_code == 200:
#         data = response.json()
        
#         ci_data = data.get("objects", [])
        
#         # Optionally save the response to a file
#         with open("ci_data.json", 'w') as file:
#             file.write(json.dumps(ci_data, indent=4))
 
#         if ci_data:
#             laptops = []
#             vms = []
#             other =[]
        
            
#             for incident_key, incident in ci_data.items():
#                 cis_list = incident.get('fields', {}).get('cis_list', [])
                
#                 if cis_list and isinstance(cis_list, list):
#                     for device in cis_list:
#                         functionalci_type = device.get("functionalci_id_finalclass_recall", "No functionalci_name found")
#                         functionalci_name = device.get("functionalci_name", "No functionalci_name found")
#                         functionalci_id = device.get("functionalci_id", "No functionalci_id found")
                        
#                         if functionalci_type.lower() == "pc":
#                             laptops.append({
#                                 "functionalci_id": functionalci_id,
#                                 "functionalci_name": functionalci_name
#                             })           
#                         elif functionalci_type.lower() == "virtualmachine":
#                             vms.append({
#                                 "functionalci_id": functionalci_id,
#                                 "functionalci_name": functionalci_name
#                             })
#                         else:
#                             other.append({
#                                 "functionalci_id": functionalci_id,
#                                 "functionalci_name": functionalci_name
#                             })
                    
#             # Return the categorized devices
#             response = {}
#             response['laptops'] = laptops
#             response['vms'] = vms
#             response['both'] = laptops + vms
#             if len(other)!= 0 :
#                 response['other'] = other
#             # return {
#             #     "laptops": laptops,
#             #     "vms": vms
#             # }
            # if system.lower()=="laptop":
            #     if len(response['laptops'])==1:
            #         return response['laptops'][0]
            #     else:
            #         return response['laptops']
            # elif system.lower()=="vm":
            #     if len(response['vms'])==1:
            #         return response['laptops'][0]
            #     else:
            #         return response['laptops']
#             elif system.lower() =="laptop and vm":
#                 return response['both']
#             else:
#                 return "No data found for the given email."
#         else:
#             return {"No data found for the given email."}
    
#     else:
#         return {"error": "Sorry, there was an issue fetching the incident details."}
 
 


@tool
def get_functionalci_id_by_functionalci_name(email: str, selected_device_name: str, system: str) -> str:
    """this tool takes the user's selected device name and returns the ID related to the given device name"""
    # global id_var
    # id_var=selected_device_name
    global id_var
    id_var=selected_device_name
    try:
        global global_tool_data
        devices_info = get_device_list_by_email.invoke({"email": email, "system": system})
        
        if not devices_info:
            raise ValueError("Device information is None")
        
        if not isinstance(devices_info, list):  # Check if it's a list instead of dict
            raise ValueError("Devices information is not in list format")
        
        # Now process the list of devices
        for device in devices_info:  # Directly iterate over the list
            if device.get('functionalci_name') == selected_device_name:
                response = {}
                response["functionalci_name"] = device.get('functionalci_name')
                response["functionalci_id"] = device.get('functionalci_id', "ID not found")
                global_tool_data["get_functionalci_id_by_functionalci_name"] = response
                return response
        
        raise ValueError("Device name not found")
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"




@tool()
def map_ci_devices_to_subservice(email:str, user_query :str , subservice: str) -> list:
    """This tool maps CI devices based on the selected subservice type and user's describe query (Laptop, Desktop, VM).for that agent have to give the user's query what agent understand in the conversation"""
 
    query_word = user_query.lower().split()
    print("subservice=======>",subservice)
 
    laptop_similar_words = ["laptop", "pc", "desktop", "computer", "workstation"]
    vm_similar_words = ["vm", "virtual", "virtualmachine", "virtual-machine"]
    
 
    if any(word in query_word for word in laptop_similar_words):
        print("if condtion of laptop --------------->")
        return "laptop"
    
 
    elif any(word in query_word for word in vm_similar_words):
        print("if condtion of vm --------------->")
        return "vm"
    
    # If no match is found
    else:
        print("check in else condition ------>")
        # Define subservice categories
        laptop_related_subservices = ["Modify PC", "PC" ]
        laptop_and_vm_related_subservices = [
            "Repair",
            "Troubleshooting",
            "Software Installation / Upgrade",
            "Software removal",
            "Troubleshooting - Software",
            "VPN Installation",
            "Windows installation / upgrade",                    
            "Adobe Installation",
            "Create Docker with Pipeline",
            "maintain docker" ,
            "Network Troubleshooting",
            "New peripheral"
 
        ]
        
        vm_related_subservices = [
            "Delete VM" , "Modify VM" , "New Database Setup with VM" , "New DNS name","New IP address"
        ]
 
        if subservice in laptop_related_subservices:
            # get_device_list_by_email.invoke(email,"laptop")
            return "laptop"
        
        if subservice in vm_related_subservices:
            # get_device_list_by_email.invoke(email,"vm")
            return "vm"
 
        if subservice in laptop_and_vm_related_subservices:
            return "laptop and vm"
            
        
        if subservice not in laptop_and_vm_related_subservices or vm_related_subservices:
            # get_device_list_by_email.invoke(email,"no ci needed")
            return "no ci needed"





#***************************************** UPDATE TOOLS START FROM HERE *****************************************
    

@tool
def get_complete_incident_details(ticket_id: str) -> str:
    """This tool retrieves cpmplete the details of an incident based on the provided ticket ID and should only be called while updating the ticket."""
    
    if not ticket_id:
        return "Please provide a valid Ticket ID."
    
    # API URL
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE ref='{ticket_id}'",
        "output_fields": "*"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()
        
        # Assuming the response is a JSON with the incident details
        incident_data = data.get("objects", {})
        
        if incident_data:
            # Iterate through the incidents
            for incident_key, incident in incident_data.items():
                status = incident.get('fields', {}).get('status', 'Unknown')
                title = incident.get('fields', {}).get('title', 'Unknown')
                description = incident.get('fields', {}).get('description', 'Unknown')
                clean_description = description.replace("<p>", "").replace("</p>", "")
                origin = incident.get('fields', {}).get('origin', 'Unknown')
                service_name = incident.get('fields', {}).get('service_name', 'Unknown')
                servicesubcategory_name = incident.get('fields', {}).get('servicesubcategory_name', 'Unknown')
                team_id_friendlyname = incident.get('fields', {}).get('team_id_friendlyname', 'Unknown')
                agent_id_friendlyname = incident.get('fields', {}).get('agent_id_friendlyname', 'Unknown')
                team_id = incident.get('fields', {}).get('team_id', 'Unknown')
                agent_id = incident.get('fields', {}).get('agent_id', 'Unknown')
                start_date = incident.get('fields', {}).get('start_date', 'Unknown')
                key = incident.get('key', 'Unknown')  # Correct access for the 'key'

            if origin == 'teamsbot':
                origin = "TEAMS BOT"

            incident_details = {
                "Status": status,
                "Title": title,
                "Description": clean_description,
                "Origin": origin,
                "Service Name": service_name,
                "Service Sub Category": servicesubcategory_name,
                "Team ID Friendly Name": team_id_friendlyname,
                "Agent ID Friendly Name": agent_id_friendlyname,
                "Team ID": team_id,
                "Agent ID": agent_id,
                "Start Date": start_date,
                "key": key
            }

            # # Construct the message
            # message = f"""Status: {status}
            # Title: {title}
            # Key: {key}
            # Description: {clean_description}
            # Origin: {origin}
            # Service Name: {service_name}
            # Service Sub Category: {servicesubcategory_name}
            # Team ID Friendly Name: {team_id_friendlyname}
            # Agent ID Friendly Name: {agent_id_friendlyname}
            # Team ID: {team_id}
            # Agent ID: {agent_id}
            # Start Date: {start_date}"""

            # Format the message properly using regular expressions
            # formatted_message = re.sub(r"(.*?: .+?)(?=\s*?Status|Title|Description|Origin|Service|Team ID|Agent ID|Start Date|$)", r"\1\n", message)
            
            return incident_details

        else:
            return "No details found for this incident."
    
    else:
        return "Sorry, there was an issue fetching the incident details."
    

@tool
def get_complete_UserRequest_details(ticket_id: str) -> str:
    """This tool retrieves cpmplete the details of an incident based on the provided ticket ID and should only be called while updating the ticket."""
    
    if not ticket_id:
        return "Please provide a valid Ticket ID."
    
    # API URL
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE ref='{ticket_id}'",
        "output_fields": "*"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()
        
        # Assuming the response is a JSON with the incident details
        incident_data = data.get("objects", {})
        
        if incident_data:
            # Iterate through the incidents
            for incident_key, incident in incident_data.items():
                status = incident.get('fields', {}).get('status', 'Unknown')
                title = incident.get('fields', {}).get('title', 'Unknown')
                description = incident.get('fields', {}).get('description', 'Unknown')
                clean_description = description.replace("<p>", "").replace("</p>", "")
                origin = incident.get('fields', {}).get('origin', 'Unknown')
                service_name = incident.get('fields', {}).get('service_name', 'Unknown')
                servicesubcategory_name = incident.get('fields', {}).get('servicesubcategory_name', 'Unknown')
                team_id_friendlyname = incident.get('fields', {}).get('team_id_friendlyname', 'Unknown')
                agent_id_friendlyname = incident.get('fields', {}).get('agent_id_friendlyname', 'Unknown')
                team_id = incident.get('fields', {}).get('team_id', 'Unknown')
                agent_id = incident.get('fields', {}).get('agent_id', 'Unknown')
                start_date = incident.get('fields', {}).get('start_date', 'Unknown')
                key = incident.get('key', 'Unknown')  # Correct access for the 'key'

            if origin == 'teamsbot':
                origin = "TEAMS BOT"

            incident_details = {
                "Status": status,
                "Title": title,
                "Description": clean_description,
                "Origin": origin,
                "Service Name": service_name,
                "Service Sub Category": servicesubcategory_name,
                "Team ID Friendly Name": team_id_friendlyname,
                "Agent ID Friendly Name": agent_id_friendlyname,
                "Team ID": team_id,
                "Agent ID": agent_id,
                "Start Date": start_date,
                "key": key
            }

            # # Construct the message
            # message = f"""Status: {status}
            # Title: {title}
            # Key: {key}
            # Description: {clean_description}
            # Origin: {origin}
            # Service Name: {service_name}
            # Service Sub Category: {servicesubcategory_name}
            # Team ID Friendly Name: {team_id_friendlyname}
            # Agent ID Friendly Name: {agent_id_friendlyname}
            # Team ID: {team_id}
            # Agent ID: {agent_id}
            # Start Date: {start_date}"""

            # Format the message properly using regular expressions
            # formatted_message = re.sub(r"(.*?: .+?)(?=\s*?Status|Title|Description|Origin|Service|Team ID|Agent ID|Start Date|$)", r"\1\n", message)
            
            return incident_details

        else:
            return "No details found for this incident."
    
    else:
        return "Sorry, there was an issue fetching the incident details."
    

@tool
def I_status_update_dispatched_to_assigned(ticket_id: str) -> dict:
    """This tool updates the status of dispatched tickets to assigned"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Get the incident details for the given ticket_id
        ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)

        # Check if ticket_info is a dictionary and contains expected data
        if not isinstance(ticket_info, dict):
            return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
        
        # Directly extract the ticket details since your structure doesn't have 'objects'
        team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
        agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
        key = ticket_info.get("key")  # Assuming key is at the top level as well
        title=ticket_info.get("Title")
        id=ticket_id
        
        # Ensure team_id and agent_id are found in ticket_info
        if not team_id or not agent_id:
            return {"status": "error", "message": "team_id or agent_id not found in incident details"}
        
        # Prepare the JSON data for the request to update the incident status
        json_data = {
            "operation": "core/apply_stimulus",
            "comment": "Synchronization from blah...",
            "class": "Incident",
            "key": key,
            "stimulus": "ev_assign",
            "output_fields": "friendlyname, title, status",
            "fields": { 
                "team_id": team_id,
                "agent_id": agent_id
            }
        }

        # Convert dictionary to JSON string
        json_string = json.dumps(json_data)
        
        # Make the GET request to apply the stimulus
        response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=(USERNAME, PASSWORD))
        
        # Handle the response for the GET request
        if response.status_code == 200:
            data = response.json()

            # Extract incident details from the response
            incident_key = f"Incident::{key}"  # Construct the incident key using the key
            incident_info = data.get("objects", {}).get(incident_key, {})
            
            # If incident data is present, format it accordingly
            if incident_info:
                incident_data = {

                                "friendlyname": incident_info.get("friendlyname", id),
                                "title": incident_info.get("title", title),
                                "status": incident_info.get("status", "assigned")
                            }

                return incident_data

            # If no incident data is found, return an error
            return {"status1": "error", "message": "Incident not found or failed to update."}

        else:
            # If the response status code is not 200, return an error
            return {"status2": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        # If any exception occurs, return an error
        return {"status3": "error", "message": str(e)}




@tool
def R_status_update_dispatched_to_assigned(ticket_id: str) -> dict:
    """This tool updates the status of dispatched tickets to assigned"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Get the incident details for the given ticket_id
        ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)

        # Check if ticket_info is a dictionary and contains expected data
        if not isinstance(ticket_info, dict):
            return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
        
        # Directly extract the ticket details since your structure doesn't have 'objects'
        team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
        agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
        key = ticket_info.get("key")  # Assuming key is at the top level as well
        title=ticket_info.get("Title")
        id=ticket_id
        
        # Ensure team_id and agent_id are found in ticket_info
        if not team_id or not agent_id:
            return {"status": "error", "message": "team_id or agent_id not found in incident details"}
        
        # Prepare the JSON data for the request to update the incident status
        json_data = {
            "operation": "core/apply_stimulus",
            "comment": "Synchronization from blah...",
            "class": "UserRequest",
            "key": key,
            "stimulus": "ev_assign",
            "output_fields": "friendlyname, title, status",
            "fields": { 
                "team_id": team_id,
                "agent_id": agent_id
            }
        }

        # Convert dictionary to JSON string
        json_string = json.dumps(json_data)
        
        # Make the GET request to apply the stimulus
        response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=(USERNAME, PASSWORD))
        
        # Handle the response for the GET request
        if response.status_code == 200:
            data = response.json()

            # Extract incident details from the response
            incident_key = f"Incident::{key}"  # Construct the incident key using the key
            incident_info = data.get("objects", {}).get(incident_key, {})
            
            # If incident data is present, format it accordingly
            if incident_info:
                incident_data = {

                                "friendlyname": incident_info.get("friendlyname", id),
                                "title": incident_info.get("title", title),
                                "status": incident_info.get("status", "assigned")
                            }

                return incident_data

            # If no incident data is found, return an error
            return {"status1": "error", "message": "Incident not found or failed to update."}

        else:
            # If the response status code is not 200, return an error
            return {"status2": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        # If any exception occurs, return an error
        return {"status3": "error", "message": str(e)}
    


@tool
def I_status_update_pending_to_assigned(ticket_id: str) -> dict:
    """This tool updates the status of dispatched tickets to assigned"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Get the incident details for the given ticket_id
        ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)

        # Check if ticket_info is a dictionary and contains expected data
        if not isinstance(ticket_info, dict):
            return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
        
        # Directly extract the ticket details since your structure doesn't have 'objects'
        team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
        agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
        key = ticket_info.get("key")  # Assuming key is at the top level as well
        title=ticket_info.get("Title")
        id=ticket_id
        
        # Ensure team_id and agent_id are found in ticket_info
        if not team_id or not agent_id:
            return {"status": "error", "message": "team_id or agent_id not found in incident details"}
        
        # Prepare the JSON data for the request to update the incident status
        json_data = {
            "operation": "core/apply_stimulus",
            "comment": "Synchronization from blah...",
            "class": "Incident",
            "key": key,
            "stimulus": "ev_assign",
            "output_fields": "friendlyname, title, status",
            "fields": { 
                "team_id": team_id,
                "agent_id": agent_id
            }
        }

        # Convert dictionary to JSON string
        json_string = json.dumps(json_data)
        
        # Make the GET request to apply the stimulus
        response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=(USERNAME, PASSWORD))
        
        # Handle the response for the GET request
        if response.status_code == 200:
            data = response.json()

            # Extract incident details from the response
            incident_key = f"Incident::{key}"  # Construct the incident key using the key
            incident_info = data.get("objects", {}).get(incident_key, {})
            
            # If incident data is present, format it accordingly
            if incident_info:
                incident_data = {

                                "friendlyname": incident_info.get("friendlyname", id),
                                "title": incident_info.get("title", title),
                                "status": incident_info.get("status", "assigned")
                            }

                return incident_data

            # If no incident data is found, return an error
            return {"status1": "error", "message": "Incident not found or failed to update."}

        else:
            # If the response status code is not 200, return an error
            return {"status2": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        # If any exception occurs, return an error
        return {"status3": "error", "message": str(e)}
    

@tool
def R_status_update_pending_to_assigned(ticket_id: str) -> dict:
    """This tool updates the status of dispatched tickets to assigned"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Get the incident details for the given ticket_id
        ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)

        # Check if ticket_info is a dictionary and contains expected data
        if not isinstance(ticket_info, dict):
            return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
        
        # Directly extract the ticket details since your structure doesn't have 'objects'
        team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
        agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
        key = ticket_info.get("key")  # Assuming key is at the top level as well
        title=ticket_info.get("Title")
        id=ticket_id
        
        # Ensure team_id and agent_id are found in ticket_info
        if not team_id or not agent_id:
            return {"status": "error", "message": "team_id or agent_id not found in incident details"}
        
        # Prepare the JSON data for the request to update the incident status
        json_data = {
            "operation": "core/apply_stimulus",
            "comment": "Synchronization from blah...",
            "class": "UserRequest",
            "key": key,
            "stimulus": "ev_assign",
            "output_fields": "friendlyname, title, status",
            "fields": { 
                "team_id": team_id,
                "agent_id": agent_id
            }
        }

        # Convert dictionary to JSON string
        json_string = json.dumps(json_data)
        
        # Make the GET request to apply the stimulus
        response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=(USERNAME, PASSWORD))
        
        # Handle the response for the GET request
        if response.status_code == 200:
            data = response.json()

            # Extract incident details from the response
            incident_key = f"Incident::{key}"  # Construct the incident key using the key
            incident_info = data.get("objects", {}).get(incident_key, {})
            
            # If incident data is present, format it accordingly
            if incident_info:
                incident_data = {

                                "friendlyname": incident_info.get("friendlyname", id),
                                "title": incident_info.get("title", title),
                                "status": incident_info.get("status", "assigned")
                            }

                return incident_data

            # If no incident data is found, return an error
            return {"status1": "error", "message": "Incident not found or failed to update."}

        else:
            # If the response status code is not 200, return an error
            return {"status2": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        # If any exception occurs, return an error
        return {"status3": "error", "message": str(e)}
    

@tool
def I_status_update_assigned_to_resolved(ticket_id: str) -> dict:
    """This tool updates the status of dispatched tickets to assigned"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Get the incident details for the given ticket_id
        ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)

        # Check if ticket_info is a dictionary and contains expected data
        if not isinstance(ticket_info, dict):
            return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
        
        # Directly extract the ticket details since your structure doesn't have 'objects'
        team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
        agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
        key = ticket_info.get("key")  # Assuming key is at the top level as well
        title=ticket_info.get("Title")
        id=ticket_id
        
        # Ensure team_id and agent_id are found in ticket_info
        if not team_id or not agent_id:
            return {"status": "error", "message": "team_id or agent_id not found in incident details"}
        
        # Prepare the JSON data for the request to update the incident status
        json_data = {
            "operation": "core/apply_stimulus",
            "comment": "Synchronization from blah...",
            "class": "Incident",
            "key": key,
            "stimulus": "ev_resolve",
            "output_fields": "friendlyname, title, status",
            "fields": { 
                "team_id": team_id,
                "agent_id": agent_id
            }
        }

        # Convert dictionary to JSON string
        json_string = json.dumps(json_data)
        
        # Make the GET request to apply the stimulus
        response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=(USERNAME, PASSWORD))
        
        # Handle the response for the GET request
        if response.status_code == 200:
            data = response.json()

            # Extract incident details from the response
            incident_key = f"Incident::{key}"  # Construct the incident key using the key
            incident_info = data.get("objects", {}).get(incident_key, {})
            
            # If incident data is present, format it accordingly
            if incident_info:
                incident_data = {

                                "friendlyname": incident_info.get("friendlyname", id),
                                "title": incident_info.get("title", title),
                                "status": incident_info.get("status", "resolved")
                            }

                return incident_data

            # If no incident data is found, return an error
            return {"status1": "error", "message": "Incident not found or failed to update."}

        else:
            # If the response status code is not 200, return an error
            return {"status2": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        # If any exception occurs, return an error
        return {"status3": "error", "message": str(e)}




@tool
def R_status_update_assigned_to_resolved(ticket_id: str) -> dict:
    """This tool updates the status of dispatched tickets to assigned"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Get the incident details for the given ticket_id
        ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)

        # Check if ticket_info is a dictionary and contains expected data
        if not isinstance(ticket_info, dict):
            return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
        
        # Directly extract the ticket details since your structure doesn't have 'objects'
        team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
        agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
        key = ticket_info.get("key")  # Assuming key is at the top level as well
        title=ticket_info.get("Title")
        id=ticket_id
        
        # Ensure team_id and agent_id are found in ticket_info
        if not team_id or not agent_id:
            return {"status": "error", "message": "team_id or agent_id not found in incident details"}
        
        # Prepare the JSON data for the request to update the incident status
        json_data = {
            "operation": "core/apply_stimulus",
            "comment": "Synchronization from blah...",
            "class": "UserRequest",
            "key": key,
            "stimulus": "ev_resolve",
            "output_fields": "friendlyname, title, status",
            "fields": { 
                "team_id": team_id,
                "agent_id": agent_id
            }
        }

        # Convert dictionary to JSON string
        json_string = json.dumps(json_data)
        
        # Make the GET request to apply the stimulus
        response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=(USERNAME, PASSWORD))
        
        # Handle the response for the GET request
        if response.status_code == 200:
            data = response.json()

            # Extract incident details from the response
            incident_key = f"Incident::{key}"  # Construct the incident key using the key
            incident_info = data.get("objects", {}).get(incident_key, {})
            
            # If incident data is present, format it accordingly
            if incident_info:
                incident_data = {

                                "friendlyname": incident_info.get("friendlyname", id),
                                "title": incident_info.get("title", title),
                                "status": incident_info.get("status", "resolved")
                            }

                return incident_data

            # If no incident data is found, return an error
            return {"status1": "error", "message": "Incident not found or failed to update."}

        else:
            # If the response status code is not 200, return an error
            return {"status2": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        # If any exception occurs, return an error
        return {"status3": "error", "message": str(e)}
    



@tool
def I_status_update_assigned_to_pending(ticket_id: str) -> dict:
    """This tool updates the status of dispatched tickets to assigned"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Get the incident details for the given ticket_id
        ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)

        # Check if ticket_info is a dictionary and contains expected data
        if not isinstance(ticket_info, dict):
            return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
        
        # Directly extract the ticket details since your structure doesn't have 'objects'
        team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
        agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
        key = ticket_info.get("key")  # Assuming key is at the top level as well
        title=ticket_info.get("Title")
        id=ticket_id
        
        # Ensure team_id and agent_id are found in ticket_info
        if not team_id or not agent_id:
            return {"status": "error", "message": "team_id or agent_id not found in incident details"}
        
        # Prepare the JSON data for the request to update the incident status
        json_data = {
            "operation": "core/apply_stimulus",
            "comment": "Synchronization from blah...",
            "class": "Incident",
            "key": key,
            "stimulus": "ev_pending",
            "output_fields": "friendlyname, title, status",
            "fields": { 
                "team_id": team_id,
                "agent_id": agent_id
            }
        }

        # Convert dictionary to JSON string
        json_string = json.dumps(json_data)
        
        # Make the GET request to apply the stimulus
        response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=(USERNAME, PASSWORD))
        
        # Handle the response for the GET request
        if response.status_code == 200:
            data = response.json()

            # Extract incident details from the response
            incident_key = f"Incident::{key}"  # Construct the incident key using the key
            incident_info = data.get("objects", {}).get(incident_key, {})
            
            # If incident data is present, format it accordingly
            if incident_info:
                incident_data = {

                                "friendlyname": incident_info.get("friendlyname", id),
                                "title": incident_info.get("title", title),
                                "status": incident_info.get("status", "pending")
                            }

                return incident_data

            # If no incident data is found, return an error
            return {"status1": "error", "message": "Incident not found or failed to update."}

        else:
            # If the response status code is not 200, return an error
            return {"status2": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        # If any exception occurs, return an error
        return {"status3": "error", "message": str(e)}
    



@tool
def R_status_update_assigned_to_pending(ticket_id: str) -> dict:
    """This tool updates the status of dispatched tickets to assigned"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Get the incident details for the given ticket_id
        ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)

        # Check if ticket_info is a dictionary and contains expected data
        if not isinstance(ticket_info, dict):
            return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
        
        # Directly extract the ticket details since your structure doesn't have 'objects'
        team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
        agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
        key = ticket_info.get("key")  # Assuming key is at the top level as well
        title=ticket_info.get("Title")
        id=ticket_id
        
        # Ensure team_id and agent_id are found in ticket_info
        if not team_id or not agent_id:
            return {"status": "error", "message": "team_id or agent_id not found in incident details"}
        
        # Prepare the JSON data for the request to update the incident status
        json_data = {
            "operation": "core/apply_stimulus",
            "comment": "Synchronization from blah...",
            "class": "UserRequest",
            "key": key,
            "stimulus": "ev_pending",
            "output_fields": "friendlyname, title, status",
            "fields": { 
                "team_id": team_id,
                "agent_id": agent_id
            }
        }

        # Convert dictionary to JSON string
        json_string = json.dumps(json_data)
        
        # Make the GET request to apply the stimulus
        response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=(USERNAME, PASSWORD))
        
        # Handle the response for the GET request
        if response.status_code == 200:
            data = response.json()

            # Extract incident details from the response
            incident_key = f"Incident::{key}"  # Construct the incident key using the key
            incident_info = data.get("objects", {}).get(incident_key, {})
            
            # If incident data is present, format it accordingly
            if incident_info:
                incident_data = {

                                "friendlyname": incident_info.get("friendlyname", id),
                                "title": incident_info.get("title", title),
                                "status": incident_info.get("status", "pending")
                            }

                return incident_data

            # If no incident data is found, return an error
            return {"status1": "error", "message": "Incident not found or failed to update."}

        else:
            # If the response status code is not 200, return an error
            return {"status2": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        # If any exception occurs, return an error
        return {"status3": "error", "message": str(e)}
    


@tool
def I_status_update_redispatch(ticket_id: str) -> dict:
    """This tool updates the status of dispatched tickets to assigned"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Get the incident details for the given ticket_id
        ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)

        # Check if ticket_info is a dictionary and contains expected data
        if not isinstance(ticket_info, dict):
            return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
        
        # Directly extract the ticket details since your structure doesn't have 'objects'
        team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
        agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
        key = ticket_info.get("key")  # Assuming key is at the top level as well
        title=ticket_info.get("Title")
        id=ticket_id
        
        # Ensure team_id and agent_id are found in ticket_info
        if not team_id or not agent_id:
            return {"status": "error", "message": "team_id or agent_id not found in incident details"}
        
        # Prepare the JSON data for the request to update the incident status
        json_data = {
            "operation": "core/apply_stimulus",
            "comment": "Synchronization from blah...",
            "class": "Incident",
            "key": key,
            "stimulus": "ev_dispatch",
            "output_fields": "friendlyname, title, status",
            "fields": { 
                "team_id": team_id,
                "agent_id": agent_id
            }
        }

        # Convert dictionary to JSON string
        json_string = json.dumps(json_data)
        
        # Make the GET request to apply the stimulus
        response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=(USERNAME, PASSWORD))
        
        # Handle the response for the GET request
        if response.status_code == 200:
            data = response.json()

            # Extract incident details from the response
            incident_key = f"Incident::{key}"  # Construct the incident key using the key
            incident_info = data.get("objects", {}).get(incident_key, {})
            
            # If incident data is present, format it accordingly
            if incident_info:
                incident_data = {

                                "friendlyname": incident_info.get("friendlyname", id),
                                "title": incident_info.get("title", title),
                                "status": incident_info.get("status", "pending")
                            }

                return incident_data

            # If no incident data is found, return an error
            return {"status1": "error", "message": "Incident not found or failed to update."}

        else:
            # If the response status code is not 200, return an error
            return {"status2": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        # If any exception occurs, return an error
        return {"status3": "error", "message": str(e)}
    


@tool
def R_status_update_redispatch(ticket_id: str) -> dict:
    """This tool updates the status of dispatched tickets to assigned"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    try:
        # Get the incident details for the given ticket_id
        ticket_info = get_complete_incident_details.invoke({"ticket_id": ticket_id})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ticket_info)

        # Check if ticket_info is a dictionary and contains expected data
        if not isinstance(ticket_info, dict):
            return {"status": "error", "message": f"Unexpected ticket_info format: {type(ticket_info)}. Expected a dictionary."}
        
        # Directly extract the ticket details since your structure doesn't have 'objects'
        team_id = ticket_info.get("Team ID")  # Correct key name based on the structure
        agent_id = ticket_info.get("Agent ID")  # Correct key name based on the structure
        key = ticket_info.get("key")  # Assuming key is at the top level as well
        title=ticket_info.get("Title")
        id=ticket_id
        
        # Ensure team_id and agent_id are found in ticket_info
        if not team_id or not agent_id:
            return {"status": "error", "message": "team_id or agent_id not found in incident details"}
        
        # Prepare the JSON data for the request to update the incident status
        json_data = {
            "operation": "core/apply_stimulus",
            "comment": "Synchronization from blah...",
            "class": "UserRequest",
            "key": key,
            "stimulus": "ev_dispatch",
            "output_fields": "friendlyname, title, status",
            "fields": { 
                "team_id": team_id,
                "agent_id": agent_id
            }
        }

        # Convert dictionary to JSON string
        json_string = json.dumps(json_data)
        
        # Make the GET request to apply the stimulus
        response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=(USERNAME, PASSWORD))
        
        # Handle the response for the GET request
        if response.status_code == 200:
            data = response.json()

            # Extract incident details from the response
            incident_key = f"Incident::{key}"  # Construct the incident key using the key
            incident_info = data.get("objects", {}).get(incident_key, {})
            
            # If incident data is present, format it accordingly
            if incident_info:
                incident_data = {

                                "friendlyname": incident_info.get("friendlyname", id),
                                "title": incident_info.get("title", title),
                                "status": incident_info.get("status", "pending")
                            }

                return incident_data

            # If no incident data is found, return an error
            return {"status1": "error", "message": "Incident not found or failed to update."}

        else:
            # If the response status code is not 200, return an error
            return {"status2": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        # If any exception occurs, return an error
        return {"status3": "error", "message": str(e)}
    


@tool
def I_dispatched_tickets_for_agent(email: str) -> dict:
    """This tool gets incident dispatched tickets as per agent_id"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    try:
        # Get the user profile based on the email
        user_info = identify_user_profile.invoke({"email": email})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", user_info)

        # Check if user_info is a dictionary and contains expected data
        if not isinstance(user_info, dict):
            return {"status": "error", "message": f"Unexpected user_info format: {type(user_info)}. Expected a dictionary."}

        profile_name = user_info.get("profile_name")
        
        # Ensure that profile_name is 'Agent' and extract agent_id
        if profile_name == 'Agent':  # Use equality comparison (==) instead of 'is'
            agent_id = user_info.get("contactid")
        else:
            return {"status": "error", "message": "User is not an Agent."}
        
        # Ensure agent_id is found
        if not agent_id:
            return {"status": "error", "message": "agent_id not found in user profile."}
        
        # Prepare the SQL query to get dispatched tickets for the agent
        query = f"""
            SELECT Incident AS I
            JOIN Team AS T ON I.team_id = T.id
            JOIN lnkPersonToTeam AS L ON L.team_id = T.id
            JOIN Person AS P ON L.person_id = P.id
            WHERE P.id = {agent_id} AND I.status='Dispatched'
        """
        
        json_data = {
            "operation": "core/get",
            "class": "Incident",
            "key": query,  # The query is passed as the key parameter
            "output_fields": "ref"  # Specify the fields you need in the response
        }

        # Make the request (assuming the server responds with JSON)
        response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

        # Handle the response
        if response.status_code == 200:
            data = response.json()

            # Check if there are dispatched tickets for the agent
            if data.get("objects"):
                return {"status": "success", "data": data["objects"]}
            else:
                return {"status": "error", "message": "No dispatched tickets found for the agent."}

        else:
            return {"status": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    


@tool
def R_dispatched_tickets_for_agent(email: str) -> dict:
    """This tool gets userrequest dispatched tickets as per agent_id"""
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    try:
        # Get the user profile based on the email
        user_info = identify_user_profile.invoke({"email": email})
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", user_info)

        # Check if user_info is a dictionary and contains expected data
        if not isinstance(user_info, dict):
            return {"status": "error", "message": f"Unexpected user_info format: {type(user_info)}. Expected a dictionary."}

        profile_name = user_info.get("profile_name")
        
        # Ensure that profile_name is 'Agent' and extract agent_id
        if profile_name == 'Agent':  # Use equality comparison (==) instead of 'is'
            agent_id = user_info.get("contactid")
        else:
            return {"status": "error", "message": "User is not an Agent."}
        
        # Ensure agent_id is found
        if not agent_id:
            return {"status": "error", "message": "agent_id not found in user profile."}
        
        # Prepare the SQL query to get dispatched tickets for the agent
        query = f"""
            SELECT UserRequest AS R
            JOIN Team AS T ON R.team_id = T.id
            JOIN lnkPersonToTeam AS L ON L.team_id = T.id
            JOIN Person AS P ON L.person_id = P.id
            WHERE P.id = {agent_id} AND R.status='Dispatched'
        """
        
        json_data = {
            "operation": "core/get",
            "class": "UserRequest",
            "key": query,  # The query is passed as the key parameter
            "output_fields": "ref"  # Specify the fields you need in the response
        }

        # Make the request (assuming the server responds with JSON)
        response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=(USERNAME, PASSWORD))

        # Handle the response
        if response.status_code == 200:
            data = response.json()

            # Check if there are dispatched tickets for the agent
            if data.get("objects"):
                return {"status": "success", "data": data["objects"]}
            else:
                return {"status": "error", "message": "No dispatched tickets found for the agent."}

        else:
            return {"status": "error", "message": f"Failed with status code {response.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    

@tool
def get_all_CI_assigned(email: str) -> dict:
    """
    Retrieves a list of Configuration Items (CIs) such as laptops, virtual machines (VMs), and other devices
    associated with the provided user's email.
    """
    if not email:
        return {"error": "Please provide a valid email."}

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    json_data = {
        "operation": "core/get",
        "class": "Person",
        "key": f"SELECT Person WHERE email='{email}'",
        "output_fields": "cis_list"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)

    if response.status_code == 200:
        data = response.json()
        ci_data = data.get("objects", [])

        with open("ci_data.json", 'w') as file:
            file.write(json.dumps(ci_data, indent=4))

        if ci_data:
            laptops = []
            vms = []
            other = []

            for _, incident in ci_data.items():
                cis_list = incident.get('fields', {}).get('cis_list', [])

                if cis_list and isinstance(cis_list, list):
                    for device in cis_list:
                        functionalci_type = device.get("functionalci_id_finalclass_recall", "Unknown")
                        functionalci_name = device.get("functionalci_name", "Unknown")
                        # functionalci_id = device.get("functionalci_id", "Unknown")

                        item = {
                            # "functionalci_id": functionalci_id,
                            "functionalci_name": functionalci_name,
                            "type": functionalci_type
                        }

                        if functionalci_type.lower() == "pc":
                            laptops.append(item)
                        elif functionalci_type.lower() == "virtualmachine":
                            vms.append(item)
                        else:
                            other.append(item)

            return {
                "laptops": laptops,
                "vms": vms,
                "other": other if other else "No other devices found"
            }

        else:
            return {"message": "No devices found for the given email."}

    return {"error": "Sorry, there was an issue fetching the CI details."}
    



@tool
def get_incident_ids_sla_tto_passed_yes(email: str) -> Union[dict, str]:

    """Fetch incident IDs for given email where SLA TTO is marked as 'yes'."""
    
    if not email:
        return "Please provide an email."

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = f"SELECT Incident WHERE agent_id = {contactid} AND sla_tto_passed = 'yes'"

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref"
    }

    response = requests.get(
        url,
        params={"version": "1.0", "json_data": json.dumps(json_data)},
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code == 200:
        data = response.json()
        user_profile_incident = data.get("objects", {})

        # Optional debug log
        with open("user_profile_incident.json", 'w') as file:
            json.dump(user_profile_incident, file, indent=4)

        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]
            if refs:
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


@tool
def get_incident_ids_sla_tto_passed_no(email: str)  -> Union[dict, str]:
    """Fetch incident IDs for given email where SLA TTO is marked as 'yes'."""
    
    if not email:
        return "Please provide an email."

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = f"SELECT Incident WHERE agent_id = {contactid} AND sla_tto_passed = 'no'"

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref"
    }

    response = requests.get(
        url,
        params={"version": "1.0", "json_data": json.dumps(json_data)},
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code == 200:
        data = response.json()
        user_profile_incident = data.get("objects", {})

        # Optional debug log
        with open("user_profile_incident.json", 'w') as file:
            json.dump(user_profile_incident, file, indent=4)

        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]
            if refs:
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."



@tool
def get_incident_ids_sla_ttr_passed_yes(email: str)  -> Union[dict, str]:
    """Fetch incident IDs for given email where SLA TTO is marked as 'yes'."""
    
    if not email:
        return "Please provide an email."

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = f"SELECT Incident WHERE agent_id = {contactid} AND sla_ttr_passed= 'yes'"

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref"
    }

    response = requests.get(
        url,
        params={"version": "1.0", "json_data": json.dumps(json_data)},
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code == 200:
        data = response.json()
        user_profile_incident = data.get("objects", {})

        # Optional debug log
        with open("user_profile_incident.json", 'w') as file:
            json.dump(user_profile_incident, file, indent=4)

        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]
            if refs:
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


@tool
def get_incident_ids_sla_ttr_passed_no(email: str)  -> Union[dict, str]:
    """Fetch incident IDs for given email where SLA TTO is marked as 'yes'."""
    
    if not email:
        return "Please provide an email."

    contact_info = identify_user_profile.invoke({"email": email})
    contactid = contact_info.get("contactid")

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"

    query = f"SELECT Incident WHERE agent_id = {contactid} AND sla_ttr_passed = 'no'"

    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": query,
        "output_fields": "ref"
    }

    response = requests.get(
        url,
        params={"version": "1.0", "json_data": json.dumps(json_data)},
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code == 200:
        data = response.json()
        user_profile_incident = data.get("objects", {})

        # Optional debug log
        with open("user_profile_incident.json", 'w') as file:
            json.dump(user_profile_incident, file, indent=4)

        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]
            if refs:
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


@tool
def get_open_Incident_tickets(email: str) -> list:
    """This tool retrieves all associated **Incident** IDs for a given **contact ID** (agent) and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE operational_status = 'ongoing' AND caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


@tool
def get_closed_Incident_tickets(email: str) -> list:
    """This tool retrieves all associated **Incident** IDs for a given **contact ID** (agent) and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE operational_status = 'closed' AND caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


@tool
def get_open_UserRequest_tickets(email: str) -> list:
    """This tool retrieves all associated **Incident** IDs for a given **contact ID** (agent) and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE operational_status = 'ongoing' AND caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."



@tool
def get_closed_UserRequest_tickets(email: str) -> list:
    """This tool retrieves all associated **Incident** IDs for a given **contact ID** (agent) and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE operational_status = 'closed' AND caller_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


@tool
def get_Incident_priority_wise(email: str, priority: int) -> list:
    """This tool retrieves all associated **Incident** IDs for a given **contact ID** (agent) and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE priority = {priority} AND agent_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


@tool
def get_UserRequest_priority_wise(email: str, priority: int) -> list:
    """This tool retrieves all associated **Incident** IDs for a given **contact ID** (agent) and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE priority = {priority} AND agent_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


@tool
def get_Incident_urgency_wise(email: str, urgency: int) -> list:
    """This tool retrieves all associated **Incident** IDs for a given **contact ID** (agent) and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE urgency = {urgency} AND agent_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


@tool
def get_UserRequest_priority_wise(email: str, urgency: int) -> list:
    """This tool retrieves all associated **Incident** IDs for a given **contact ID** (agent) and **status**."""
    
    contact_info= identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide a email."
    
    contactid= contact_info.get("contactid")
    
    url = f"https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    # Prepare the payload
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE urgency = {urgency} AND agent_id = {contactid}",
        "output_fields": "ref"
    }

    json_string = json.dumps(json_data)
    
    # Prepare headers for Basic Auth
    auth = (USERNAME, PASSWORD)
    
    # Make the GET request
    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()

        # Fix: If "objects" is missing or None, assign an empty dictionary
        user_profile_incident = data.get("objects", {})

        # Optionally write the data to a file for review
        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        # Fix: Ensure user_profile_incident is not empty
        if user_profile_incident:
            refs = [
                incident.get("fields", {}).get("ref", "No ref found") 
                for incident in user_profile_incident.values()
            ]

            if refs:  # Ensures at least one valid reference exists
                return {
                    "refs_count": len(refs),
                    "refs": refs
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."



@tool
def get_faqs_related_to_query(query: str) -> str:
    """
    Return relevant FAQs in a clean, formatted response.
    If the query is generic like 'show me faqs', return all FAQs else filter response according to users query.
    """
    date = datetime.now()
    formatted_date = date.strftime("%Y-%m-%d%%20%H:%M:%S")
    
    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    json_data = {
        "operation": "core/get",
        "class": "FAQ",
        "key": "SELECT FAQ WHERE status ='publish' AND audiences='public'",
        "output_fields": "title,description"
    }
    
    auth = (USERNAME, PASSWORD)
    
    response = requests.get(url, params={"version": "1.0", "json_data": json.dumps(json_data)}, auth=auth)
    
    if response.status_code == 200:
        data = response.json()
        
        faq_list = []
        
        objects = data.get("objects", {})
        
        for obj_key, obj_value in objects.items():
            fields = obj_value.get("fields", {})
            title = fields.get("title", "").strip()
            description = h.handle(fields.get("description", "").strip())
            
            faq_list.append({
                "title": title,
                "description": description
            })
        



@tool
def get_agent_I_tickets(email: str) -> list:
    """This tool retrieves all associated incident refs and caller_ids for a given agent_id."""
    
    contact_info = identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide an email."
    
    contactid = contact_info.get("contactid")

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    json_data = {
        "operation": "core/get",
        "class": "Incident",
        "key": f"SELECT Incident WHERE agent_id = {contactid}",
        "output_fields": "ref, caller_id"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    if response.status_code == 200:
        data = response.json()
        user_profile_incident = data.get("objects", {})

        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        if user_profile_incident:
            incidents = [
                {
                    "ref": incident.get("fields", {}).get("ref", "No ref found"),
                    "caller_id": incident.get("fields", {}).get("caller_id", "No caller_id found")
                }
                for incident in user_profile_incident.values()
            ]

            if incidents:
                return {
                    "count": len(incidents),
                    "incidents": incidents
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."



@tool
def get_agent_R_tickets(email: str) -> list:
    """This tool retrieves all associated incident refs and caller_ids for a given agent_id."""
    
    contact_info = identify_user_profile.invoke({"email": email})

    if not email:
        return "Please provide an email."
    
    contactid = contact_info.get("contactid")

    url = "https://iserve.cats4u.ai:47102/chatbot/web/webservices/rest.php"
    
    json_data = {
        "operation": "core/get",
        "class": "UserRequest",
        "key": f"SELECT UserRequest WHERE agent_id = {contactid}",
        "output_fields": "ref, caller_id"
    }

    json_string = json.dumps(json_data)
    auth = (USERNAME, PASSWORD)

    response = requests.get(url, params={"version": "1.0", "json_data": json_string}, auth=auth)
    
    if response.status_code == 200:
        data = response.json()
        user_profile_incident = data.get("objects", {})

        with open("user_profile_incident.json", 'w') as file:
            file.write(json.dumps(user_profile_incident, indent=4))

        if user_profile_incident:
            incidents = [
                {
                    "ref": incident.get("fields", {}).get("ref", "No ref found"),
                    "caller_id": incident.get("fields", {}).get("caller_id", "No caller_id found")
                }
                for incident in user_profile_incident.values()
            ]

            if incidents:
                return {
                    "count": len(incidents),
                    "incidents": incidents
                }

        return "No incidents found for this contact ID."

    return "Sorry, there was an issue fetching the incident details."


