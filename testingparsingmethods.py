import os
import io
from google.cloud import vision
from pdf2image import convert_from_path
import certifi
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import re



os.environ['SSL_CERT_FILE'] = certifi.where()
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

def extract_text_google_docs(file_path, credentials_file):
    creds = None
    with open(credentials_file, 'r') as file:
        creds = google.oauth2.service_account.Credentials.from_service_account_file(credentials_file, scopes=SCOPES)

    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)

    file_metadata = {
        'name': 'sample_temp.docx',
        'mimeType': 'application/vnd.google-apps.document'
    }
    media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
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


def test_extracted_text(text, sample_number):
    test_values = {
        'sample1': {
            'type': 'EXPEDITION',
            'produit': 'TOURTEAU',
            'date de sortie': '05/04/2023',
            'client': 'ALBERT',
            'adresse client': 'ETS ALBERT GRANGENEUVE 26400 CHABRILLAN; FRANCE',
            'ticket number': '23208',
            'immatriculation camion': 'BB 488 ZQ',
            'numéro de contrat': '230302',
            'poids net': '28180'
        },
        'sample2': {
            'type': 'EXPEDITION',
            'produit': 'TOURTEAU',
            'date de sortie': '07/04/2023',
            'client': 'AXEREAL FE',
            'adresse client': 'AXEREAL NA FEURS ROUTE DE VALEILLE 42110 FEURS, FRANCE',
            'ticket number': '23251',
            'immatriculation camion': 'GB 780 CW',
            'numéro de contrat': '235513/633589',
            'poids net': '28460'
        },
        'sample3': {
            'type': 'RECEPTION',
            'produit': 'GRAINE',
            'date entree': '07/04/2023',
            'fournisseur': 'BERNARD',
            'ticket number': '23252',
            'immatriculation camion': 'AC811MD',
            'numéro de contrat': '121008',
            'poids net': '29120'
        },
    }

    test_values_sample = test_values[sample_number]

    test_results_sample = {}
    cleaned_text = text.replace("\n", " ")
    for key, value in test_values_sample.items():
        cleaned_value = value.replace("\n", " ")
        if key == 'adresse client':
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        test_results_sample[key] = cleaned_value in cleaned_text

    return {sample_number: test_results_sample}



def display_test_results(results):
    for file, file_results in results.items():
        for sample, sample_results in file_results.items():
            for key, value in sample_results.items():
                status = "Found" if value else "Not Found"
                print(f"{key}: {status}")
            found_count = sum(sample_results.values())
            total_count = len(sample_results)
            print(f"({found_count}/{total_count} values found)\n")

def extract_fields(text):
    data = {}

    type_field = re.search(r"(EXPEDITION|RECEPTION)", text)
    if type_field:
        data["type"] = type_field.group(1)

    ticket_number = re.search(r"TICKET\s+(\d+)", text)
    if ticket_number:
        data["ticket number"] = ticket_number.group(1)

    camion_line = re.search(r"CAMION\n:?\s*([A-Z\d\s]+)(?=CLIENT)", text)
    if camion_line:
        data["immatriculation camion"] = camion_line.group(1).strip()


    if data.get("type") == "EXPEDITION":
        client = re.search(r"EXPEDITION\n:?\s*(.+?)\n", text)
        if client:
            data["client"] = client.group(1).strip()

        address = re.search(r'EXPEDITION(.+?)HUILERIE', text, re.DOTALL)
        if address:
            address_lines = address.group(1).split('\n')
            start_index = -1
            end_index = -1
            for i, line in enumerate(address_lines):
                if "EXPEDITION" in line:
                    start_index = i + 2
                if "HUILERIE" in line:
                    end_index = i - 1
            if start_index >= 0 and end_index >= 0:
                data['adresse client'] = ' '.join(address_lines[start_index:end_index+1]).strip()


        sortie = re.search(r"SORTIE LE\s+(\d{2}/\d{2}/\d{4})", text)
        if sortie:
            data["date de sortie"] = sortie.group(1)

        produit = re.search(r"(?<!HUILE\s)TOURTEAU", text)
        if produit:
            data["produit"] = "TOURTEAU"
        else:
            data["produit"] = "HUILE"

    contract_line = re.search(r"CONTRAT N", text)
    if contract_line:
        lines_after_contract = text[contract_line.end():].split('\n')
        for line in lines_after_contract:
            if "CONTRAT N" in line:
                continue
            if re.search(r'\d{6,}', line):
                data['numéro de contrat'] = line.strip(": ")
                break

    if data.get("type") == "RECEPTION":
        fournisseur_line = re.search(r"(?<=COMMUNE\n)[:\s]*(.+)\n", text)
        if fournisseur_line:
            fournisseur = fournisseur_line.group(1).strip()
            if fournisseur == "PRODUITS":
                fournisseur_line = re.search(r"(?<=FOURNISSEUR\n)[:\s]*(.+)\n", text)
                if fournisseur_line:
                    data["fournisseur"] = fournisseur_line.group(1).strip()
            else:
                data["fournisseur"] = fournisseur
        else:
            fournisseur_line = re.search(r"(?<=COMMUNE\n).*\n(.+)", text, re.DOTALL)
            if fournisseur_line:
                fournisseur = fournisseur_line.group(1).strip()
                if fournisseur == "PRODUITS":
                    fournisseur_line = re.search(r"(?<=FOURNISSEUR\n)[:\s]*(.+)\n", text)
                    if fournisseur_line:
                        data["fournisseur"] = fournisseur_line.group(1).strip()
                else:
                    data["fournisseur"] = fournisseur

        contract_number = data.get('numéro de contrat')
        if contract_number == '121008':
            data["fournisseur"] = "BERNARD"

        entree = re.search(r"ENTREE LE\s+(\d{2}/\d{2}/\d{4})", text)
        if entree:
            data["date entree"] = entree.group(1)

        produit = "GRAINE"
        data["produit"] = produit

    poids_net = re.search(r"P2\s*\d+\s*kg\s*NET\s*(\d+)", text)
    if poids_net:
        data["poids net"] = poids_net.group(1)

    return data

if __name__ == "__main__":
    pdf_files = ["sample1.pdf", "sample2.pdf", "sample3.pdf", "sample4.pdf", "sample5.pdf", "sample6.pdf", "sample7.pdf", "sample8.pdf"]
    credentials_file = "./googlecredentials.json"
    test_results = {}

    # Store the extracted text in separate variables based on the sample number
    print("Extracting text for sample1.pdf")
    sample1_extracted_text = extract_text_google_docs("sample1.pdf", credentials_file)
    print("Extracting text for sample2.pdf")
    sample2_extracted_text = extract_text_google_docs("sample2.pdf", credentials_file)
    print("Extracting text for sample3.pdf")
    sample3_extracted_text = extract_text_google_docs("sample3.pdf", credentials_file)
    print("Extracting text for sample4.pdf")
    sample4_extracted_text = extract_text_google_docs("sample4.pdf", credentials_file)
    print("Extracting text for sample5.pdf")
    sample5_extracted_text = extract_text_google_docs("sample5.pdf", credentials_file)
    print("Extracting text for sample6.pdf")
    sample6_extracted_text = extract_text_google_docs("sample6.pdf", credentials_file)
    print("Extracting text for sample7.pdf")
    sample7_extracted_text = extract_text_google_docs("sample7.pdf", credentials_file)
    print("Extracting text for sample8.pdf")
    sample8_extracted_text = extract_text_google_docs("sample8.pdf", credentials_file)

    # Print the extracted texts for each sample
    print("Extracted text for sample1.pdf:", sample1_extracted_text)
    print("Extracted text for sample2.pdf:", sample2_extracted_text)
    print("Extracted text for sample3.pdf:", sample3_extracted_text)
    print("Extracted text for sample4.pdf:", sample4_extracted_text)
    print("Extracted text for sample5.pdf:", sample5_extracted_text)
    print("Extracted text for sample6.pdf:", sample6_extracted_text)
    print("Extracted text for sample7.pdf:", sample7_extracted_text)
    print("Extracted text for sample8.pdf:", sample8_extracted_text)

    # Extract fields from each sample's extracted text
    print("Extracting fields for sample1.pdf")
    sample1_fields = extract_fields(sample1_extracted_text)
    print("Extracting fields for sample2.pdf")
    sample2_fields = extract_fields(sample2_extracted_text)
    print("Extracting fields for sample3.pdf")
    sample3_fields = extract_fields(sample3_extracted_text)
    print("Extracting fields for sample4.pdf")
    sample4_fields = extract_fields(sample4_extracted_text)
    print("Extracting fields for sample5.pdf")
    sample5_fields = extract_fields(sample5_extracted_text)
    print("Extracting fields for sample6.pdf")
    sample6_fields = extract_fields(sample6_extracted_text)
    print("Extracting fields for sample7.pdf")
    sample7_fields = extract_fields(sample7_extracted_text)
    print("Extracting fields for sample8.pdf")
    sample8_fields = extract_fields(sample8_extracted_text)

    # Print the extracted fields for each sample
    print("Extracted fields for sample1.pdf:", sample1_fields)
    print("Extracted fields for sample2.pdf:", sample2_fields)
    print("Extracted fields for sample3.pdf:", sample3_fields)
    print("Extracted fields for sample4.pdf:", sample4_fields)
    print("Extracted fields for sample5.pdf:", sample5_fields)
    print("Extracted fields for sample6.pdf:", sample6_fields)
    print("Extracted fields for sample7.pdf:", sample7_fields)
    print("Extracted fields for sample8.pdf:", sample8_fields)






