import os
import io
import cv2
import re
import numpy as np
import torch
from PIL import Image
import requests
import json
import easyocr
from google.cloud import vision
from pdf2image import convert_from_path, convert_from_bytes
from pytesseract import image_to_string
from pytesseract import pytesseract
import certifi
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.imagenet_utils import preprocess_input

import torch
from PIL import Image
from torchvision import transforms




# First, deactivate your current virtual environment:
# deactivate
# python3.9 -m venv venv39
# source venv39/bin/activate
# pip install PyMuPDF numpy tensorflow tensorflow-io-gcs-filesystem easyocr torchvision opencv-python-headless
# pip install torch Pillow requests google-cloud-vision pdf2image pytesseract google-auth google-auth-oauthlib google-auth-httplib2

# AttributeError: module 'tqdm' has no attribute 'auto'
# I apologize for the inconvenience. It seems the issue still persists. As a workaround, you can try modifying the problematic file directly. The file is located at:
# /Users/vivien/Documents/PDFparser/venv39/lib/python3.9/site-packages/torchmetrics/functional/text/bert.py
# Find the following line (line 247):
# def _get_progress_bar(dataloader: DataLoader, verbose: bool = False) -> Union[DataLoader, tqdm.auto.tqdm]:
# Replace it with:
# def _get_progress_bar(dataloader: DataLoader, verbose: bool = False) -> Union[DataLoader, tqdm.tqdm]:
# Save the file and try running your code again. This should resolve the AttributeError. If you encounter any other issues or have questions, please let me know.



model_path = './models/model22.h5'
model = tf.keras.models.load_model(model_path)


os.environ['SSL_CERT_FILE'] = certifi.where()
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']


def extract_text_from_pdf(pdf_file):
    pdf_file = open(pdf_file, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    pdf_file.close()
    return text



def pdf_to_images(pdf_file):
    images = convert_from_path(pdf_file)

    images_as_bytes = []

    for image in images:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        images_as_bytes.append(img_bytes.getvalue())

    return images_as_bytes


def preprocess_image(image, target_size):
    image = Image.fromarray(image).convert('L')  
    image = image.resize(target_size[:2], Image.ANTIALIAS)  
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = image.astype('float32')
    image /= 255
    return image

def process_output(prediction):
    digit_index = np.argmax(prediction, axis=1)
    return str(digit_index[0])






def extract_text_tesseract(pdf_file):
    images = convert_from_path(pdf_file)
    all_text = ""
    for image in images:
        text = image_to_string(image)
        all_text += text + '\n' if text else ""
    return all_text


def extract_text_easyocr(pdf_file):
    reader = easyocr.Reader(['en'])
    images = convert_from_path(pdf_file)
    all_text = ""
    for image in images:
        np_image = np.array(image)
        text = reader.readtext(np_image, detail=0)
        all_text += ' '.join(text) + '\n' if text else ""
    return all_text



def extract_text_google_vision(pdf_file):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./googlecredentials.json"

    client = vision.ImageAnnotatorClient()
    images = convert_from_path(pdf_file)
    all_text = ""
    for image in images:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        vision_image = vision.Image(content=img_byte_arr)
        response = client.document_text_detection(image=vision_image)
        text = response.full_text_annotation.text
        all_text += text + '\n' if text else ""
    return all_text

def extract_text_azure_vision(pdf_file, subscription_key, endpoint):
    ocr_url = endpoint + "vision/v3.2/ocr"

    images = convert_from_path(pdf_file)
    all_text = ""

    for image in images:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()

        headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
        params = {'language': 'en', 'detectOrientation': 'true'}
        response = requests.post(ocr_url, headers=headers, params=params, data=img_byte_arr)
        response.raise_for_status()
        analysis = response.json()

        for region in analysis["regions"]:
            for line in region["lines"]:
                words = [word["text"] for word in line["words"]]
                all_text += " ".join(words) + '\n'

    return all_text

def test_extracted_text(text):
    test_values = {
        'produit': 'TOURTEAU',
        'date de sortie': '05/04/2023',
        'client': 'ALBERT',
        'client adresse': 'ETS ALBERT GRANGENEUVE 26400 CHABRILLAN; FRANCE',
        'ticket number': '23208',
        'immatriculation camion': 'BB 488 ZQ',
        'numéro de contrat': '230302',
        'poids net': '28180'
    }

    test_results = {}
    for key, value in test_values.items():
        test_results[key] = value in text

    return test_results

def display_test_results(results):
    for method, method_results in results.items():
        found_count = sum(value for value in method_results.values())
        total_count = len(method_results)
        print(f"\n{method} ({found_count}/{total_count} values found):")
        for key, value in method_results.items():
            status = "Found" if value else "Not found"
            print(f"{key}: {status}")


def extract_text_google_docs(pdf_file, credentials_file):
    creds = None
    with open(credentials_file, 'r') as file:
        creds = google.oauth2.service_account.Credentials.from_service_account_file(credentials_file, scopes=SCOPES)

    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)

    file_metadata = {
        'name': 'sample1_temp.docx',
        'mimeType': 'application/vnd.google-apps.document'
    }
    media = MediaFileUpload(pdf_file, mimetype='application/pdf', resumable=True)
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    doc_id = uploaded_file.get('id')

    doc = docs_service.documents().get(documentId=doc_id).execute()

    drive_service.files().delete(fileId=doc_id).execute()

    all_text = ""
    for content in doc.get('body').get('content'):
        if 'paragraph' in content:
            elements = content.get('paragraph').get('elements')
            for element in elements:
                if 'textRun' in element:
                    all_text += element.get('textRun').get('content')

    return all_text



def read_structural_elements(elements):
    text = ''
    for element in elements:
        if 'paragraph' in element:
            elements = element.get('paragraph').get('elements')
            for elem in elements:
                text_run = elem.get('textRun')
                if text_run:
                    text += text_run.get('content')
        elif 'table' in element:
            table = element.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                text += read_structural_elements(cells)
        elif 'tableCell' in element:
            text += read_structural_elements(element.get('tableCell').get('content'))
    return text

def extract_text_custom_model(pdf_file, model, target_size=(28, 28, 1)):
    images = convert_from_path(pdf_file)
    all_text = ""

    for image in images:
        np_image = np.array(image)
        preprocessed_image = preprocess_image(np_image, target_size=target_size)
        prediction = model.predict(preprocessed_image)
        text = process_output(prediction)
        all_text += text + '\n' if text else ""

    return all_text




def extract_text_torch_hub(image, model_name='vitstr'):
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
    logits.shape  # torch.Size([1, 26, 95]), 94 characters + [EOS] symbol

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




def test_models(pdf_file, model_files, target_value='4'):
    successful_models = []
    tested_models_count = 0

    for model_file in model_files:
        try:
            model = tf.keras.models.load_model(model_file)
            extracted_text_custom_model = extract_text_custom_model(pdf_file, model)

            # Check if the target_value is present as a standalone number
            if re.search(rf'\b{target_value}\b', extracted_text_custom_model):
                successful_models.append(model_file)
            
            tested_models_count += 1
        except Exception as e:
            print(f"Error with {model_file}: {e}")

    return successful_models, tested_models_count


if __name__ == "__main__":
    pdf_file = "./test/sample8_Silos.pdf"
    model_files = [f'./models/model{i}.h5' for i in range(1, 49)]
    


    subscription_key = "198fad436c244970a2e2e666e083f698"
    endpoint = "https://pdfparse.cognitiveservices.azure.com/"
    credentials_file = "./googlecredentials.json"



      # Convert the PDF file to a list of images
    pdf_images = pdf_to_images(pdf_file)

    # Extract text from each image using Torch Hub
    extracted_text_torch_hub = ""
    for pdf_image in pdf_images:
        extracted_text_torch_hub += extract_text_torch_hub(pdf_image) + "\n"


    # successful_models, tested_models_count = test_models(pdf_file, model_files, target_value='4')


    extracted_text_tesseract = extract_text_tesseract(pdf_file)
    extracted_text_easyocr = extract_text_easyocr(pdf_file)
    extracted_text_google_vision = extract_text_google_vision(pdf_file)
    extracted_text_azure_vision = extract_text_azure_vision(pdf_file, subscription_key, endpoint)
    extracted_text_google_docs = extract_text_google_docs(pdf_file, credentials_file)
    extracted_text_custom_model = extract_text_custom_model(pdf_file, model)


    # test_results = {
    #     'pytesseract': test_extracted_text(extracted_text_tesseract),
    #     'easyocr': test_extracted_text(extracted_text_easyocr),
    #     'google_vision': test_extracted_text(extracted_text_google_vision),
    #     'azure_vision': test_extracted_text(extracted_text_azure_vision),
    #     'custom_model': test_extracted_text(extracted_text_custom_model),
    #     'google_docs': test_extracted_text(extracted_text_google_docs)

    # }

    print("\nExtracted text using pytesseract (OCR):")
    print(extracted_text_tesseract)

    print("\nExtracted text using easyocr:")
    print(extracted_text_easyocr)

    print("\nExtracted text using Google Cloud Vision API:")
    print(extracted_text_google_vision)

    print("\nExtracted text using Azure OCR:")
    print(extracted_text_azure_vision)

    print("\nExtracted text using Google Docs:")
    print(extracted_text_google_docs)

    print("\nExtracted text using Custom TensorFlow model:")
    print(extracted_text_custom_model)

    print("\nExtracted text using Torch Hub (Pretrained Model):")
    print(extracted_text_torch_hub)

    # print(f"Total models tested: {tested_models_count}")
    # print("Models that returned the target value:")
    # for model_file in successful_models:
    #     print(model_file)

    # print("\nTest results for all methods:")
    # display_test_results(test_results)
