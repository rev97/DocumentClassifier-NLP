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
from backend.backend.model_training_api import handle_training_request
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render
from backend.backend.settings import REDIS_URL
import os
import redis
from rq import Queue

conn = redis.from_url(REDIS_URL)

@api_view(['POST'])
def main_api(request):
    if len(request.FILES) == 0:
        return Response({"error": "No files are uploaded"}, status=400)

    if 'file' not in request.FILES:
        return Response({"error": "'file' field missing in form-data"}, status=400)

    pdf_file = request.FILES['file']
    keywords = request.POST['keywords']
    has_page_range = request.POST['has_page_range']
    use_trained_model = request.POST['Use Trained Model']
    page_number = request.POST['page_number']
    user_model_file = request.FILES.get('model_file', None)

    APP_ROOT = os.path.dirname(os.path.abspath(__file__))

    file_name = str(uuid.uuid4().hex[:15].upper()) + ".pdf"
    folder_path = os.path.join(APP_ROOT, 'uploads')
    FileSystemStorage(folder_path).save(file_name, pdf_file)
    file_path = os.path.join(folder_path, file_name)

    # Enqueue the background job
    q = Queue(connection=conn)
    job = q.enqueue('tasks.handle_upload_task', file_path, folder_path, keywords, has_page_range, use_trained_model, page_number, user_model_file)
    return Response({"job_id": job.id}, status=202)

@api_view(['POST'])
def check_task_status(request):
    job_id = request.POST['job_id']
    queue = Queue('default',connection=conn)
    job = queue.fetch_job(job_id)

    if job is None:
        return Response({"error": "Job not found"}, status=404)

    if job.is_finished:
        return Response({"status": "finished", "result": job.result}, status=200)
    elif job.is_failed:
        return Response({"status": "failed", "error": str(job.exc_info)}, status=500)
    else:
        return Response({"status": "in progress"}, status=200)



@api_view(['POST'])
def model_training_api(request):
    if request.method == 'POST':
        output = handle_training_request(request)

        return Response(output)


@xframe_options_exempt
@api_view(['GET'])
def get_trained_model(request):
    model_path = request.GET.get('path', '')
    model_full_path = f'{model_path}'

    try:
        with open(model_full_path, 'rb') as model_file:
            # Determine the appropriate content type based on the file extension
            content_type = 'application/octet-stream'  # Default to generic binary

            # Set specific content type based on file extension if known
            if model_full_path.endswith('.pkl'):
                content_type = 'application/octet-stream'  # Example for pickle files

            # Prepare response with binary data
            response = HttpResponse(model_file.read(), content_type=content_type)

            # Set Content-Disposition to attachment to force download
            response['Content-Disposition'] = f'attachment; filename="{model_full_path}"'
            return response

    except FileNotFoundError:
        return HttpResponse(status=404)  # File not found response
    except Exception as e:
        return HttpResponse(status=500)  # Internal server error response

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