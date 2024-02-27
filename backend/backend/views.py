from django.shortcuts import render
import json
import os
import uuid
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from rest_framework.decorators import api_view
from backend.util import get_text_from_files, preprocess_text, extract_keywords_nltk, get_model
from backend.process_pdf_files import save_highlighted_page_as_image

pickle_file_path = r'/Users/revanthgottuparthy/Desktop/NLP project/DocumentClassifier-NLP/backend/backend/model/nlp_model.pkl'
image_path = r'/Users/revanthgottuparthy/Desktop/NLP project/DocumentClassifier-NLP/backend/backend/images'
def predict_class(file_path, page_number,user_keywords, model):
    text = get_text_from_files(file_path, page_number)
    new_document_keywords = extract_keywords_nltk(preprocess_text(text), user_keywords)
    predicted_class = model.predict([new_document_keywords])
    return predicted_class

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
    page_number = request.POST['page_number']
    user_keywords = keywords+class_1_keywords+class_2_keywords+class_3_keywords
    user_keywords = [word for word in user_keywords if bool(word)]
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))

    file_name = str(uuid.uuid4().hex[:15].upper()) + ".pdf"
    folder_path = os.path.join(APP_ROOT, 'uploads')
    FileSystemStorage(folder_path).save(file_name, pdf_file)
    file_path = os.path.join(folder_path, file_name)

    outimg_path = save_highlighted_page_as_image(file_path,page_number,user_keywords,image_path)
    nlp_model = get_model(pickle_file_path)
    prediction = predict_class(file_path, page_number, user_keywords, nlp_model)

    with open(outimg_path, 'rb') as f:
        image_data = f.read()

    additional_data = {
        'param1': 'value1',
        'param2': 'value2',
    }

    output_val = {
        "classification": prediction,
        "keywords": set(user_keywords),
        "image_path": outimg_path,
        'image_data': image_data.decode('latin-1')
    }

    return output_val


@api_view(['POST'])
def main_api(request):
    if request.method == 'POST':
        output = handle_upload(request)

        return Response(output)
