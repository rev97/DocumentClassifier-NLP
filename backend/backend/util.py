import pandas as pd
import fitz  # PyMuPDF
import json
import pickle
import nltk
from nltk.corpus import stopwords
import re
# Download NLTK resources
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Initialize NLTK's English stopwords
stop_words = set(stopwords.words('english'))
def preprocess_text(text):
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    cleaned_text = ' '.join(cleaned_text.split())
    lemmatizer = nltk.stem.WordNetLemmatizer()
    lemmatized_text = ' '.join(
        [lemmatizer.lemmatize(word) for word in cleaned_text.split() if word not in stop_words])
    return lemmatized_text

def get_model(pickle_file_path):
    try:
        nlp_model = load_pickle_file(pickle_file_path)
        print(f"Successfully loaded the object from {pickle_file_path}")
        return nlp_model
    except FileNotFoundError:
        print(f"Error: File not found at path '{pickle_file_path}'")
    except pickle.UnpicklingError as e:
        print(f"Error: Unable to unpickle the file '{pickle_file_path}': {e}")
def extract_keywords_nltk(text, user_keywords):
    keywords = [word.lower() for word in nltk.word_tokenize(text) if word.lower() in user_keywords]
    return " ".join(keywords)

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def get_text_from_files(file_name, page_number):
    pdf_document = fitz.open(file_name)

    page = pdf_document[int(page_number)]
    text_content = page.get_text()

    pdf_document.close()

    return text_content


def read_dataset(csv_file):
    df = pd.read_csv(csv_file)
    return df


def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
        return text_content
    except FileNotFoundError:
        print(f"Error: File not found at path '{file_path}'")
        return None


def load_pickle_file(file_path):
    with open(file_path, 'rb') as file:
        loaded_object = pickle.load(file)
    return loaded_object


def get_last_word_in_string(input_string):
    words = input_string.split()
    if words:
        last_word = words[-1]
        return last_word
    else:
        return None