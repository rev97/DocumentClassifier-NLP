import os
import uuid
import pandas as pd
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from rest_framework.decorators import api_view
from backend.util import get_text_from_files, preprocess_text, extract_keywords_nltk, get_model
from backend.process_pdf_files import get_total_pages, merge_pdfs, save_highlighted_page_as_pdf
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt


pickle_file_path = r'/Users/revanthgottuparthy/Desktop/NLP project/DocumentClassifier-NLP/backend/backend/model/nlp_model.pkl'
image_path = r'/Users/revanthgottuparthy/Desktop/NLP project/DocumentClassifier-NLP/backend/backend/images'


def predict_class(file_path, page_number, user_keywords, keywords, class_1_keywords, class_2_keywords, class_3_keywords, model):
    text = get_text_from_files(file_path, page_number)
    new_document_keywords, tech_keys, class1_keys, class2_keys, class3_keys = extract_keywords_nltk(preprocess_text(text), user_keywords, keywords, class_1_keywords, class_2_keywords, class_3_keywords)
    predicted_class = model.predict([new_document_keywords])
    return predicted_class, tech_keys, class1_keys, class2_keys, class3_keys



def handle_upload(request):
    if len(request.FILES) == 0:
        raise Exception("No files are uploaded")

    if 'file' not in request.FILES:
        raise Exception("'video' field missing in form-data")

    pdf_file = request.FILES['file']

    keywords = request.POST['keywords'].split(",")
    class_1_keywords = request.POST['preliminary_keywords'].split(",")
    class_2_keywords = request.POST['implementation_keywords'].split(",")
    class_3_keywords = request.POST['advanced_keywords'].split(",")
    has_page_range = request.POST['has_page_range']
    page_number = request.POST['page_number']
    user_keywords = keywords + class_1_keywords + class_2_keywords + class_3_keywords
    user_keywords = [word for word in user_keywords if bool(word)]
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
            bar_chart_data = []
            predictions = {}
            bar_data = {}
            for page_number in range(start_page, end_page + 1):
                generated_pdf = save_highlighted_page_as_pdf(file_path, page_number, user_keywords, image_path)
                generated_pdfs.append(generated_pdf)
                prediction, no_tech_keys, no_class1_keys, no_class2_keys, no_class3_keys = predict_class(file_path,
                                                                                                         page_number,
                                                                                                         user_keywords,
                                                                                                         keywords,
                                                                                                         class_1_keywords,
                                                                                                         class_2_keywords,
                                                                                                         class_3_keywords,
                                                                                                         nlp_model)
                predictions[page_number] = prediction
                bar_chart_data.append(
                    [page_number, no_tech_keys, no_class1_keys, no_class2_keys, no_class3_keys, prediction])

            cols = ['page', 'no_of_tech_keys', 'no_of_preliminary_keys', 'no_of_implementation_keys',
                    'no_of_advanced_keys', 'prediction']
            bar_df = pd.DataFrame(bar_chart_data, columns=cols)
            bar_data['Articles'] = len(bar_df['page'])
            bar_data['Tech keywords'] = bar_df['no_of_tech_keys'].sum()
            bar_data['Preliminary keywords'] = bar_df['no_of_preliminary_keys'].sum()
            bar_data['Implementation keywords'] = bar_df['no_of_implementation_keys'].sum()
            bar_data['Advanced keywords'] = bar_df['no_of_advanced_keys'].sum()
            merged_pdf_path = os.path.join(image_path, 'merged_highlighted_pages.pdf')
            merge_pdfs(generated_pdfs, merged_pdf_path)
            output_pages = {"classification": predictions[page_number],
                            "keywords": set(user_keywords),
                            "output_pdf_path": merged_pdf_path,
                            "bar_data": bar_data}
            return output_pages
        else:
            # Handle the case when only a single page is given
            bar_data = {}
            bar_chart_data = []
            page_number = int(page_number)
            generated_pdf = save_highlighted_page_as_pdf(file_path, page_number, user_keywords, image_path)
            prediction, no_tech_keys, no_class1_keys, no_class2_keys, no_class3_keys = predict_class(file_path,
                                                                                                         page_number,
                                                                                                         user_keywords,
                                                                                                         keywords,
                                                                                                         class_1_keywords,
                                                                                                         class_2_keywords,
                                                                                                         class_3_keywords,
                                                                                                         nlp_model)

            bar_chart_data.append(
                    [page_number, no_tech_keys, no_class1_keys, no_class2_keys, no_class3_keys, prediction])

            cols = ['page', 'no_of_tech_keys', 'no_of_preliminary_keys', 'no_of_implementation_keys',
                    'no_of_advanced_keys', 'prediction']
            bar_df = pd.DataFrame(bar_chart_data, columns=cols)
            bar_data['Articles'] = len(bar_df['page'])
            bar_data['Tech keywords'] = bar_df['no_of_tech_keys'].sum()
            bar_data['Preliminary keywords'] = bar_df['no_of_preliminary_keys'].sum()
            bar_data['Implementation keywords'] = bar_df['no_of_implementation_keys'].sum()
            bar_data['Advanced keywords'] = bar_df['no_of_advanced_keys'].sum()
            output_pages = {"classification": prediction,
                            "keywords": set(user_keywords),
                            "output_pdf_path": generated_pdf,
                            "bar_data": bar_data}
            return output_pages

    else:
        start_page = 0
        end_page = get_total_pages(file_path)
        predictions = {}
        bar_chart_data = []
        bar_data={}
        for page_number in range(start_page, end_page):
            generated_pdf = save_highlighted_page_as_pdf(file_path, page_number, user_keywords, image_path)
            generated_pdfs.append(generated_pdf)
            prediction, no_tech_keys, no_class1_keys, no_class2_keys, no_class3_keys = predict_class(file_path,
                                                                                                     page_number,
                                                                                                     user_keywords,
                                                                                                     keywords,
                                                                                                     class_1_keywords,
                                                                                                     class_2_keywords,
                                                                                                     class_3_keywords,
                                                                                                     nlp_model)
            predictions[page_number] = prediction
            bar_chart_data.append(
                [page_number, no_tech_keys, no_class1_keys, no_class2_keys, no_class3_keys, prediction])

        cols = ['page', 'no_of_tech_keys', 'no_of_preliminary_keys', 'no_of_implementation_keys', 'no_of_advanced_keys',
                'prediction']
        bar_df = pd.DataFrame(bar_chart_data, columns=cols)
        #bar_df['total_no_of_articles'] = len(bar_df['page'])
        #bar_df['total_no_of_techkeys'] = bar_df['no_of_tech_keys'].sum()
        #bar_df['total_no_of_preliminary_keys'] = bar_df['no_of_preliminary_keys'].sum()
        #bar_df['total_no_of_implementation_keys'] = bar_df['no_of_implementation_keys'].sum()
        #bar_df['total_no_of_advanced_keys'] = bar_df['no_of_advanced_keys'].sum()
        bar_data['Articles'] = len(bar_df['page'])
        bar_data['Tech keywords'] = bar_df['no_of_tech_keys'].sum()
        bar_data['Preliminary keywords'] = bar_df['no_of_preliminary_keys'].sum()
        bar_data['Implementation keywords'] = bar_df['no_of_implementation_keys'].sum()
        bar_data['Advanced keywords'] = bar_df['no_of_advanced_keys'].sum()
        merged_pdf_path = os.path.join(image_path, 'merged_highlighted_pages.pdf')
        merge_pdfs(generated_pdfs, merged_pdf_path)
        output_pages = {"classification": predictions[page_number],
                        "keywords": set(user_keywords),
                        "output_pdf_path": merged_pdf_path,
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
