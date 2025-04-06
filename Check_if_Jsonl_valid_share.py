# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 19:37:45 2024

@author: Mike Thelwall
"""
import json
import os

def is_valid_jsonl(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if line:  # Only process non-empty lines
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"Invalid JSON at line {line_number}: {e}")
                        print(line)
                        return False
        print("The file is a valid JSONL file.")
        return True
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

# CHANGE TO THE PATH CONTAINING YOUR FILE
default_path = r"C:\Users"
os.chdir(default_path)

# CHANGE TO THE FILENAME OF YOUR CHATGPT BATCH FILE
file_path = 'Panel D gpt-4o-mini-2024-07-18 1743958728.txt'

is_valid_jsonl(file_path)

