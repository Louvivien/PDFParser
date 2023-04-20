import json
import io
import os
import sys
import re
import fitz  
import matplotlib.pyplot as plt
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from io import BytesIO
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.generic import RectangleObject
import tempfile
import shutil
import shlex
import ghostscript
from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.imagenet_utils import preprocess_input

import cv2
from sklearn.cluster import KMeans


import torch
from PIL import Image
from torchvision import transforms




# First, deactivate your current virtual environment:
# deactivate
# python3.9 -m venv venv39
# source venv39/bin/activate
# pip install PyMuPDF numpy tensorflow tensorflow-io-gcs-filesystem easyocr torchvision opencv-python-headless
# pip install matplotlib google-api-python-client PyPDF2 ghostscript pdf2image


# Define a template on the PDF
def open_pdf_and_define_coordinates(pdf_file):
    print("Opening PDF viewer...")
    print("Click on two points to define a rectangular field (top-left corner and bottom-right corner).")

    coordinates = []
    field_names = []

    def on_click(event):
        nonlocal coordinates
        x, y = event.xdata, event.ydata
        print(f"Clicked at {x}, {y}")
        coordinates.append((x, y))
        if len(coordinates) % 2 == 0:
            print("Two points selected.")
            field_name = input("Enter field name: ")
            field_names.append(field_name)
            print("Press 'Enter' to finish or 'c' to continue adding fields.")
            action = input()
            if action.lower() == 'c':
                print("Click on two points to define the next rectangular field.")
            else:
                plt.close()

    doc = fitz.open(pdf_file)
    page = doc[0]
    zoom = 4
    mat = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=mat)
    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        pixmap.save(temp_file.name, "png")
        image = plt.imread(temp_file.name)

    fig, ax = plt.subplots()
    ax.imshow(image)
    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.show()

    if len(coordinates) % 2 != 0:
        print("Error: Odd number of clicks. Exiting.")
        sys.exit(1)

    fields = []
    for i in range(len(coordinates) // 2):
        x1, y1 = coordinates[2 * i]
        x2, y2 = coordinates[2 * i + 1]
        x = min(x1, x2) / zoom
        y = min(y1, y2) / zoom
        w = abs(x1 - x2) / zoom
        h = abs(y1 - y2) / zoom
        fields.append(
            {"name": field_names[i],
             "coordinates": {"x": x, "y": y, "w": w, "h": h}}
        )
    return {"fields": fields}


def save_template(template, template_file):
    with open(template_file, "w") as f:
        json.dump(template, f, indent=4)
def load_template(template_file):
    with open(template_file, 'r') as f:
        template = json.load(f)
    return template

def destructive_crop(file_path):
    command = f'gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="{file_path}.pdf" "{file_path}"'
    ghostscript.Ghostscript(*shlex.split(command))
    shutil.move(f"{file_path}.pdf", file_path)

# Split the original pdf in several pdfs based on the fields
def split_pdf(pdf_file, template):
    with fitz.open(pdf_file) as input_pdf:
        output_pdfs = {}
        for field in template["fields"]:
            x, y, w, h = field["coordinates"].values()
            x, y, w, h = int(x), int(y), int(w), int(h)

            output_pdf = fitz.open()
            input_page = input_pdf.load_page(0)
            cropped_rect = fitz.Rect(x, y, x + w, y + h)

            output_page = output_pdf.new_page(width=w, height=h)
            output_page.show_pdf_page(output_page.rect, input_pdf, 0, clip=cropped_rect)

            output_stream = BytesIO()
            output_pdf.save(output_stream)
            print(f"Cropped {field['name']} page with coordinates {x}, {y}, {w}, {h}")

            # Save the cropped PDF temporarily
            temp_file_path = f"./temp_{field['name']}.pdf"
            with open(temp_file_path, "wb") as f:
                f.write(output_stream.getvalue())

            # Perform destructive crop and save back to the memory buffer
            destructive_crop(temp_file_path)
            with open(temp_file_path, "rb") as f:
                output_stream = BytesIO(f.read())

            # Delete the temporary file
            os.remove(temp_file_path)

            output_pdfs[field["name"]] = output_stream

    return output_pdfs



def save_pdfs_to_files(output_pdfs):
    file_paths = {}
    pdf_directory = "./PDF"
    if not os.path.exists(pdf_directory):
        os.mkdir(pdf_directory)
    for name, output_pdf in output_pdfs.items():
        output_pdf.seek(0)
        file_path = f"{pdf_directory}/{name}.pdf"
        with open(file_path, "wb") as f:
            f.write(output_pdf.getvalue())
        file_paths[name] = file_path
    return file_paths

# We will upload the files to google drive
def upload_to_google_drive(credentials_file, file_paths):
    print("Uploading files to Google Drive...")
    creds = service_account.Credentials.from_service_account_file(credentials_file)
    service = build("drive", "v3", credentials=creds)
    uploaded_files = {}
    for name, file_path in file_paths.items():
        file_metadata = {"name": f"{name}.pdf", "mimeType": "application/pdf"}
        media = MediaFileUpload(file_path, mimetype="application/pdf")
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        uploaded_files[name] = file["id"]
    print("Files uploaded to Google Drive.")
    return uploaded_files


def delete_files_from_google_drive(credentials_file, file_ids):
    print("Deleting files from Google Drive...")
    creds = service_account.Credentials.from_service_account_file(credentials_file)
    service = build("drive", "v3", credentials=creds)
    for file_id in file_ids.values():
        try:
            service.files().delete(fileId=file_id).execute()
        except HttpError as error:
            print(f"An error occurred: {error}")
    print("Files deleted from Google Drive.")

# We will open the files with Google Docs
def convert_to_google_docs(credentials_file, file_ids):
    print("Converting PDFs to Google Docs format...")
    creds = service_account.Credentials.from_service_account_file(credentials_file)
    service = build("drive", "v3", credentials=creds)
    doc_ids = {}
    for name, file_id in file_ids.items():
        file_metadata = {
            "name": f"{name}.gdoc",
            "mimeType": "application/vnd.google-apps.document",
            "parents": [{"id": file_id}],
        }
        file = (
            service.files()
            .copy(fileId=file_id, body=file_metadata, fields="id")
            .execute()
        )
        doc_ids[name] = file["id"]
    print("PDFs converted to Google Docs format.")
    return doc_ids

# We will extract the text from Google Docs
def extract_content_from_google_docs(credentials_file, doc_ids):
    print("Extracting content from Google Docs...")
    creds = service_account.Credentials.from_service_account_file(credentials_file)
    service = build("docs", "v1", credentials=creds)
    extracted_data = {}
    for name, doc_id in doc_ids.items():
        doc = service.documents().get(documentId=doc_id).execute()
        content = doc.get("body", {}).get("content", [])
        text = ""
        for item in content:
            if "paragraph" in item:
                elements = item["paragraph"]["elements"]
                for element in elements:
                    if "textRun" in element:
                        text += element["textRun"]["content"]
        extracted_data[name] = text.strip()
    print("Content extracted from Google Docs.")
    return extracted_data

# For the manual writing, we will convert it to image
def pdf_to_images(pdf_file):
    images = convert_from_path(pdf_file)

    images_as_bytes = []

    for image in images:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        
        cropped_image_path = "./temp_cropped_image.jpeg"
        with open("temp_image.jpeg", "wb") as f:
            f.write(img_bytes.getvalue())
        crop_central_line("temp_image.jpeg", cropped_image_path)
        # os.remove("temp_image.jpeg")

        with open(cropped_image_path, "rb") as f:
            cropped_img_bytes = f.read()
        # os.remove(cropped_image_path)

        images_as_bytes.append(cropped_img_bytes)

    return images_as_bytes

# For the manual writing, we will crop it
def crop_central_line(image_path, output_path, padding=5, debug=False):
    # Load the image using OpenCV
    img = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to create a mask
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours in the binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Calculate the bounding boxes of the contours
    bounding_boxes = [cv2.boundingRect(cnt) for cnt in contours]

    # Calculate the y-coordinate of the center of each bounding box
    centers_y = [y + h//2 for _, y, _, h in bounding_boxes]

    # Apply k-means clustering to group the elements based on their y-coordinate centers
    kmeans = KMeans(n_clusters=3, n_init=10, random_state=0).fit(np.array(centers_y).reshape(-1, 1))

    # Find the cluster labels and sort them based on the cluster centers
    sorted_labels = sorted(range(3), key=lambda i: kmeans.cluster_centers_[i])

    if len(sorted_labels) == 2:
        # If there are only 2 clusters, assume the central line is the one with the highest y-coordinate (i.e., the second line)
        median_label = sorted_labels[1]
    else:
        # Otherwise, find the cluster label corresponding to the median y-coordinate
        median_label = sorted_labels[1]

    # Get the bounding boxes belonging to the central line
    central_line_bboxes = [bbox for bbox, label in zip(bounding_boxes, kmeans.labels_) if label == median_label]

    # Save an image with bounding boxes drawn for debugging
    if debug:
        img_with_bboxes = img.copy()
        for x, y, w, h in central_line_bboxes:
            cv2.rectangle(img_with_bboxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite('./test/debug_image_with_bboxes.jpeg', img_with_bboxes)

    # Find the minimum and maximum x-coordinates and y-coordinates of the elements in the central line
    min_x = min([x for x, _, _, _ in central_line_bboxes])
    max_x = max([x + w for x, _, w, _ in central_line_bboxes])
    min_y = min([y for _, y, _, _ in central_line_bboxes])
    max_y = max([y + h for _, y, _, h in central_line_bboxes])

    # Extract the corresponding region with optional padding
    cropped_img = img[min_y - padding:max_y + padding, min_x - padding:max_x + padding]

    # Save the cropped image
    cv2.imwrite(output_path, cropped_img)


# For the manual writing, we extract it with a trained model
def extract_text_torch_hub(image, model_name='vitstr'):
        # https://huggingface.co/spaces/baudm/PARSeq-OCR
    # Load model and image transforms
    parseq = torch.hub.load('baudm/parseq', model_name, pretrained=True).eval()
    img_transform = transforms.Compose([
    transforms.Resize(parseq.hparams.img_size),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
    ])

    # Convert image to RGB if needed
    image = Image.open(io.BytesIO(image))
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Preprocess. Model expects a batch of images with shape: (B, C, H, W)
    img = img_transform(image).unsqueeze(0)

    logits = parseq(img)
    # logits.shape  # torch.Size([1, 26, 95]), 94 characters + [EOS] symbol

    # Greedy decoding
    pred = logits.softmax(-1)
    label, confidence = parseq.tokenizer.decode(pred)
    raw_label, raw_confidence = parseq.tokenizer.decode(pred, raw=True)
    # Format confidence values
    max_len = 25 if model_name == 'crnn' else len(label[0]) + 1
    conf = list(map('{:0.1f}'.format, raw_confidence[0][:max_len].tolist()))
    print(f"output: {label[0]} raw_confidence:{[raw_label[0][:max_len], conf]}")
    print(raw_label[0][0])
    return label[0]


def clean_extracted_data(extracted_data):

    cleaned_data = {}

    for field, text in extracted_data.items():

        if field == "Numero contrat":
            cleaned_text = re.sub(r'(?<![0-9a-zA-Z])\W(?![0-9a-zA-Z])', '', text)

        elif field == "Poids net":
            cleaned_text = ''.join(re.findall(r'\d', text))[:5]

        elif field == "Date de sortie" or field == "Date entree":
            cleaned_text = re.search(r'\d{2}/\d{2}/\d{4}', text)
            if cleaned_text:
                cleaned_text = cleaned_text.group(0)
            else:
                cleaned_text = ""

        elif field == "Produit":
            cleaned_text = text.split()[0]

        elif field == "Type":
            cleaned_text = "RECEPTION" if re.search(r'ЕСЕРТІON', text, re.IGNORECASE) else text

        elif field == "Ticket number":
            cleaned_text = ''.join(re.findall(r'\d', text))[:5]

        else:
            cleaned_text = text

        cleaned_data[field] = cleaned_text

    return cleaned_data

# Get the data into Excel
  


def main(pdf_file, template_file, credentials_file):
    # template = open_pdf_and_define_coordinates(pdf_file)
    # save_template(template, template_file)

    template = load_template(template_file)
    output_pdfs = split_pdf(pdf_file, template)
    file_paths = save_pdfs_to_files(output_pdfs)
    uploaded_files = upload_to_google_drive(credentials_file, file_paths)
    doc_ids = convert_to_google_docs(credentials_file, uploaded_files)
    extracted_data = extract_content_from_google_docs(credentials_file, doc_ids)

    # Extract the Silos field using extract_text_torch_hub
    if 'Silos' in file_paths:
        images_as_bytes = pdf_to_images(file_paths['Silos'])
        extracted_texts = []
        for image in images_as_bytes:
            extracted_texts.append(extract_text_torch_hub(image))
        flat_list = [item for sublist in extracted_texts for item in sublist]
        extracted_data['Silos'] = ' '.join(flat_list)


    cleaned_extracted_data = clean_extracted_data(extracted_data)


    # print("Deleting local PDF files...")
    # pdf_directory = "./PDF"
    # for file_name in os.listdir(pdf_directory):
    #     file_path = os.path.join(pdf_directory, file_name)
    #     try:
    #         if os.path.isfile(file_path):
    #             os.remove(file_path)
    #     except Exception as e:
    #         print(f"Error deleting {file_path}: {e}")
    # print("Local PDF files deleted.")

    delete_files_from_google_drive(credentials_file, uploaded_files)

    print("\nExtracted Data:")
    for name, text in cleaned_extracted_data.items():
        print(f"{name}: {text}")




if __name__ == "__main__":
    pdf_file = "./data/sample6.pdf"
    file_path = "./data/sample.xlsx"
    template_file = "template.json"
    credentials_file = "googlecredentials.json"
    main(pdf_file, template_file, credentials_file)



