# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 18:42:45 2024
https://platform.openai.com/docs/guides/batch
@author: Mike Thelwall

WARNING: USE THIS PROGRAM AT YOUR OWN RISK! IT COSTS MONEY FROM OPENAI

This file automtically submits batch jobs to ChatGPT API

There are helper fuctions not used to do other tasks, like cancelling batches - but you will need to modify this code to call them.

#Example batch file contents
#{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-3.5-turbo-0125", "messages": [{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": "Hello world!"}],"max_tokens": 1000}}
#{"custom_id": "request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-3.5-turbo-0125", "messages": [{"role": "system", "content": "You are an unhelpful assistant."},{"role": "user", "content": "Hello world!"}],"max_tokens": 1000}}

"""
from openai import OpenAI
import time 
import os, sys
client = OpenAI(api_key='YOUR OPENAI API KEY HERE') #WARNING: USE THIS PROGRAM AT YOUR OWN RISK! IT COSTS MONEY FROM OPENAI

#SET BOOLEANS AND FILENAME AND IDs if needed
#All REF A B C D
default_path = r'C:\Users\Batch'
batch_input_file_path_set = ["Panel C gpt-4o-2024-11-20 1741469250_1.txt","Panel C gpt-4o-2024-11-20 1741469250_2.txt"] 


file_object_id_set1 = [] # 
batch_input_file_id_set =[] # Set to non-null to overide batch_input_file_path_set
automatic_batch = True # Do everything in one go

batch_iterations = 1 # Number of times to submit each batch e.g. 1, 5, 10, or 30

upload_batch_input_files = False
create_batch = False
check_batch_status = False
save_batch_when_ready = False
list_all_batches = False
save_batch = False
just_save_batch = False; batch_id = "batch_6750dde8cf659dda"  # Set to true to save batch and nothing else - must set batch id too
list_files = False
delete_batch_input_file = False

batch_input_file_id = "" 
batch_output_file_id = ""


os.chdir(default_path)

cancel_batch = [] # Can't cancel failed batch ["batch_CBQu8RfkuAJMc9Sw9cKtWKAg","batch_lyV0UyAs0jv6jloOWAqNETVk"]
file_time_id = str(int(time.time()))


def batch_save_when_ready(batch_id, record_file_path): # batch_save_when_ready(batch_id,batch_record_file_path)
    batch_unfinished = True
    wait_mins=0
    while batch_unfinished:
        time.sleep(60) # Sleep for 60 seconds
        wait_mins += 1
        batch_status = client.batches.retrieve(batch_id)
        print(str(batch_status) + " " + str(batch_status.request_counts) + " after mins: "+ str(wait_mins))
        if batch_status.status == "completed":
            batch_output_file_id = batch_status.output_file_id
            print(batch_output_file_id)
            file_response = client.files.content(batch_output_file_id)
            with open(record_file_path,"a", encoding="utf-8") as batchfile:
                batchfile.write(file_response.text)
            batch_unfinished = False
    return batch_output_file_id

if just_save_batch:
    save_filename = str(int(time.time())) + "extra saved batch_record.txt"
    batch_save_when_ready(batch_id,save_filename)
    print("Saved to " + save_filename)
    sys.exit()

batch_record_file_path_set = []
if len(batch_input_file_path_set) > 1:
    for i in range (len(batch_input_file_path_set)): # for batch_input_file in batch_input_file_path_set:
    	batch_record_file_path_set.append(batch_input_file_path_set[i][:-4] + " " + file_time_id + "_record.txt")
    #batch_record_file_path_set = batch_input_file_path_set[0][:-6] + " " + file_time_id + "_record.txt"
else:
    batch_record_file_path = batch_input_file_path_set[0][:-4] + " " + file_time_id + "_record.txt" # For non-batch versions'
    batch_record_file_path_set.append(batch_input_file_path_set[0][:-4] + " " + file_time_id + "_record.txt")

if len(file_object_id_set1)>0 and len(batch_input_file_path_set) > 0:
    print("Only one must be non-empty: file_object_id_set1, batch_input_file_path_set")
    sys.exit(0)

# Upload batch files
batch_file_count = 0
batch_input_file_set = []
if upload_batch_input_files:
    for batch_input_file_path in batch_input_file_path_set:
        batch_file_count += 1 
        batch_input_file_set[batch_file_count] = client.files.create(
          file=open(batch_input_file_path[0], "rb"),
          purpose="batch"
        )
        print(batch_input_file_set[batch_file_count].id)

if create_batch:
    batch_input_file_id = batch_input_file_set[0].id
    batch_object = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
          "description": "batch_record_file_path"
        }
    )
    batch_id = batch_object.id
    print(batch_object)
    with open(batch_record_file_path,"a", encoding="utf-8") as batchfile:
        batchfile.write(str(batch_object))

if check_batch_status:
    batch_status = client.batches.retrieve(batch_id)
    if batch_status.status == "completed":
        batch_output_file_id = batch_status.output_file_id
        if save_batch_when_ready:
            save_batch = True
    print(batch_status)

if list_all_batches:
    print(str(client.batches.list(limit=100)).replace("Batch(id=","\nBatch(id=")) #https://platform.openai.com/docs/api-reference/batch/list after last object id

#Get results when ready
if save_batch:
    file_response = client.files.content(batch_output_file_id)
    #print(file_response.text)
    with open(batch_record_file_path,"a", encoding="utf-8") as batchfile:
        batchfile.write(file_response.text)

if len(cancel_batch) > 0:
    for batch in cancel_batch:
        client.batches.cancel(batch) #Can't delete - wait 24h?

if delete_batch_input_file:
    client.files.delete(batch_input_file_id)
    print("File " + batch_input_file_id + " deleted.")
    
if list_files:
    file_list = client.files.list()
    print(str(file_list).replace("FileObject","\nFileObject"))

def batch_start(input_file_id, record_file_path): # batch_start(batch_input_file_id,batch_record_file_path)
    batch_object = client.batches.create(
        input_file_id=input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
          "description": record_file_path
        }
    )
    batch_id = batch_object.id
    print(batch_object)
    with open(record_file_path,"a", encoding="utf-8") as batchfile:
        batchfile.write(str(batch_object))
    return batch_id

def batch_save_when_ready_copy(batch_id, record_file_path): # batch_save_when_ready(batch_id,batch_record_file_path)
    batch_unfinished = True
    wait_mins=0
    while batch_unfinished:
        time.sleep(60) # Sleep for 60 seconds
        wait_mins += 1
        batch_status = client.batches.retrieve(batch_id)
        print(str(batch_status) + " " + str(batch_status.request_counts) + " after mins: "+ str(wait_mins))
        if batch_status.status == "completed":
            batch_output_file_id = batch_status.output_file_id
            print(batch_output_file_id)
            file_response = client.files.content(batch_output_file_id)
            with open(record_file_path,"a", encoding="utf-8") as batchfile:
                batchfile.write(file_response.text)
            batch_unfinished = False
    return batch_output_file_id

if automatic_batch: 
    # First upload all files
    batch_input_file_id_set=[]
    # batch_set_count = 0
    for j in range (len(batch_input_file_path_set)): # for batch_input_file in batch_input_file_path_set:
        # batch_set_count += 1
        print("Batch set " + str(j+1)+ "/" + str(len(batch_input_file_path_set)))
        batch_input_file_object = client.files.create(
          file=open(batch_input_file_path_set[j], "rb"),#
          purpose="batch"
        )
        print(batch_input_file_object)
        batch_input_file_id_set.append(batch_input_file_object.id)
    for i in range(batch_iterations):
        print("Iteration " + str(i+1)+ "/" + str(batch_iterations))
        # batch_set_count = 0
        for j in range (len(batch_input_file_path_set)): # for batch_input_file in batch_input_file_path_set:
            batch_record_file_path_iteration = batch_record_file_path_set[j][:-11] + " " + str(i) + "_record.txt"   #batch_record_file_path = batch_input_file_path + " " + file_time_id + " " + str(i) + "_record.txt"
            # batch_set_count += 1
            print("Batch set " + str(j+1)+ "/" + str(len(batch_input_file_path_set)))
            batch_id = batch_start(batch_input_file_id_set[j],batch_record_file_path_iteration)
            batch_save_when_ready(batch_id,batch_record_file_path_iteration)
            
            