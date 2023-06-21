import csv
import os
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials


def importer_google(spreadsheet_name: str, person_email: Optional[str] = None,
                    credential_json_file: Optional[str] = None):
    if person_email is None:
        person_email = 'jackson.barreto@gmail.com'
    if credential_json_file is None:
        credential_json_file = "google-credential.json"

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credential_json_file, scopes=scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.create(spreadsheet_name)
    email = person_email
    spreadsheet.share(email, perm_type='user', role='writer')
    # Configurar a região para EUA
    # Isso pode ser feito manualmente nas configurações da planilha, pois é uma configuração única.

    spreadsheet = client.open(spreadsheet_name)

    base_path = '../analyzes/tables/'

    csv_files = []

    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith('_combined.csv'):
                    csv_files.append(os.path.join(folder_path, file_name))

    for i, csv_file in enumerate(csv_files):
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            data = list(csv_reader)

        num_rows = len(data)
        num_cols = len(data[0]) if data else 0
        worksheet_title = os.path.basename(csv_file).split('_by')[0]
        worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows=num_rows, cols=num_cols)

        spreadsheet.values_update(
            worksheet_title,
            params={'valueInputOption': 'RAW'},
            body={'values': data}
        )
        worksheet.freeze(rows=1)

        # Configurar colunas como do tipo número
        # Isso pode ser feito através da interface da web, pois a gspread não suporta a formatação de células diretamente.

        worksheet.set_basic_filter()

    first_worksheet = spreadsheet.get_worksheet(0)
    first_worksheet.update_title("General Results")

    regions = []
    file_name = os.path.join(base_path, 'https/https_by_region_combined.csv')
    with open(file_name, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            regions.append(row[0])

    regions = sorted(regions[:-1])

    data = [
        ["Region", "DNSSEC", "ssl_algorithms", "key_length", "worst_ssl", "valid_ssl", "https", "security_headers", "",
         "SCORE", "", "PESOS"]
    ]

    for i, region in enumerate(regions, start=2):
        data.append([
            region,
            f'=VLOOKUP(A{i}, dnssec!$A:$C, 2, FALSE)',
            f'=VLOOKUP(A{i}, ssl_algorithms!$A:$B, 2, FALSE)',
            f'=VLOOKUP(A{i}, key_length!$A:$B, 2, FALSE)',
            f'=VLOOKUP(A{i}, worst_ssl_supported!$A:$B, 2, FALSE)',
            f'=VLOOKUP(A{i}, valid_ssl!$A:$B, 2, FALSE)',
            f'=VLOOKUP(A{i}, https!$A:$B, 2, FALSE)',
            f'=VLOOKUP(A{i}, security_headers!$A:$B, 2, FALSE)',
            '',
            f'=(B{i}*$M$2)+(C{i}*$M$3)+(D{i}*$M$4)+(E{i}*$M$5)+(F{i}*$M$6)+(G{i}*$M$7)+(H{i}*$M$8)'
        ])

    range_name = f'A1:L{len(regions) + 1}'

    spreadsheet.values_update(
        f'General Results!{range_name}',
        params={'valueInputOption': 'USER_ENTERED'},
        body={'values': data}
    )

    additional_content = [
        ["DNSSEC", 0.2],
        ["ssl_algorithms", 0.1],
        ["key_length", 0.1],
        ["worst_ssl", 0.2],
        ["ssl_valid", 0.1],
        ["https", 0.2],
        ["security_headers", 0.1]
    ]

    spreadsheet.values_update(
        'General Results!L2:M8',
        params={'valueInputOption': 'RAW'},
        body={'values': additional_content}
    )


if __name__ == '__main__':
    importer_google(spreadsheet_name='HEIs Polish')
