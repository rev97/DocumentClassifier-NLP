import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import os

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


def save_highlighted_page_as_image(pdf_path, page_number, keywords, output_path):
    doc = fitz.open(pdf_path)

    try:
        page = doc.load_page(int(page_number) - 1)  # Page numbers are 0-based in PyMuPDF
    except IndexError:
        print(f"Error: Page {page_number} not found in the PDF.")
        return

    highlighted_img = highlight_keywords(page, keywords)
    pdf_file_name = os.path.basename(pdf_path)
    highlighted_img.save(os.path.join(output_path,pdf_file_name)+str("_")+str(page_number)+".jpg")
    print(f"Highlighted image saved to {output_path}")
    return os.path.join(output_path,pdf_file_name)+str("_")+str(page_number)+".jpg"

