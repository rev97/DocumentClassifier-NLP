import os
import uuid
import pandas as pd
import numpy as np
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from backend.backend.util import get_text_from_files, preprocess_text, extract_keywords, get_model, extract_words_counts, total_word_counts, string_to_dict, find_column_with_largest_count
from backend.backend.process_pdf_files import get_total_pages, merge_pdfs, save_highlighted_page_as_pdf, upload_pickle_to_s3
from backend.backend.train_model import TextClassifier
import pickle

image_path = r'backend/backend/images'
model_path = r'backend/backend/model'


def get_keywords_dict(file_path, page_number, user_keywords, keywords_dict):
    text = get_text_from_files(file_path, page_number)
    new_document_keywords, keywords_dict = extract_keywords(text, keywords_dict, user_keywords)
    keywords_dict['text'] = text
    return keywords_dict

def handle_training_request(request):
    if len(request.FILES) == 0:
        raise Exception("No files are uploaded")

    if 'file' not in request.FILES:
        raise Exception("'video' field missing in form-data")

    pdf_file = request.FILES['file']

    keywords = request.POST['keywords']
    has_page_range = request.POST['has_page_range']
    page_number = request.POST['page_number']
    keywords_dict = string_to_dict(keywords)
    user_keywords = [item for sublist in keywords_dict.values() for item in sublist]

    APP_ROOT = os.path.dirname(os.path.abspath(__file__))

    file_name = str(uuid.uuid4().hex[:15].upper()) + ".pdf"
    folder_path = os.path.join(APP_ROOT, 'uploads')
    FileSystemStorage(folder_path).save(file_name, pdf_file)
    file_path = os.path.join(folder_path, file_name)

    generated_pdfs = []
    if has_page_range == "true":
        if '-' in page_number:
            start_page, end_page = map(int, page_number.split('-'))
            predictions = []
            bar_data = {}
            classifications = {}
            for page_number in range(start_page, end_page + 1):
                generated_pdf = save_highlighted_page_as_pdf(file_path, page_number, user_keywords, image_path)
                generated_pdfs.append(generated_pdf)
                keywords_dict_page = get_keywords_dict(file_path, page_number, user_keywords, keywords_dict)
                keywords_dict_page['page'] = page_number
                updated_keywords_dict_page = keywords_dict_page.copy()
                for key in keywords_dict_page.keys():
                    # Check if the key contains the substring "_count"
                    if '_count' in key:
                        # If so, compute the sum of the values
                        sum_values = sum(updated_keywords_dict_page[key].values()) if isinstance(updated_keywords_dict_page[key], dict) else updated_keywords_dict_page[key]
                        # Store the sum in a separate key in the same dictionary
                        updated_keywords_dict_page[key + '_sum'] = sum_values
                converted_dict = {key: [value] if not isinstance(value, list) else [str(value)] for key, value in updated_keywords_dict_page.items()}
                df_page = pd.DataFrame(converted_dict)
                predictions.append(df_page)

            result_df = pd.concat(predictions)
            result_df['Label'] = result_df.apply(
                lambda x: find_column_with_largest_count(x), axis=1)

            # MODEL TRAINING
            tc = TextClassifier(result_df)
            nlp_model, pred = tc.train_model(user_keywords)

            # TRAINING STATS
            bar_data['Articles'] = len(result_df['page'])
            # Iterate over the columns of the DataFrame
            for col in result_df.columns:
                # Check if the column name ends with "_count_sum"
                if col.endswith('_count_sum'):
                    # Calculate the sum of values in the column
                    col_sum = result_df[col].sum()
                    # Store the sum in the dictionary with the column name (without the suffix) as the key
                    bar_data[col[:-len('_count_sum')]] = col_sum
                    classifications[col[:-len('_count_sum')]] = col_sum
            bar_data['Word Frequencies'] = total_word_counts(result_df)

            if nlp_model is not None and pred is not None:

                unique_elements, counts = np.unique(pred, return_counts=True)
                model_output = unique_elements[np.argmax(counts)]

                # Get the current date and time
                current_datetime = datetime.now()

                # Format the current date and time as a string to include in the file name
                timestamp_str = current_datetime.strftime("%Y%m%d_%H%M%S")  # Example format: 20220430_154530
                model_file_name = f"model_{timestamp_str}.pkl"
                nlp_model_path = os.path.join(model_path, f"model_{timestamp_str}.pkl")

                # Open the file in binary write mode and serialize the model
                with open(nlp_model_path, 'wb') as file:
                    pickle.dump(nlp_model, file)

                s3_model_url = upload_pickle_to_s3(nlp_model_path, model_file_name)

                output_model = {"model_file": s3_model_url,
                                "classification": classifications,
                                "keywords": set(user_keywords),
                                "bar_data": bar_data}
                return output_model
            else:
                not_found = {"model_file": "no file found",
                                "classification": classifications,
                                "keywords": set(user_keywords),
                                "bar_data": bar_data}
                return not_found
        else:
            # Handle the case when only a single page is given
            page_number = int(page_number)
            generated_pdf = save_highlighted_page_as_pdf(file_path, page_number, user_keywords, image_path)
            predictions = []
            bar_data = {}
            classifications = {}
            keywords_dict_page = get_keywords_dict(file_path, page_number, user_keywords, keywords_dict)
            keywords_dict_page['page'] = page_number
            updated_keywords_dict_page = keywords_dict_page.copy()
            for key in keywords_dict_page.keys():
                # Check if the key contains the substring "_count"
                if '_count' in key:
                    # If so, compute the sum of the values
                    sum_values = sum(updated_keywords_dict_page[key].values()) if isinstance(updated_keywords_dict_page[key], dict) else updated_keywords_dict_page[key]
                    # Store the sum in a separate key in the same dictionary
                    updated_keywords_dict_page[key + '_sum'] = sum_values
            converted_dict = {key: [value] if not isinstance(value, list) else [str(value)] for key, value in updated_keywords_dict_page.items()}
            df_page = pd.DataFrame(converted_dict)
            predictions.append(df_page)

            result_df = pd.concat(predictions)
            result_df['Label'] = result_df['page'].apply(
                lambda x: np.random.choice(list(keywords_dict.keys())))

            # MODEL TRAINING
            tc = TextClassifier(result_df)
            nlp_model, pred = tc.train_model(user_keywords)


            bar_data['Articles'] = len(result_df['page'])
            # Iterate over the columns of the DataFrame
            for col in result_df.columns:
                # Check if the column name ends with "_count_sum"
                if col.endswith('_count_sum'):
                    # Calculate the sum of values in the column
                    col_sum = result_df[col].sum()
                    # Store the sum in the dictionary with the column name (without the suffix) as the key
                    bar_data[col[:-len('_count_sum')]] = col_sum
                    classifications[col[:-len('_count_sum')]] = col_sum
            bar_data['Word Frequencies'] = total_word_counts(result_df)

            if nlp_model is not None and pred is not None:

                unique_elements, counts = np.unique(pred, return_counts=True)
                model_output = unique_elements[np.argmax(counts)]

                # Get the current date and time
                current_datetime = datetime.now()

                # Format the current date and time as a string to include in the file name
                timestamp_str = current_datetime.strftime("%Y%m%d_%H%M%S")  # Example format: 20220430_154530
                model_file_name = f"model_{timestamp_str}.pkl"
                nlp_model_path = os.path.join(model_path, f"model_{timestamp_str}.pkl")

                # Open the file in binary write mode and serialize the model
                with open(nlp_model_path, 'wb') as file:
                    pickle.dump(nlp_model, file)

                s3_model_url = upload_pickle_to_s3(nlp_model_path, model_file_name)

                output_model = {"model_file": s3_model_url,
                                "classification": classifications,
                                "keywords": set(user_keywords),
                                "bar_data": bar_data}
                return output_model

            else:
                not_found = {"model_file": "no file found",
                                "classification": classifications,
                                "keywords": set(user_keywords),
                                "bar_data": bar_data}
                return not_found

    else:
        start_page = 0
        end_page = get_total_pages(file_path)
        predictions = []
        bar_data = {}
        classifications = {}
        for page_number in range(start_page, end_page):
            generated_pdf = save_highlighted_page_as_pdf(file_path, page_number, user_keywords, image_path)
            generated_pdfs.append(generated_pdf)
            keywords_dict_page = get_keywords_dict(file_path, page_number, user_keywords, keywords_dict)
            keywords_dict_page['page'] = page_number
            updated_keywords_dict_page = keywords_dict_page.copy()
            for key in keywords_dict_page.keys():
                # Check if the key contains the substring "_count"
                if '_count' in key:
                    # If so, compute the sum of the values
                    sum_values = sum(updated_keywords_dict_page[key].values()) if isinstance(
                        updated_keywords_dict_page[key], dict) else updated_keywords_dict_page[key]
                    # Store the sum in a separate key in the same dictionary
                    updated_keywords_dict_page[key + '_sum'] = sum_values
            converted_dict = {key: [value] if not isinstance(value, list) else [str(value)] for key, value in
                              updated_keywords_dict_page.items()}
            df_page = pd.DataFrame(converted_dict)
            predictions.append(df_page)

        result_df = pd.concat(predictions)
        result_df['Label'] = result_df.apply(
            lambda x: find_column_with_largest_count(x), axis=1)

        #MODEL TRAINING
        tc = TextClassifier(result_df)
        nlp_model, pred = tc.train_model(user_keywords)


        bar_data['Articles'] = len(result_df['page'])
        # Iterate over the columns of the DataFrame
        for col in result_df.columns:
            # Check if the column name ends with "_count_sum"
            if col.endswith('_count_sum'):
                # Calculate the sum of values in the column
                col_sum = result_df[col].sum()
                # Store the sum in the dictionary with the column name (without the suffix) as the key
                bar_data[col[:-len('_count_sum')]] = col_sum
                classifications[col[:-len('_count_sum')]] = col_sum
        bar_data['Word Frequencies'] = total_word_counts(result_df)

        if nlp_model is not None and pred is not None:

            unique_elements, counts = np.unique(pred, return_counts=True)
            model_output = unique_elements[np.argmax(counts)]

            # Get the current date and time
            current_datetime = datetime.now()

            # Format the current date and time as a string to include in the file name
            timestamp_str = current_datetime.strftime("%Y%m%d_%H%M%S")  # Example format: 20220430_154530
            nlp_model_path = os.path.join(model_path, f"model_{timestamp_str}.pkl")
            model_file_name = f"model_{timestamp_str}.pkl"

            # Open the file in binary write mode and serialize the model
            with open(nlp_model_path, 'wb') as file:
                pickle.dump(nlp_model, file)

            s3_model_url = upload_pickle_to_s3(nlp_model_path, model_file_name)

            output_model = {"model_file": s3_model_url,
                            "classification": classifications,
                            "keywords": set(user_keywords),
                            "bar_data": bar_data}
            return output_model

        else:

            not_found = {"model_file": "no file found",
                         "classification": classifications,
                         "keywords": set(user_keywords),
                         "bar_data": bar_data}
            return not_found



