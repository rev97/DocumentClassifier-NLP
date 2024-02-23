from django.shortcuts import render
import json
import os
import uuid
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from rest_framework.decorators import api_view


def handle_upload(request):
    if len(request.FILES) == 0:
        raise Exception("No files are uploaded")

    if 'file' not in request.FILES:
        raise Exception("'video' field missing in form-data")

    pdf_file = request.FILES['file']

    keywords = request.POST['keywords']

    APP_ROOT = os.path.dirname(os.path.abspath(__file__))

    file_name = str(uuid.uuid4().hex[:15].upper()) + ".pdf"
    folder_path = os.path.join(APP_ROOT, 'uploads')

    file_path = os.path.join(folder_path, file_name)
    FileSystemStorage(folder_path).save(file_name, pdf_file)
    # video.save(path)
    print("video saved")

    # do analysis

    # os.remove(file_path)
    print(file_path + " stored")
    # return analysis

    output_val = {
        "classification": "preliminary",
        "keywords": str(keywords).split(",")
    }

    return output_val


@api_view(['POST'])
def main_api(request):
    if request.method == 'POST':
        output = handle_upload(request)

        return Response(output)
