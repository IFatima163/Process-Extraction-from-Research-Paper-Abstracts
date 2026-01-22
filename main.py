import pdfplumber
import re
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------
# STEP 1: Extract raw text from PDF
# ------------------------
def extract_pdf_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# ------------------------
# STEP 2: Extract abstract using LLM
# ------------------------
def extract_abstract_llm(text):
    prompt = open("prompts/prompt_extract_abstract.txt").read() + "\n\n" + text
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# ------------------------
# STEP 3: Clean abstract text
# ------------------------
def clean_text(t):
    t = re.sub(r"\[[0-9]+\]", "", t)          # remove [12]
    t = re.sub(r"\(.*?\)", "", t)            # remove (Smith, 2020)
    t = re.sub(r"\s+", " ", t)               # fix spacing
    return t.strip()

# ------------------------
# STEP 4: Extract processes using LLM
# ------------------------
def extract_processes_llm(abstract):
    prompt = open("prompts/prompt_extract_processes.txt").read() + "\n\n" + abstract
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    raw_list = response.choices[0].message.content.strip()
    processes = re.findall(r"- (.*)", raw_list) or re.findall(r"\* (.*)", raw_list)
    if not processes:
        processes = [p.strip() for p in raw_list.split("\n") if p.strip()]
    return processes

# ------------------------
# STEP 5: Confidence scoring with LLM
# ------------------------
def score_confidence(processes):
    prompt = open("prompts/prompt_confidence.txt").read() + "\n\nProcesses:\n" + str(processes)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

# ------------------------
# STEP 6: Main pipeline
# ------------------------
def process_pdf(file_path):
    print("Extracting PDF text...")
    raw_text = extract_pdf_text(file_path)

    print("Extracting abstract...")
    abstract = extract_abstract_llm(raw_text)

    print("Cleaning abstract...")
    cleaned = clean_text(abstract)

    print("Extracting processes...")
    processes = extract_processes_llm(cleaned)

    print("Scoring confidence...")
    scored = score_confidence(processes)

    df = pd.DataFrame(eval(scored))
    df["paper_id"] = os.path.basename(file_path)

    output_path = f"data/output/{os.path.basename(file_path)}.csv"
    df.to_csv(output_path, index=False)

    os.rename(file_path, f"data/archive/{os.path.basename(file_path)}")

    print(f"Done. Saved to {output_path}")

# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    input_dir = "data/input/"
    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            process_pdf(os.path.join(input_dir, file))
