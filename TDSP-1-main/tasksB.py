import os
import requests
import json
import subprocess
import sqlite3
import duckdb
from scipy.spatial.distance import cosine
from PIL import Image
import markdown
from flask import Flask, request, jsonify

###########################
# Security Checks (B1 & B2)
###########################

def B12(filepath):
    """
    Check if the normalized absolute path of 'filepath' is within '/data'.
    """
    normalized = os.path.abspath(filepath)
    allowed_dir = os.path.abspath('/data')
    return normalized.startswith(allowed_dir)

###########################
# B3: Fetch Data from an API
###########################

def B3(url, save_path):
    """
    Fetch data from the API at 'url' and save the text response to 'save_path'.
    """
    if not B12(save_path):
        raise PermissionError("Access outside /data is not allowed.")
    response = requests.get(url)
    response.raise_for_status()
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(response.text)
    print(f"Data fetched from {url} and saved to {save_path}")

###########################
# B4: Clone a Git Repo and Make a Commit
###########################

def B4(repo_url, commit_message, clone_dir='/data/repo'):
    """
    Clone a git repository from 'repo_url' into 'clone_dir' (must be within /data)
    and make a commit with 'commit_message'.
    """
    if not B12(clone_dir):
        raise PermissionError("Access outside /data is not allowed.")
    
    # Clone the repository
    subprocess.run(["git", "clone", repo_url, clone_dir], check=True)
    
    # Optionally, you could create or modify a file here.
    # For example, create a dummy file to commit.
    dummy_file = os.path.join(clone_dir, "dummy.txt")
    with open(dummy_file, 'w', encoding='utf-8') as f:
        f.write("This is a dummy commit.\n")
    
    # Stage changes and commit
    subprocess.run(["git", "-C", clone_dir, "add", "."], check=True)
    subprocess.run(["git", "-C", clone_dir, "commit", "-m", commit_message], check=True)
    print(f"Repository cloned from {repo_url} into {clone_dir} and commit made.")

###########################
# B5: Run SQL Query on a SQLite or DuckDB Database
###########################

def B5(db_path, query, output_filename):
    """
    Run the SQL 'query' on the database at 'db_path' (SQLite for .db files, DuckDB otherwise)
    and write the result (as a string) to 'output_filename'.
    """
    if not B12(db_path) or not B12(output_filename):
        raise PermissionError("Access outside /data is not allowed.")
    
    if db_path.endswith('.db'):
        conn = sqlite3.connect(db_path)
    else:
        conn = duckdb.connect(db_path)
    
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()
    
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(str(result))
    
    print(f"SQL query executed on {db_path} and results written to {output_filename}")
    return result

###########################
# B6: Web Scraping (Extract Data from a Website)
###########################

def B6(url, output_filename):
    """
    Scrape the content from the specified 'url' and save it to 'output_filename'.
    """
    if not B12(output_filename):
        raise PermissionError("Access outside /data is not allowed.")
    
    result = requests.get(url).text
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(result)
    
    print(f"Web content from {url} written to {output_filename}")

###########################
# B7: Compress or Resize an Image
###########################

def B7(image_path, output_path, resize=None):
    """
    Open the image at 'image_path', optionally resize it (provide a (width, height) tuple),
    and save it to 'output_path'.
    """
    if not B12(image_path) or not B12(output_path):
        raise PermissionError("Access outside /data is not allowed.")
    
    img = Image.open(image_path)
    if resize:
        img = img.resize(resize)
    img.save(output_path)
    print(f"Image processed from {image_path} and saved to {output_path}")

###########################
# B8: Transcribe Audio from an MP3 File
###########################

def B8(audio_path, output_path):
    """
    Transcribe the audio from 'audio_path' using OpenAI's Whisper API
    and save the transcription text to 'output_path'.
    """
    if not B12(audio_path) or not B12(output_path):
        raise PermissionError("Access outside /data is not allowed.")
    
    import openai
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if openai.api_key is None:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    
    with open(audio_path, 'rb') as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    
    transcription_text = transcript.get('text', '')
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(transcription_text)
    
    print(f"Audio from {audio_path} transcribed and saved to {output_path}")
    return transcription_text

###########################
# B9: Convert Markdown to HTML
###########################

def B9(md_path, output_path):
    """
    Convert the Markdown file at 'md_path' to HTML and save it to 'output_path'.
    """
    if not B12(md_path) or not B12(output_path):
        raise PermissionError("Access outside /data is not allowed.")
    
    with open(md_path, 'r', encoding='utf-8') as file:
        html = markdown.markdown(file.read())
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html)
    
    print(f"Markdown from {md_path} converted to HTML and saved to {output_path}")

###########################
# B10: API Endpoint for CSV Filtering
###########################
