import fitz  # PyMuPDF
from PIL import Image, ImageDraw
from PyPDF2 import PdfMerger
from fpdf import FPDF
import os
import boto3
from datetime import datetime, timedelta
import requests

# Initialize AWS S3 client
s3 = boto3.client('s3')

# Bucket name
bucket_name = 'nlppdffiles'


# Function to upload a file to S3
def upload_to_s3(file_path, file_name):
    try:
        # Upload the file to S3
        with open(file_path, 'rb') as f:
            s3.upload_fileobj(f, bucket_name, file_name, ExtraArgs={'ContentType': 'application/pdf'})
        print(f"File uploaded to S3: s3://{bucket_name}/{file_name}")

        # Generate a signed URL for the uploaded file
        expiration_time = datetime.now() + timedelta(days=1)  # Expiration time of 1 day
        signed_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': file_name}, ExpiresIn=86400)
        print(f"Signed URL for the file: {signed_url}")

        return signed_url
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return None

def upload_pickle_to_s3(file_path, file_name):
    try:
        # Upload the pickle file to S3
        with open(file_path, 'rb') as f:
            s3.upload_fileobj(f, bucket_name, file_name, ExtraArgs={'ContentType': 'application/octet-stream'})
        print(f"File uploaded to S3: s3://{bucket_name}/{file_name}")

        # Generate a signed URL for the uploaded file
        expiration_time = datetime.now() + timedelta(days=1)  # Expiration time of 1 day
        signed_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': file_name}, ExpiresIn=86400)
        print(f"Signed URL for the file: {signed_url}")

        return signed_url
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return None

def download_pdf_from_s3(s3_presigned_url):
    # Extract file name from URL
    file_name = os.path.basename(s3_presigned_url)

    # Send GET request to S3 presigned URL
    response = requests.get(s3_presigned_url)

    # Check if request was successful
    if response.status_code == 200:
        # Save file to the current directory
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return True, file_name  # Return success and file name
    else:
        return False, None  # Return failure

def get_total_pages(pdf_path):
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)

        # Get the total number of pages
        total_pages = pdf_document.page_count

        # Close the PDF document
        pdf_document.close()

        return total_pages

    except Exception as e:
        print(f"Error: {e}")
        return None


def highlight_keywords(page, keywords):
    # Convert PDF page to image
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Use Pillow to draw on the image
    draw = ImageDraw.Draw(img)

    for keyword in keywords:
        # Highlight each keyword in red
        locations = page.search_for(keyword)
        for loc in locations:
            # Accessing Rect attributes directly
            rect = loc
            draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], outline="red")

    return img

def convert_image_to_pdf(image_path, output_pdf_path):
    # Open the image using PIL (Pillow)
    img = Image.open(image_path)

    # Create a PDF document
    pdf = FPDF(orientation='P', unit='mm', format='A4')

    # Add a page to the PDF
    pdf.add_page()

    # Get image dimensions
    img_width, img_height = img.size

    # Calculate the aspect ratio to fit the image within the PDF page
    aspect_ratio = img_width / img_height

    # Set the width and height based on the aspect ratio
    pdf_width = 210  # A4 width in mm
    pdf_height = pdf_width / aspect_ratio

    # Add the image to the PDF
    pdf.image(image_path, x=10, y=10, w=pdf_width-20, h=pdf_height-20)

    # Output the PDF to a file
    pdf.output(output_pdf_path)


def save_highlighted_page_as_image(pdf_path, page_number, keywords, output_path):
    doc = fitz.open(pdf_path)

    try:
        page = doc.load_page(int(page_number) - 1)  # Page numbers are 0-based in PyMuPDF
    except IndexError:
        print(f"Error: Page {page_number} not found in the PDF.")
        return

    highlighted_img = highlight_keywords(page, keywords)
    pdf_file_name = os.path.basename(pdf_path)
    img_path = os.path.join(output_path, f"{pdf_file_name}_highlighted_{page_number}.jpg")

    # Save the highlighted image
    highlighted_img.save(img_path, "JPEG")

    return img_path


def save_highlighted_page_as_pdf(pdf_path, page_number, keywords, output_path):
    doc = fitz.open(pdf_path)

    try:
        page = doc.load_page(int(page_number) - 1)  # Page numbers are 0-based in PyMuPDF
    except IndexError:
        print(f"Error: Page {page_number} not found in the PDF.")
        return

    highlighted_img = highlight_keywords(page, keywords)
    pdf_file_name = os.path.basename(pdf_path)
    img_path = os.path.join(output_path, f"{pdf_file_name}_highlighted_{page_number}.jpg")
    pdf_path = img_path.replace('.jpg', '.pdf')

    # Save the highlighted image
    highlighted_img.save(img_path, "JPEG")

    # Convert the image to PDF
    convert_image_to_pdf(img_path, pdf_path)

    print(f"Highlighted PDF saved to {pdf_path}")

    # Delete the intermediate image file
    os.remove(img_path)

    return pdf_path

def merge_pdfs(input_pdfs, files_path):
    pdf_merger = PdfMerger()

    for pdf_path in input_pdfs:
        pdf_merger.append(pdf_path)

    # Generate a unique name for the output PDF file based on the current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_pdf_file = f"{current_datetime}.pdf"
    output_pdf_path = os.path.join(files_path, output_pdf_file)

    # Write the merged PDF with the timestamped filename
    pdf_merger.write(output_pdf_path)
    pdf_merger.close()

    # Upload the merged PDF to S3
    s3_file_url = upload_to_s3(output_pdf_path, output_pdf_file)

    # Delete intermediate PDF files
    for pdf_path in input_pdfs:
        os.remove(pdf_path)

    return s3_file_url