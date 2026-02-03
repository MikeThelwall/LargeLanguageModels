These files are associated with the https://sites.google.com/sheffield.ac.uk/peer-ai project. Use at your own risk! API calls cost you money to run!


* 1446_REF_score_reports_correct_scores.py

A specialist program that you probably don't need.


* ChatGPT estimate quality - share.py

This is a general purpose program for creating multiple ChatGPT queries from text files with a variety of different prompts. Despite the program name, it can be used for sentiment analysis prompts as well as research quality estimation. You can also edit it to enter your own prompts.
To use this you will need an ChatGPT API key and a file of texts, one per line, in the format ID tab Text.
You will then need to enter your key into the program and register the name and path of your file.
You will also need to select:

The user prompt template

The location of the system instructions file

The ChatGPT version

Any non-default parameters

Whether to run the queries immediately (faster, but twice as expensive) or create a batch file containing the queries (slower but cheaper). (one query = user prompt including a line of text from the text file, system prompt, parameters, model name). 


* Check_if_Jsonl_valid_share.py

If you create a batch file (recommended) then test it by entering its directory and path here and it will report JSON errors. 

* ChatGPT_Batch_API_share.py
  
If the Jsonl batch file created in the first step then you can run it with the above program, after entering the location of the batch filea and the number of iterations (repeated submissions of the same batch file). You can list multiple batch files for it to submit in one go. It runs them sequentially in series, not parallel, in case of quota issues.
