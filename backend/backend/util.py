import pandas as pd
import fitz  # PyMuPDF
import json
import pickle
import nltk
from nltk.corpus import stopwords
from collections import defaultdict
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


def word_frequency(word_list, text):
    # Tokenize the text using NLTK's word_tokenize function
    words = nltk.word_tokenize(text)

    # Convert the word list to lowercase for case-insensitive matching
    word_list_lower = [word.lower() for word in word_list]

    # Initialize a defaultdict to store word frequencies
    frequency_dict = defaultdict(int)

    # Iterate through each word in the tokenized text
    for word in words:
        # Convert the word to lowercase for case-insensitive matching
        word_lower = word.lower()
        # If the lowercase word is in the word list
        if word_lower in word_list_lower:
            # Increment the frequency count for the current word
            frequency_dict[word_lower] += 1

    return dict(frequency_dict)


def extract_keywords_nltk(text, user_keywords,keywords, class_1_keywords, class_2_keywords, class_3_keywords):
    all_keywords = [word.lower() for word in nltk.word_tokenize(text) if word.lower() in user_keywords]
    no_of_tech = len([word.lower() for word in nltk.word_tokenize(text) if word.lower() in keywords])
    no_of_class_1 = len([word.lower() for word in nltk.word_tokenize(text) if word.lower() in class_1_keywords])
    no_of_class_2 = len([word.lower() for word in nltk.word_tokenize(text) if word.lower() in class_2_keywords])
    no_of_class_3 = len([word.lower() for word in nltk.word_tokenize(text) if word.lower() in class_3_keywords])
    tech_wf  = word_frequency(keywords, text)
    class_1_wf = word_frequency(class_1_keywords, text)
    class_2_wf = word_frequency(class_2_keywords, text)
    class_3_wf = word_frequency(class_3_keywords, text)
    return " ".join(all_keywords), no_of_tech, no_of_class_1, no_of_class_2, no_of_class_3, tech_wf, class_1_wf, class_2_wf, class_3_wf


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


# Function to extract words and their counts from a dictionary
def extract_words_counts(string_dict):
    #string_dict = string_dict.replace("\\", "")
    #string_dict = string_dict.replace("'", '"')
    #dictionary = json.loads(string_dict)
    return string_dict

# Calculate the total count of each individual unique word across all 'wf' columns
def total_word_counts(df):
    total_dict = {}
    for col in df.columns:
        if col.endswith('_wf'):
            wf_dicts = df[col].apply(extract_words_counts)
            for wf_dict in wf_dicts:
                for word, count in wf_dict.items():
                    total_dict[word] = total_dict.get(word, 0) + count
    return total_dict