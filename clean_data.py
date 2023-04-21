import re


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