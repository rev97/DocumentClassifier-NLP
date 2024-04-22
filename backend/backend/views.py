import os
import uuid
import pandas as pd
import numpy as np
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from rest_framework.decorators import api_view
from backend.backend.util import get_text_from_files, preprocess_text, extract_keywords, get_model, extract_words_counts, total_word_counts, string_to_dict, find_column_with_largest_count
from backend.backend.process_pdf_files import get_total_pages, merge_pdfs, save_highlighted_page_as_pdf
from backend.backend.train_model import TextClassifier
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render


pickle_file_path = r'backend/backend/model/nlp_model.pkl'
image_path = r'backend/backend/images'


def predict_class(file_path, page_number, user_keywords, keywords_dict, model):
    text = get_text_from_files(file_path, page_number)
    # DEFINE A NEW FUNCTION FOR RETURNING KEYWORDS
    #new_document_keywords, tech_keys, class1_keys, class2_keys, class3_keys, tech_fq, class_1_fq, class_2_fq, class_3_fq  = extract_keywords_nltk(preprocess_text(text), user_keywords, keywords, class_1_keywords, class_2_keywords, class_3_keywords)
    new_document_keywords, keywords_dict = extract_keywords(text, keywords_dict, user_keywords)
    keywords_dict['text'] = text
    predicted_class = model.predict([new_document_keywords])
    return predicted_class, keywords_dict



def handle_upload(request):
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
    nlp_model = get_model(pickle_file_path)
    if has_page_range == "true":
        if '-' in page_number:
            start_page, end_page = map(int, page_number.split('-'))
            predictions = []
            bar_data = {}
            for page_number in range(start_page, end_page + 1):
                generated_pdf = save_highlighted_page_as_pdf(file_path, page_number, user_keywords, image_path)
                generated_pdfs.append(generated_pdf)
                prediction, keywords_dict_page = predict_class(file_path, page_number, user_keywords, keywords_dict, nlp_model)
                keywords_dict_page['prediction'] = prediction[0]
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
            result_df['Label'] = result_df['prediction'].apply(
                lambda x: find_column_with_largest_count(x), axis=1)
            tc = TextClassifier(result_df)
            nlp_model, pred = tc.train_model(user_keywords)
            unique_elements, counts = np.unique(pred, return_counts=True)
            model_output = unique_elements[np.argmax(counts)]
            bar_data['Articles'] = len(result_df['page'])
            # Iterate over the columns of the DataFrame
            for col in result_df.columns:
                # Check if the column name ends with "_count_sum"
                if col.endswith('_count_sum'):
                    # Calculate the sum of values in the column
                    col_sum = result_df[col].sum()
                    # Store the sum in the dictionary with the column name (without the suffix) as the key
                    bar_data[col[:-len('_count_sum')]] = col_sum
            bar_data['Word Frequencies'] = total_word_counts(result_df)

            #merged_pdf_path = os.path.join(image_path, 'merged_highlighted_pages.pdf')
            s3_file_url = merge_pdfs(generated_pdfs, image_path)
            output_pages = {"classification": model_output,
                            "keywords": set(user_keywords),
                            "output_pdf_path": s3_file_url,
                            "bar_data": bar_data}
            return output_pages
        else:
            # Handle the case when only a single page is given
            page_number = int(page_number)
            generated_pdf = save_highlighted_page_as_pdf(file_path, page_number, user_keywords, image_path)
            generated_pdfs.append(generated_pdf)
            predictions = []
            bar_data = {}
            prediction, keywords_dict_page = predict_class(file_path, page_number, user_keywords, keywords_dict, nlp_model)
            keywords_dict_page['prediction'] = prediction[0]
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
            result_df['Label'] = result_df['prediction'].apply(
                lambda x: np.random.choice(list(keywords_dict.keys())))
            bar_data['Articles'] = len(result_df['page'])
            # Iterate over the columns of the DataFrame
            for col in result_df.columns:
                # Check if the column name ends with "_count_sum"
                if col.endswith('_count_sum'):
                    # Calculate the sum of values in the column
                    col_sum = result_df[col].sum()
                    # Store the sum in the dictionary with the column name (without the suffix) as the key
                    bar_data[col[:-len('_count_sum')]] = col_sum
            bar_data['Word Frequencies'] = total_word_counts(result_df)
            s3_file_url = merge_pdfs(generated_pdfs, image_path)
            output_pages = {"classification": result_df['Label'].tolist()[0],
                            "keywords": set(user_keywords),
                            "output_pdf_path": s3_file_url,
                            "bar_data": bar_data}
            return output_pages

    else:
        start_page = 0
        end_page = get_total_pages(file_path)
        predictions = []
        bar_data = {}
        for page_number in range(start_page, end_page):
            generated_pdf = save_highlighted_page_as_pdf(file_path, page_number, user_keywords, image_path)
            generated_pdfs.append(generated_pdf)
            prediction, keywords_dict_page = predict_class(file_path, page_number, user_keywords, keywords_dict,
                                                           nlp_model)
            keywords_dict_page['prediction'] = prediction[0]
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
        tc = TextClassifier(result_df)
        nlp_model, pred = tc.train_model(user_keywords)
        unique_elements, counts = np.unique(pred, return_counts=True)
        model_output = unique_elements[np.argmax(counts)]
        bar_data['Articles'] = len(result_df['page'])
        # Iterate over the columns of the DataFrame
        for col in result_df.columns:
            # Check if the column name ends with "_count_sum"
            if col.endswith('_count_sum'):
                # Calculate the sum of values in the column
                col_sum = result_df[col].sum()
                # Store the sum in the dictionary with the column name (without the suffix) as the key
                bar_data[col[:-len('_count_sum')]] = col_sum
        bar_data['Word Frequencies'] = total_word_counts(result_df)

        #merged_pdf_path = os.path.join(image_path, 'merged_highlighted_pages.pdf')
        s3_file_url = merge_pdfs(generated_pdfs, image_path)
        output_pages = {"classification": model_output,
                        "keywords": set(user_keywords),
                        "output_pdf_path": s3_file_url,
                        "bar_data": bar_data}
        return output_pages



@api_view(['POST'])
def main_api(request):
    if request.method == 'POST':
        output = handle_upload(request)

        return Response(output)

@xframe_options_exempt
@api_view(['GET'])
def view_pdf(request):
    pdf_path = request.GET.get('path', '')

    # Validate pdf_path if needed

    # Assuming your PDFs are stored in a 'pdfs' directory within your Django project
    pdf_full_path = f'{pdf_path}'

    with open(pdf_full_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{pdf_path}"'
        return response


@xframe_options_exempt
@api_view(['GET'])
def home(request):
    return render(request, 'index.html')