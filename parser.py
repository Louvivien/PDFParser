import os
import io
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from io import BytesIO
import fitz  
import shutil
import shlex
import ghostscript
from PIL import Image
import torch
from PIL import Image
from torchvision import transforms
import glob

from define_template import open_pdf_and_define_coordinates, save_template
from img_transform import pdf_to_images
from clean_data import clean_extracted_data



# First, deactivate your current virtual environment:
# deactivate
# python3.9 -m venv venv39
# source venv39/bin/activate
# pip install PyMuPDF numpy tensorflow tensorflow-io-gcs-filesystem easyocr torchvision opencv-python-headless
# pip install matplotlib google-api-python-client PyPDF2 ghostscript pdf2image

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


# For the manual writing, we extract it with a trained model
def extract_text_torch_hub(image, multiple_rectangles):
        # https://huggingface.co/spaces/baudm/PARSeq-OCR
    # Load model and image transforms
    print(f"multiple boxes: {multiple_rectangles}")
    if multiple_rectangles[0]:
        model_name='parseq_tiny'
    else:
        model_name='vitstr'
    print(f"model name: {model_name}")    
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
    if multiple_rectangles[0]:
        print(label[0])
        return label[0]
    else:
        print(raw_label[0][0])
        return raw_label[0][0]



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

    # Extract the manual writing field using extract_text_torch_hub
    # The model for torch_hub is different if there are several objects detected
    if 'Silos' in file_paths:
        images_as_bytes, multiple_rectangles = pdf_to_images(file_paths['Silos'])
        extracted_texts = []
        for image in images_as_bytes:
            extracted_texts.append(extract_text_torch_hub(image, multiple_rectangles))
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
    # pdf_file = "./data/sample6.pdf"
    pdf_file = "./data/test/TP23347.pdf"
    file_path = "./data/sample.xlsx"
    template_file = "template.json"
    credentials_file = "googlecredentials.json"
    main(pdf_file, template_file, credentials_file)


# def main(pdf_files, template_file, credentials_file):
#     all_extracted_data = {}

#     for pdf_file in pdf_files:
#         print(f"Processing {pdf_file}")
        
#         template = load_template(template_file)
#         output_pdfs = split_pdf(pdf_file, template)
#         file_paths = save_pdfs_to_files(output_pdfs)
#         uploaded_files = upload_to_google_drive(credentials_file, file_paths)
#         doc_ids = convert_to_google_docs(credentials_file, uploaded_files)
#         extracted_data = extract_content_from_google_docs(credentials_file, doc_ids)

#         if 'Silos' in file_paths:
#             images_as_bytes, multiple_rectangles = pdf_to_images(file_paths['Silos'])
#             extracted_texts = []
#             for image in images_as_bytes:
#                 extracted_texts.append(extract_text_torch_hub(image, multiple_rectangles))
#             flat_list = [item for sublist in extracted_texts for item in sublist]
#             extracted_data['Silos'] = ' '.join(flat_list)

#         cleaned_extracted_data = clean_extracted_data(extracted_data)
#         all_extracted_data[pdf_file] = cleaned_extracted_data

#         delete_files_from_google_drive(credentials_file, uploaded_files)

#     return all_extracted_data

# if __name__ == "__main__":
#     test_directory = "./data/test/"
#     pdf_files = glob.glob(os.path.join(test_directory, "*.pdf"))
#     template_file = "template.json"
#     credentials_file = "googlecredentials.json"
#     extracted_data = main(pdf_files, template_file, credentials_file)

#     print("\nExtracted Data:")
#     for pdf_file, data in extracted_data.items():
#         print(f"File: {pdf_file}")
#         for name, text in data.items():
#             print(f"{name}: {text}")
#         print()



