from flask import Flask, request, send_file
import pandas as pd
import os
from io import BytesIO
import smtplib
from email.message import EmailMessage


app = Flask(__name__)

DATA_DIRECTORY = "./data"  # Directory where XLSX files are stored

sender_email = "srujan.int@niveussolutions.com"
sender_password = "rmlh ikej rtmz ejme"
subject = "Compute Calculation Results"
body = "Please find the attached file for the results of the computation."


def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, file_path):
    try:
        
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.set_content(body)

        
        with open(file_path, 'rb') as file:
            file_data = file.read()
            file_name = file_path.split('/')[-1]  # Get the file name from the path
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

       
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def consolidate_xlsx():
    file1_path = os.path.join(DATA_DIRECTORY, "file1.xlsx")
    file2_path = os.path.join(DATA_DIRECTORY, "file2.xlsx")
    
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        return {'error': 'One or both files do not exist'}, 400
    
    if not file1_path.endswith('.xlsx') or not file2_path.endswith('.xlsx'):
        return {'error': 'Only .xlsx files are allowed'}, 400
    
    df1 = pd.read_excel(file1_path, sheet_name=None)  # Read all sheets
    df2 = pd.read_excel(file2_path, sheet_name=None)  # Read all sheets
    
    output_path = os.path.join(DATA_DIRECTORY, "output.xlsx")
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    
    # Writing sheets from first file
    for sheet_name, df in df1.items():
        df.to_excel(writer, sheet_name=f"file1-{sheet_name}", index=False)
    
    # Writing sheets from second file
    for sheet_name, df in df2.items():
        df.to_excel(writer, sheet_name=f"file2-{sheet_name}", index=False)
    
    writer.close()
    




@app.route('/consolidate', methods=['POST'])
def home():
    sheet = request.form.get('sheet')
    email = request.form.get('email')
    consolidate_xlsx()
    send_email_with_attachment(sender_email, sender_password,email,subject,body,"data/output.xlsx")
    os.remove
    return "process completed and mailed",200


if __name__ == '__main__':
    app.run(debug=True)
