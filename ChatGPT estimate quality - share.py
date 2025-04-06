# -*- coding: utf-8 -*-
"""
#########################################################################################################
## Runs ChatGPT completions live online or saves them to a batch file for running in ChatGPT Batch API ##
## Written by Mike Thelwall with a lot of help from elsewhere 
## WARNING!!!! USING THIS WILL COST YOU MONEY IN API CALLS FROM OPENAI.
##  DO NOT USE THIS PROGRAM IF YOU DON'T FULLY UNDERSTAND THIS.
##  USE OF THIS PROGRAM ***WILL*** COST YOU MONEY AND IS AT YOUR OWN RISK.
#########################################################################################################
"""
import sys
import os
import datetime, time
from openai import OpenAI


SIMPLE_PROMPT = 1; ICS_PROMPT = 4; IS_STATEMENT_TRUE_PROMPT = 5; SENTISTRENGTH_CHINESE_PROMPT = 6; SENTISTRENGTH_ENGLISH_PROMPT = 7

file_time_id = str(int(time.time())) 

###############################################################################
# Configure everythiing in this section
###############################################################################
client = OpenAI(api_key='YOUR OPEN AI KEY HERE') ##  USE OF THIS PROGRAM ***WILL*** COST YOU MONEY AND IS AT YOUR OWN RISK.

prompt_type = SIMPLE_PROMPT
        
batch_file_root = r"C:\title_abs "  #Start of filename of output batch file
jsonl_file = r"C:\title_abstract.txt" #File of lines to be processed in format ID -tab- text. No double quotes, no lines can end in \. Unsual characters may cause Json errors. Check that any batch file created is valid with another file in this Github folder.
system_file = r"C:\ChatGPT D instructions 12 July 2024.txt" # File of system instructions. Can contain newwlines.

save_as_batch = True   
batch_fine_tuning = False   

gpt_model = "gpt-4o-mini-2024-07-18" 
gpt_max_tokens = 1000 #  1000 normally, 40 for sentiment, 40 for truth checker

gpt_temperature = 1 # Default 1
gpt_top_p = 1 # Default and max 1
gpt_frequency_penalty = 0
gpt_presence_penalty = 0

max_lines = 120000000
max_lines_per_batch = 15000
###############################################################

if batch_fine_tuning:
    batch_file = batch_file_root + "fine_tune " + file_time_id + ".txt"
    results_file = os.path.splitext(batch_file)[0] + "_info.txt"
elif save_as_batch:
    batch_file = batch_file_root + gpt_model.replace(":","") + " " + file_time_id + ".txt"
    results_file = os.path.splitext(batch_file)[0] + "_info.txt"
else:
    results_file = jsonl_file + file_time_id + "out.txt"
   

def make_prompt_for_article(prompt_type, article_text):
    if prompt_type == SIMPLE_PROMPT:
        return "Score this article: " + article_text
    elif prompt_type == ICS_PROMPT:
        return "Score the following impact case study: " + article_text
    elif prompt_type == IS_STATEMENT_TRUE_PROMPT:
        return "Is the following statement true? " + article_text
    elif prompt_type == SENTISTRENGTH_CHINESE_PROMPT:
        return "Assess the strength of positive and negative sentiment in the following Chinese text. Respond only with one of the following: 'very strong positive sentiment', 'strong positive sentiment', 'moderate positive sentiment', 'weak positive sentiment', or 'no positive sentiment'; AND with one of the following: 'very strong negative sentiment', 'strong negative sentiment', 'moderate negative sentiment', 'weak negative sentiment', or 'no negative sentiment'. " + article_text
    elif prompt_type == SENTISTRENGTH_ENGLISH_PROMPT:
        return "Assess the strength of positive and negative sentiment in the following text. Respond only with one of the following: 'very strong positive sentiment', 'strong positive sentiment', 'moderate positive sentiment', 'weak positive sentiment', or 'no positive sentiment'; AND with one of the following: 'very strong negative sentiment', 'strong negative sentiment', 'moderate negative sentiment', 'weak negative sentiment', or 'no negative sentiment'. "  + article_text
    print("Error unknonwn prompt type"); sys.exit(0)

def ChatGPT_completion(system_msg, user_msg):
    return client.chat.completions.create(
      model=gpt_model,
      messages=[
        {
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": system_msg
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": user_msg
            }
          ]
        }
      ],
      temperature=gpt_temperature,
      max_tokens=gpt_max_tokens, # 668 is long ChatGPT ref assessor output, 1000 should be OK. The maximum number of tokens to generate shared between the prompt and completion. The exact limit varies by model. (One token is roughly 4 characters for standard English text)
      top_p=gpt_top_p,
      frequency_penalty=gpt_frequency_penalty,
      presence_penalty=gpt_presence_penalty
    )

def ChatGPT_batch_query_no_system_message(user_msg,batch_id,request_id):
    line_1 = '{"custom_id": "request-' + batch_id + '-' + request_id + '", "method": "POST", "url": "/v1/chat/completions", "body": {'
    line_2 = '"model": "' + gpt_model + '", "messages": [{"role": "user", "content": [{"type": "text","text": "' + user_msg + '"}]}],' 
    line_4 = '"temperature":' + str(gpt_temperature) + ', "max_tokens": ' + str(gpt_max_tokens) + ',"top_p": ' + str(gpt_top_p) + ', "frequency_penalty": ' + str(gpt_frequency_penalty)
    line_5 = ', "presence_penalty": ' + str(gpt_presence_penalty) + '}}\n'
    return line_1 + line_2 + line_4 + line_5

def ChatGPT_batch_query(system_msg, user_msg,batch_id,request_id):
    if system_msg == "":
        return ChatGPT_batch_query_no_system_message(user_msg,batch_id,request_id)
    else:
        
        line_1 = '{"custom_id": "request-' + batch_id + '-' + request_id + '", "method": "POST", "url": "/v1/chat/completions", "body": {'
        line_2 = '"model": "' + gpt_model + '", "messages": [{"role":"system","content":[{"type":"text", "text":"' + system_msg + '"}]},'  
        line_3 = '{"role": "user", "content": [{"type": "text","text": "' + user_msg.rstrip('\\') + '"}]}],' 
        line_4 = '"temperature":' + str(gpt_temperature) + ', "max_tokens": ' + str(gpt_max_tokens) + ',"top_p": ' + str(gpt_top_p) + ', "frequency_penalty": ' + str(gpt_frequency_penalty)
        line_5 = ', "presence_penalty": ' + str(gpt_presence_penalty) + '}}\n'
        return line_1 + line_2 + line_3 + line_4 + line_5

def ChatGPT_fine_tune(system_msg, user_msg, assistant_response, batch_id,request_id):
    line_1 = '{"messages": [{"role": "system", "content": "' + system_msg + '"},' 
    line_2 = '{"role": "user", "content": "' + user_msg + '"},' 
    line_3 = '{"role": "assistant", "content": "' + assistant_response + '"}]}' 
    return line_1 + line_2 + line_3

def split_file(input_file, output_prefix, max_lines_per_batch):
    with open(input_file, 'r', encoding="utf-8") as file:
        line_count = 0
        file_count = 1
        output_file = open(f'{output_prefix}_{file_count}.txt', 'w', encoding="utf-8")
        for line in file:  #If this generates an error, fix the file
            if line_count == max_lines_per_batch:
                output_file.close()
                file_count += 1
                output_file = open(f'{output_prefix}_{file_count}.txt', 'w', encoding="utf-8")
                line_count = 0
            output_file.write(line)
            line_count += 1
        output_file.close()

######################################################################################################
#                                            Main program
######################################################################################################
if system_file == "":
    system_text = ""
    print("No system file!")
else:
    with open(system_file, 'r', encoding="utf-8") as f:
        system_text = f.read()
    system_text = system_text.replace("\n","\\n")

line_count = 0
with open(results_file,"a", encoding="utf-8") as resultsfile:
    resultsfile.write("Date and time run: " + str(datetime.datetime.now()) + "\n")
    resultsfile.write("jsonl_file: "+jsonl_file+"\n")
    if system_file != "": resultsfile.write("system_file: " + system_file + "\n")
    if system_text != "": resultsfile.write("system_text: " + system_text + "\n")
    resultsfile.write("user_prompt: "+ make_prompt_for_article(prompt_type,"") + "\n")
    if not batch_fine_tuning:
        resultsfile.write("gpt_model: " + gpt_model + "\n")
        resultsfile.write("gpt_temperature: "+str(gpt_temperature)+"\n")
        resultsfile.write("gpt_max_tokens: "+str(gpt_max_tokens)+"\n")
        resultsfile.write("gpt_top_p: "+str(gpt_top_p))
        resultsfile.write("gpt_frequency_penalty: "+str(gpt_frequency_penalty)+"\n")
        resultsfile.write("gpt_presence_penalty: "+str(gpt_presence_penalty)+"\n\n")
    with open(jsonl_file, 'r', encoding="utf-8") as infile:
        if save_as_batch:
            batch_set = 0
            with open(batch_file,"a", encoding="utf-8") as batchfile:
                for line in infile:
                    line_count += 1
                    try:
                        if line_count <= max_lines:
                            columns = line.strip().split('\t')
                            prompt_including_article = make_prompt_for_article(prompt_type, columns[1]) #user_prompt + columns[1] #
                            if batch_fine_tuning:
                                batchfile.write(ChatGPT_fine_tune(system_text,prompt_including_article,columns[2],file_time_id,str(line_count)))
                            else:
                                batchfile.write(ChatGPT_batch_query(system_text,prompt_including_article, file_time_id, str(line_count)))
                    except Exception as e:
                        print(e)
                        print(line)
        else: # run now in API
            for line in infile:
                line_count += 1
                if line_count <= max_lines:
                    columns = line.strip().split('\t')
                    try:
                        prompt_including_article = make_prompt_for_article(prompt_type, columns[1]) # = user_prompt + columns[1] #make_prompt_for_article(prompt_type, article_text)
                        response = ChatGPT_completion(system_text,prompt_including_article)
                        resultsfile.write(columns[0] + "\n" + str(response) + "\n\n" )
                    except:
                        print(line)

# split into consecutive batch files
if max_lines_per_batch > 0 and max_lines_per_batch < line_count:
    split_file(batch_file, os.path.splitext(batch_file)[0],max_lines_per_batch) 
