from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import time
import os
import pandas as pd
import re
import csv
import glob
import json
import smtplib
from email.message import EmailMessage
import requests
from flask import Flask, request,jsonify
import pyperclip

pyautogui.FAILSAFE = False


app=Flask(__name__)

process_status = {}


index_file = "assets/index.json"



input_file = "data/sheet.csv"  # Replace with your input file path


output_file_filtered = "data/output.csv" 
input_filtered_file="data/output.csv"


output_file = "data/output_results.csv"

sender_email = "srujan.int@niveussolutions.com"
sender_password = "rmlh ikej rtmz ejme"
subject = "Compute Calculation Results"
body = "Please find the attached file for the results of the computation."
file_path = "output_results.xlsx"


with open('assets/knowledge_base.json', 'r') as kb_file:
    knowledge_base = json.load(kb_file)

os_mapping = {
    r"win(dows)?": "Paid: Windows Server",
    r"rhel\s*7": "Paid: Red Hat Enterprise Linux 7 with Extended Life Cycle Support",
    r"rhel\s*sap": "Paid: Red Hat Enterprise Linux for SAP with HA and Update Services",
    r"rhel": "Paid: Red Hat Enterprise Linux",
    r"ubuntu\s*pro": "Paid: Ubuntu Pro",
    r"ubuntu": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"debian": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"sql-web": "Paid: SQL Server Web",  
    r"sql-enterprise": "Paid: SQL Server Enterprise",
    r"sql-standard": "Paid: SQL Server Standard",
    r"free": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"sles(\s*12)?": "Paid: SLES 12 for SAP",
    r"sles(\s*15)?": "Paid: SLES 15 for SAP",
    r"sles": "Paid: SLES"
}

def map_os(value, os_mapping):
    """
    Matches an OS string against the predefined mapping.

    :param value: The OS string to match.
    :param os_mapping: The dictionary of regex patterns and corresponding OS labels.
    :return: The mapped OS label or a default value if no match is found.
    """
    if value.lower()=="sql-web":
        return "Paid: SQL Server Web"
    if value.lower()=="sql-enterprise":
        return "Paid: SQL Server Enterprise"
    if value.lower()=="sql-standard":
        return "Paid: SQL Server Standard"
    
    if value.lower()=="ubuntu-pro" or value.lower()=="ubuntu pro":
        return "Paid: Ubuntu Pro"
    
    if value.lower()=="win":
        return "Paid: Windows Server"
    else:
        value = value.lower().strip()  # Normalize case and remove extra spaces

        for pattern, replacement in os_mapping.items():
            if re.match(pattern, value, re.IGNORECASE):  # Allow partial match for broad patterns
                return replacement

        return "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL"  # Default fallback




def extract_sheet_id(sheet_url):
    pattern = r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, sheet_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Sheet URL")

def download_sheet(sheet_url):
        try:
            print("downloading the sheet !!")
            sheet_id = extract_sheet_id(sheet_url)
            tab_name = "ComputeEngine"
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={tab_name}"
            response = requests.get(csv_url)

            if response.status_code == 200:
                with open("data/sheet.csv", "wb") as f:
                    f.write(response.content)
                print("Google Sheet downloaded as sheet.csv")
                row_count = count_rows(file_path)
            else:
                print("Failed to download sheet. HTTP Status Code:", response.status_code)
        except ValueError as e:
            print(e)
        except Exception as e:
            print("An error occurred:", e)


def count_rows(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            return sum(1 for _ in reader) - 1  # Exclude header row
    except Exception as e:
        print("Error counting rows:", e)
        return 0


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



def map_value(value, knowledge_base):
    for key in knowledge_base:
        if re.search(rf"\b{re.escape(value)}\b", key, re.IGNORECASE):
            return key
    return value 

def process_csv(input_file, output_file):
    df = pd.read_csv(input_file)

    if 'OS with version' in df.columns:
        df['OS with version'] = df['OS with version'].apply(
            lambda x: map_os(str(x).strip(), os_mapping) if pd.notnull(x) else x
        )
        
        
    if 'Machine Family' in df.columns and (df["Machine Family"] == "Compute-optimized").any():
        
        if 'Series' in df.columns:
            df['Series'] = df['Series'].fillna("C2")

        if 'Machine Type' in df.columns and 'vCPUs' in df.columns:
            df['Machine Type'] = df['Machine Type'].fillna("custom") + "-" + df['vCPUs'].astype(str)
            
    
    
    

    else:
        if 'Machine Family' in df.columns:
            df['Machine Family'] = df['Machine Family'].fillna("general purpose")

        if 'Series' in df.columns:
            df['Series'] = df['Series'].fillna("E2")

        if 'Machine Type' in df.columns:
            df['Machine Type'] = df['Machine Type'].fillna("custom")

        columns_to_map = ["Machine Family", "Series", "Machine Type"]

        for column in columns_to_map:
            if column in df.columns:
                df[column] = df[column].apply(lambda x: map_value(str(x).strip(), knowledge_base) if pd.notnull(x) else x)

    
    df.to_csv(output_file, index=False)
    print("input file filtered")



def load_index(file_path):
    
    with open(file_path, 'r') as file:
        return json.load(file)


indices = load_index(index_file)


os_mapping = {
    r"win(dows)?": "Paid: Windows Server",
    r"rhel": "Paid: Red Hat Enterprise Linux",
    r"ubuntu": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"debian": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"sql": "Paid: SQL Server Standard",
    r"free" :"Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
}


os_options = {
    0: "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    1: "Paid: Ubuntu Pro",
    2: "Paid: Windows Server",
    3: "Paid: Red Hat Enterprise Linux",
    4: "Paid: Red Hat Enterprise Linux 7 with Extended Life Cycle Support",
    5: "Paid: Red Hat Enterprise Linux for SAP with HA and Update Services",
    6: "Paid: SLES",
    7: "Paid: SLES 12 for SAP",
    8: "Paid: SLES 15 for SAP",
    9: "Paid: SQL Server Standard",
    10: "Paid: SQL Server Web",
    11: "Paid: SQL Server Enterprise",
}



def get_os_index(os_name):
    """Get the index of the OS based on its name."""
    for regex, mapped_name in os_mapping.items():
        if pd.notna(os_name) and re.search(regex, os_name, re.IGNORECASE):
            for index, name in os_options.items():
                if name == mapped_name:
                    return index
    return None

def get_index(variable_name, indices):
    
    return indices.get(variable_name, 0)
   
    
def home_page(driver,actions):
        """Navigates to the pricing section."""
        driver.implicitly_wait(5)
        add_to_estimate_button = driver.find_element(By.XPATH, "//span[text()='Add to estimate']")
        add_to_estimate_button.click()
        time.sleep(5)
        div_element = driver.find_element(By.XPATH, "//div[@class='d5NbRd-EScbFb-JIbuQc PtwYlf' and @data-service-form='8']")
        actions.move_to_element(div_element).click().perform()
        time.sleep(2)
        print("✅ home page done")

def handle_instance(driver,actions,no_of_instance,hours_per_day):
    hours_status=False
    
    for _ in range(6):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    if hours_per_day < 5 and hours_per_day > 0:
        actions.send_keys(Keys.ENTER).perform()
        hours_status=True
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    if hours_status==True:
        no_of_instance=int(no_of_instance)
        print(no_of_instance)
        #pyautogui.write(formatted_number, interval=0.8)  # Adds a slight delay for accuracy
        actions.send_keys(no_of_instance).perform() 
    else:
        no_of_instance=float(no_of_instance)
        formatted_number=f"{no_of_instance:.2f}"
        print(formatted_number)
        #pyautogui.write(formatted_number, interval=0.8)  # Adds a slight delay for accuracy
        actions.send_keys(formatted_number).perform()
    
    
        
        
        
    for _ in range(4):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    print("Instance handled")


def handle_hours_per_day(driver,actions,hours_per_day):
    if hours_per_day==730:
        for _ in range(3):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        print("✅ default hours handled")
        pass
        
    else:
        actions.send_keys(hours_per_day).perform()
        time.sleep(1)
        for _ in range(3):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        print("✅ Hours handled")


def handle_os(driver,actions,os_index,os_name):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Operating System / Software')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite(os_name)
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("✅ os selected")
    
    
    
def handle_machine_family(driver,actions,machine_family_index,machine_family):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Machine Family')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite(machine_family)
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("✅ machine family selected")


def handle_series(driver,actions,series_index,series):
    time.sleep(0.6)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite(series)
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.TAB).perform()
    print("✅ machine series selected")
    
    
def handle_machine_type(driver,actions,machine_type,machine_type_index):
    
    
    time.sleep(0.6)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite(machine_type)
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("✅ machine type selected")
    
def extended_mem_toggle_on(driver,actions):
    time.sleep(0.6)
    
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Extended memory')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.ENTER).perform()
    print("✅ extension toggle turned on")
    
    
       
 
def handle_vcpu_and_memory(driver,actions,vCPU,ram):
    print(vCPU)
    print(ram)
    time.sleep(0.6)
    
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Number of vCPUs')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
        
        
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.3)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.3)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.3)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.6)

    actions.send_keys(Keys.BACKSPACE).perform()
    
    time.sleep(0.6)
    actions.send_keys(vCPU).perform()
    time.sleep(0.6)
    
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Amount of memory')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    
    time.sleep(0.6)
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
        
   
    time.sleep(0.6)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.BACKSPACE).perform() 
    time.sleep(0.5)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.3)
    actions.send_keys(Keys.BACKSPACE).perform() 
    time.sleep(0.3)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.3)
    actions.send_keys(Keys.BACKSPACE).perform() 
    time.sleep(0.3)



    pyautogui.write(str(ram), interval=0.1)
    pyautogui.press("enter")

  
    print("✅ vpcu and ram selected")
    
    
  
def boot_disk_type(driver,actions):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Boot disk type')
    time.sleep(0.6)
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.TAB).perform()
    actions.send_keys(Keys.TAB).perform()   
    
    print("✅ Boot Disk Type handled")

def boot_disk_capacitys(driver,actions,boot_disk_capacity):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Boot disk size')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    actions.send_keys(Keys.ENTER).perform()
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
   
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.6)
    pyautogui.typewrite(str(boot_disk_capacity))
    time.sleep(0.6)
    actions.send_keys(Keys.TAB).perform()
    actions.send_keys(Keys.TAB).perform()
    print("✅ boot disk capacity entered")
   


def select_region(driver, actions, region):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Region')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite(region)
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("✅ Region selected")


def get_price_with_js(driver):
    
    try:
        js_script = """
        const element = document.querySelector('span.MyvX5d.D0aEmf');
        return element ? element.textContent.trim() : null;
        """
        price_text = driver.execute_script(js_script)
        
        if price_text and price_text.startswith("$"):
            print("✅ price extracted")
            return price_text
        elif price_text:
            print("❌ Invalid price format")
            return "Invalid price format"
        else:
            print("❌ Price element not found")
            return "Price element not found"
    
    except JavascriptException as e:
        return f"An unexpected JavaScript error occurred: {str(e)}"


def move_to_region(driver,actions,moves):
    pass
    


def sud_toggle_on(driver,actions):
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Add sustained use discounts')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.ENTER).perform()
    print("✅ Sud turned on")

def one_year_selection(driver,actions):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Committed use discount options')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    actions.send_keys(Keys.ARROW_RIGHT).perform()
    actions.send_keys(Keys.ENTER).perform()
    print("✅ one year selected")




def three_year_selection(driver,actions):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Committed use discount options')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    actions.send_keys(Keys.ARROW_RIGHT).perform()
    time.sleep(0.2)
    actions.send_keys(Keys.ARROW_RIGHT).perform()
    time.sleep(0.2)
    actions.send_keys(Keys.ENTER).perform()
    print("✅ three year selected")
 
 
def handle_machine_class(driver,actions,machine_class): 
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Provisioning Model')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    if machine_class=='preemptible':
        actions.send_keys(Keys.ARROW_RIGHT).perform()
        actions.send_keys(Keys.ENTER).perform()
        print("✅ machine class handled preemptible selected")
    else:
        print("✅ machine class handled regular selected")
        pass

def add_estimate(driver,actions):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Cost details')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)  
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    actions.send_keys(Keys.ENTER).perform()
    
        
def scrape_machine_type(driver,actions):
    time.sleep(0.6)
    element = driver.find_element(By.CLASS_NAME, "D3Zlgc.MyvX5d.D0aEmf")
    print("Extracted Content:", element.text)
    return element.text

def scrape_custom_machine_type(driver,actions):
    time.sleep(0.6)
    element = driver.find_element(By.CLASS_NAME, "HY0Uh")
    print("Extracted Content:", element.text)
    return element.text

def get_memory_limit(series, ram):
    ram_limits = {
        'N1': {
            2: 13, 4: 26, 6: 39, 8: 52, 10: 65, 12: 78, 14: 91, 16: 104, 18: 117, 20: 130,
            22: 143, 24: 156, 26: 169, 28: 182, 30: 195, 32: 208, 34: 221, 36: 234, 38: 247, 40: 260,
            42: 273, 44: 286, 46: 299, 48: 312, 50: 325, 52: 338, 54: 351, 56: 364, 58: 377, 60: 390,
            62: 403, 64: 416, 66: 429, 68: 442, 70: 455, 72: 468, 74: 481, 76: 494, 78: 507, 80: 520,
            82: 533, 84: 546, 86: 559, 88: 572, 90: 585, 92: 598, 94: 611, 96: 624
        },
        'N2': {
            2: 8, 4: 32, 6: 48, 8: 64, 10: 80, 12: 96, 14: 112, 16: 128, 18: 144, 20: 160,
            22: 176, 24: 192, 26: 208, 28: 224, 30: 240, 32: 256, 34: 272, 36: 288, 38: 304, 40: 320,
            42: 336, 44: 352, 46: 368, 48: 384, 50: 400, 52: 416, 54: 432, 56: 448, 58: 464, 60: 480,
            62: 496, 64: 512, 66: 528, 68: 544, 70: 560, 72: 576, 74: 592, 76: 608, 78: 624, 80: 640,
            82: 656, 84: 672, 86: 688, 88: 704, 90: 720, 92: 736, 94: 752, 96: 768, 98: 784, 100: 800,
            102: 816, 104: 832, 106: 848, 108: 864, 110: 864, 112: 864, 114: 864, 116: 864, 118: 864,
            120: 864, 122: 864, 124: 864, 126: 864, 128: 864
        },
        'N2D': {
            2: 16, 4: 32, 6: 48, 8: 64, 10: 80, 12: 96, 14: 112, 16: 128, 18: 144, 20: 160,
            22: 176, 24: 192, 26: 208, 28: 224, 30: 240, 32: 256, 34: 272, 36: 288, 38: 304, 40: 320,
            42: 336, 44: 352, 46: 368, 48: 384, 50: 400, 52: 416, 54: 432, 56: 448, 58: 464, 60: 480,
            62: 496, 64: 512, 66: 528, 68: 544, 70: 560, 72: 576, 74: 592, 76: 608, 78: 624, 80: 640,
            82: 656, 84: 672, 86: 688, 88: 704, 90: 720, 92: 736, 94: 752, 96: 768, 98: 784, 100: 800,
            102: 816, 104: 832, 106: 848, 108: 864, 110: 880, 112: 896, 114: 896, 116: 896, 118: 896,
            120: 896, 122: 896, 124: 896, 126: 896, 128: 896, 130: 896, 132: 896, 134: 896, 136: 896,
            138: 896, 140: 896, 142: 896, 144: 896, 146: 896, 148: 896, 150: 896, 152: 896, 154: 896,
            156: 896, 158: 896, 160: 896, 162: 896, 164: 896, 166: 896, 168: 896, 170: 896, 172: 896,
            174: 896, 176: 896, 178: 896, 180: 896, 182: 896, 184: 896, 186: 896, 188: 896, 190: 896,
            192: 896, 194: 896, 196: 896, 198: 896, 200: 896, 202: 896, 204: 896, 206: 896, 208: 896,
            210: 896, 212: 896, 214: 896, 216: 896, 218: 896, 220: 896, 222: 896, 224: 896
        }
    }
    
    fixed_memory_limits = {
        'N4': 16,
        'E2': 16
    }
    
    if series in fixed_memory_limits:
        return fixed_memory_limits[series]

    # Return the memory limit for the given RAM size
    return ram_limits.get(series, {}).get(ram, float('inf'))  




#=============================================================================================#
def get_on_demand_pricing( os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class):
    print(f"Getting on demand pricing: 🖥️ OS: {os_name}, 🔢 No. of Instances: {no_of_instances}, ⏳ Hours per Day: {hours_per_day}, "
      f"🛠️ Machine Family: {machine_family}, 📊 Series: {series}, 💻 Machine Type: {machine_type}, "
      f"⚙️ vCPU: {vCPU}, 🖥️ RAM: {ram} GB, 💾 Boot Disk Capacity: {boot_disk_capacity} GB, "
      f"🌍 Region: {region}, 🏷️ Machine Class: {machine_class}")
    os_index = get_os_index(os_name)
    machine_family_index = get_index(machine_family, indices)
    series_index = get_index(series, indices)
    machine_type_index = get_index(machine_type, indices)
    
    print(f"os index : {os_index},machine family : {machine_family_index},series index :{series_index},machine type index : {machine_type_index}")
    print(vCPU,ram)
    print("ondemand pricing")
    download_directory = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_directory, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    actions = ActionChains(driver)
    driver.get("https://cloud.google.com/products/calculator")
    driver.implicitly_wait(10)
    
    home_page(driver,actions)
    handle_instance(driver,actions,no_of_instances,hours_per_day)
    handle_hours_per_day(driver,actions,hours_per_day)
    #time.sleep(0.6)
    handle_machine_class(driver,actions,machine_class)
    
    handle_os(driver,actions,os_index,os_name)
    #time.sleep(0.6)
    handle_machine_family(driver,actions,machine_family_index,machine_family)
    #time.sleep(0.6)
    handle_series(driver,actions,series_index,series)
    #time.sleep(0.6)
    handle_machine_type(driver,actions,machine_type,machine_type_index)
    #time.sleep(0.6)
    
    if vCPU!=0:
        if (machine_family.lower() == "general purpose" and series in ["N1", "N2", "N4", "E2", "N2D"] and not (series == "N1" and machine_type in ["f1-micro", "g1-small"])):
                print(f"Calling handle_vcpu_and_memory Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
                ram_limits = {
                'N1': 13,
                'N2': 16,
                'N2D': 256,
                'N4': 16,
                'E2': 16
                }
                
                memory_limit = get_memory_limit(series, vCPU)

                if machine_type == 'custom' and ram > memory_limit:
                    extended_mem_toggle_on(driver,actions)
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                else:
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                
            
        elif machine_family.lower() == "accelerator optimized" and series == "G2":
                print(f"Calling handle_vcpu_and_memory  Machine Family: {machine_family}, Series: {series}")
                if machine_type=='custom':
                    #extended_mem_toggle_on(driver,actions)
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                else:
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
           
            
    else:
        print(f"Skipping handle_vcpu_and_memory: Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
    
    #time.sleep(0.6)
    boot_disk_type(driver,actions)
    #time.sleep(0.6)
    boot_disk_capacitys(driver,actions,boot_disk_capacity)    
    
    #time.sleep(0.6)

    

    select_region(driver,actions,region)
    
        
        
    
    time.sleep(10)
    
    current_url = driver.current_url
    
    price=get_price_with_js(driver)
    if machine_type=='custom':
       machine_type_data= scrape_custom_machine_type(driver,actions)
    else:
        machine_type_data=scrape_machine_type(driver,actions)
    
    print(price,current_url)
    
    driver.quit()
    print("✅ ondemand pricing done")
    
    return current_url, price,machine_type_data
    
    
    
    
    
    
def get_sud_pricing( os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class):
    print(f"Getting SUD pricing: 🖥️ OS: {os_name}, 🔢 No. of Instances: {no_of_instances}, ⏳ Hours per Day: {hours_per_day}, "
      f"🛠️ Machine Family: {machine_family}, 📊 Series: {series}, 💻 Machine Type: {machine_type}, "
      f"⚙️ vCPU: {vCPU}, 🖥️ RAM: {ram} GB, 💾 Boot Disk Capacity: {boot_disk_capacity} GB, "
      f"🌍 Region: {region}, 🏷️ Machine Class: {machine_class}")

    os_index = get_os_index(os_name)
    machine_family_index = get_index(machine_family, indices)
    series_index = get_index(series, indices)
    machine_type_index = get_index(machine_type, indices)
    
    print(f"os index : {os_index},machine family : {machine_family_index},series index :{series_index},machine type index : {machine_type_index}")
    print(vCPU,ram)
    print("sud pricing")
    download_directory = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_directory, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    actions = ActionChains(driver)
    driver.get("https://cloud.google.com/products/calculator")
    driver.implicitly_wait(10)
    
    home_page(driver,actions)
    handle_instance(driver,actions,no_of_instances,hours_per_day)
    #time.sleep(0.6)
    handle_hours_per_day(driver,actions,hours_per_day)
    #time.sleep(0.6)
    handle_machine_class(driver,actions,machine_class)
    
    handle_os(driver,actions,os_index,os_name)
    #time.sleep(0.6)
    handle_machine_family(driver,actions,machine_family_index,machine_family)
    #time.sleep(0.6)
    handle_series(driver,actions,series_index,series)
    #time.sleep(0.6)
    handle_machine_type(driver,actions,machine_type,machine_type_index)
    #time.sleep(0.6)
    
    if vCPU!=0:
        if (machine_family.lower() == "general purpose" and series in ["N1", "N2", "N4", "E2", "N2D"] and not (series == "N1" and machine_type in ["f1-micro", "g1-small"])):
                print(f"Calling handle_vcpu_and_memory Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
                ram_limits = {
                'N1': 256,
                'N2': 16,
                'N2D': 256,
                'N4': 16,
                'E2': 16
                }
                
                memory_limit = get_memory_limit(series, ram)

                if machine_type == 'custom' and ram > memory_limit:
                    extended_mem_toggle_on(driver,actions)
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                else:
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                
            
        elif machine_family.lower() == "accelerator optimized" and series == "G2":
                print(f"Calling handle_vcpu_and_memory  Machine Family: {machine_family}, Series: {series}")
                if machine_type=='custom':
                    #extended_mem_toggle_on(driver,actions)
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                else:
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
           
            
    else:
        print(f"Skipping handle_vcpu_and_memory: Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
    
    #time.sleep(0.6)
    boot_disk_type(driver,actions)
    #time.sleep(0.6)
    boot_disk_capacitys(driver,actions,boot_disk_capacity)    
    
    #time.sleep(2)

    sud_toggle_on(driver,actions)
    
    #time.sleep(2)
    select_region(driver,actions,region)
    
        
        
    
    time.sleep(10)
    
    current_url = driver.current_url
    
    price=get_price_with_js(driver)
    
    if machine_type=='custom':
           machine_type_data= scrape_custom_machine_type(driver,actions)
    else:
        machine_type_data=scrape_machine_type(driver,actions)
    print(price,current_url)
    
    driver.quit()
    print("✅ sud pricing done")
    
    return current_url, price, machine_type_data
    
    
def get_one_year_pricing(os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class):
    print(f"Getting one year pricing: 🖥️ OS: {os_name}, 🔢 No. of Instances: {no_of_instances}, ⏳ Hours per Day: {hours_per_day}, "
      f"🛠️ Machine Family: {machine_family}, 📊 Series: {series}, 💻 Machine Type: {machine_type}, "
      f"⚙️ vCPU: {vCPU}, 🖥️ RAM: {ram} GB, 💾 Boot Disk Capacity: {boot_disk_capacity} GB, "
      f"🌍 Region: {region}, 🏷️ Machine Class: {machine_class}")

    os_index = get_os_index(os_name)
    machine_family_index = get_index(machine_family, indices)
    series_index = get_index(series, indices)
    machine_type_index = get_index(machine_type, indices)
    
    print(f"os index : {os_index},machine family : {machine_family_index},series index :{series_index},machine type index : {machine_type_index}")
    print(vCPU,ram)
    print("one year pricing")
    download_directory = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_directory, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    actions = ActionChains(driver)
    driver.get("https://cloud.google.com/products/calculator")
    driver.implicitly_wait(10)
    
    home_page(driver,actions)
    handle_instance(driver,actions,no_of_instances,hours_per_day)
    #time.sleep(0.6)
    handle_hours_per_day(driver,actions,hours_per_day)
    #time.sleep(0.6)
    handle_machine_class(driver,actions,machine_class)
    
    handle_os(driver,actions,os_index,os_name)
    #time.sleep(0.6)
    handle_machine_family(driver,actions,machine_family_index,machine_family)
    #time.sleep(0.6)
    handle_series(driver,actions,series_index,series)
    #time.sleep(0.6)
    handle_machine_type(driver,actions,machine_type,machine_type_index)
    #time.sleep(0.6)
    
    if vCPU!=0:
        if (machine_family.lower() == "general purpose" and series in ["N1", "N2", "N4", "E2", "N2D"] and not (series == "N1" and machine_type in ["f1-micro", "g1-small"])):
                print(f"Calling handle_vcpu_and_memory Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
                
                ram_limits = {
                'N1': 256,
                'N2': 16,
                'N2D': 256,
                'N4': 16,
                'E2': 16
                }
                
                memory_limit = get_memory_limit(series, ram)

                if machine_type == 'custom' and ram > memory_limit:
                    extended_mem_toggle_on(driver,actions)
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                else:
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                
            
        elif machine_family.lower() == "accelerator optimized" and series == "G2":
                print(f"Calling handle_vcpu_and_memory  Machine Family: {machine_family}, Series: {series}")
                if machine_type=='custom':
                    #extended_mem_toggle_on(driver,actions)
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                else:
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
           
            
        else:
            print(f"Skipping handle_vcpu_and_memory: Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
    
    #time.sleep(0.6)
    boot_disk_type(driver,actions)
    #time.sleep(0.6)
    boot_disk_capacitys(driver,actions,boot_disk_capacity)    
    
    #time.sleep(0.6)

    

    select_region(driver,actions,region)
    
    #time.sleep(0.6)
    
    one_year_selection(driver,actions)  
        
    
    time.sleep(10)
    
    current_url = driver.current_url
    
    price=get_price_with_js(driver)
    if machine_type=='custom':
           machine_type_data= scrape_custom_machine_type(driver,actions)
    else:
      machine_type_data=scrape_machine_type(driver,actions)
     
    print(price,current_url)
    
    driver.quit()
    print("✅ one year pricing done")
    
    return current_url, price , machine_type_data

def  get_three_year_pricing(os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class):
    print(f"Getting three year pricing: 🖥️ OS: {os_name}, 🔢 No. of Instances: {no_of_instances}, ⏳ Hours per Day: {hours_per_day}, "
      f"🛠️ Machine Family: {machine_family}, 📊 Series: {series}, 💻 Machine Type: {machine_type}, "
      f"⚙️ vCPU: {vCPU}, 🖥️ RAM: {ram} GB, 💾 Boot Disk Capacity: {boot_disk_capacity} GB, "
      f"🌍 Region: {region}, 🏷️ Machine Class: {machine_class}")

    os_index = get_os_index(os_name)
    machine_family_index = get_index(machine_family, indices)
    series_index = get_index(series, indices)
    machine_type_index = get_index(machine_type, indices)
    
    print(f"os index : {os_index},machine family : {machine_family_index},series index :{series_index},machine type index : {machine_type_index}")
    print(vCPU,ram)
    print("three year  pricing")
    download_directory = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_directory, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    actions = ActionChains(driver)
    driver.get("https://cloud.google.com/products/calculator")
    driver.implicitly_wait(10)
    
    home_page(driver,actions)
    handle_instance(driver,actions,no_of_instances,hours_per_day)
    #time.sleep(0.6)
    handle_hours_per_day(driver,actions,hours_per_day)
    
    handle_machine_class(driver,actions,machine_class)
    #time.sleep(0.6)
    handle_os(driver,actions,os_index,os_name)
    #time.sleep(0.6)
    handle_machine_family(driver,actions,machine_family_index,machine_family)
    #time.sleep(0.6)
    handle_series(driver,actions,series_index,series)
    #time.sleep(0.6)
    handle_machine_type(driver,actions,machine_type,machine_type_index)
    #time.sleep(0.6)
    
    if vCPU!=0:
        if (machine_family.lower() == "general purpose" and series in ["N1", "N2", "N4", "E2", "N2D"] and not (series == "N1" and machine_type in ["f1-micro", "g1-small"])):
                print(f"Calling handle_vcpu_and_memory Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
                
                ram_limits = {
                'N1': 256,
                'N2': 16,
                'N2D': 256,
                'N4': 16,
                'E2': 16
                }
                
                memory_limit = get_memory_limit(series, ram)

                if machine_type == 'custom' and ram > memory_limit:
                    extended_mem_toggle_on(driver,actions)
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                else:
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                
            
        elif machine_family.lower() == "accelerator optimized" and series == "G2":
                print(f"Calling handle_vcpu_and_memory  Machine Family: {machine_family}, Series: {series}")
                if machine_type=='custom':
                    #extended_mem_toggle_on(driver,actions)
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                else:
                    handle_vcpu_and_memory(driver, actions, vCPU, ram)
                    
        else:
            print("inside the loop ")
           
            
    else:
        print(f"Skipping handle_vcpu_and_memory: Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
    
    #time.sleep(0.6)
    boot_disk_type(driver,actions)
    #time.sleep(0.6)
    boot_disk_capacitys(driver,actions,boot_disk_capacity)    
    
    #time.sleep(0.6)
    
    select_region(driver,actions,region)
    
    #time.sleep(0.6)
    
    three_year_selection(driver,actions)
    
    time.sleep(10)
    
    current_url = driver.current_url
    
    price=get_price_with_js(driver)
    if machine_type=='custom':
       machine_type_data= scrape_custom_machine_type(driver,actions)
    else:
       machine_type_data=scrape_machine_type(driver,actions)
    print(price,current_url)
    
    driver.quit()
    
    print("✅ three year pricing done")
    
    return current_url, price , machine_type_data


#=============================================================================================#


def main(sheet_url,recipient_email):
    download_sheet(sheet_url)

    process_csv(input_file, output_file_filtered)
    sheet = pd.read_csv(input_filtered_file)
    results = []

    for index, row in sheet.iterrows():
        try:
            
            missing_fields = []
            required_fields = ["No. of Instances",  "Datacenter Location", "OS with version"]
            
            for field in required_fields:
                if pd.isna(row[field]):
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"Skipping row {index + 1}: Missing required fields ({', '.join(missing_fields)})")
                results.append({
                    "Row Index": index + 1,
                    "OS with version": row["OS with version"] if pd.notna(row["OS with version"]) else "Unknown",
                    "Error": f"Missing required fields: {', '.join(missing_fields)}"
                })
                continue
        
            os_name = row["OS with version"]
            print(os_name)
            no_of_instances = round(float(row["No. of Instances"]), 2) if pd.notna(row["No. of Instances"]) else 0.00
            machine_family = row["Machine Family"].lower() if pd.notna(row["Machine Family"]) else "general purpose"
            series = row["Series"].upper() if pd.notna(row["Series"]) else "E2"
            machine_type = row["Machine Type"].lower() if pd.notna(row["Machine Type"]) else "custom"
            vCPU = row["vCPUs"] if pd.notna(row["vCPUs"]) else 0
            ram = row["RAM"] if pd.notna(row["RAM"]) else 0
            boot_disk_capacity = row["BootDisk Capacity"] if pd.notna(row["BootDisk Capacity"]) else 0
            region = row["Datacenter Location"] if pd.notna(row["Datacenter Location"]) else "Mumbai"
            hours_per_day = int(row["Avg no. of hrs"]) if pd.notna(row["Avg no. of hrs"]) else 730
            machine_class = str(row["Machine Class"]) if pd.notna(row["Machine Class"]) else "regular"
            #print(hours_per_day)
            machine_class=machine_class.lower()
            
            '''if hours_per_day <730:
                same_costing=True'''
            
            print(f"Processing row {index + 1} with OS: {os_name}, Instances: {no_of_instances}, machine family: {machine_family}, series: {series}, machine type: {machine_type}")

            row_result = {
                "Row Index": index + 1,
                "OS with version": os_name,
                "No. of Instances": no_of_instances,
                "Machine Family": machine_family,
                "Machine type":machine_type,
                "On-Demand URL": None,
                "On-Demand Price": None,
                "SUD URL": None,
                "SUD Price": None,
                "1-Year URL": None,
                "1-Year Price": None,
                "3-Year URL": None,
                "3-Year Price": None
            }

            for iteration in range(4):  
                try:
                    
                    
                    
                    if  machine_class=="preemptible": #if it is less than on demand price  ///////even if it greater then 730 and (spot/premtible eny condition the price is ondemand)
                        if series=="E2":  
                            if iteration==0:
                                print(f"Iteration {iteration + 1}: Getting on-demand price and link (e2-micro)")
                                row_result["On-Demand URL"], row_result["On-Demand Price"] , row["Machine type"]= get_on_demand_pricing(
                                    os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class
                                )

                            if iteration==1:
                                
                                print(f"Iteration {iteration + 1}: Getting sustained use discount (SUD) price and link")
                                row_result["SUD URL"], row_result["SUD Price"], row["Machine type"] = row_result["On-Demand URL"], row_result["On-Demand Price"], row["Machine type"]
                                
                                row_result["1-Year URL"], row_result["1-Year Price"], row["Machine type"] = row_result["SUD URL"], row_result["SUD Price"], row["Machine type"]
                                row_result["3-Year URL"], row_result["3-Year Price"], row["Machine type"] = row_result["SUD URL"], row_result["SUD Price"], row["Machine type"]
                                break
                        
                        else:
                            if iteration==0:
                                print(f"Iteration {iteration + 1}: Getting on-demand price and link (e2-micro)")
                                row_result["On-Demand URL"], row_result["On-Demand Price"] , row["Machine type"]= get_on_demand_pricing(
                                    os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class
                                )

                            if iteration==1:
                                
                                print(f"Iteration {iteration + 1}: Getting sustained use discount (SUD) price and link")
                                row_result["SUD URL"], row_result["SUD Price"], row["Machine type"] = row_result["On-Demand URL"], row_result["On-Demand Price"], row["Machine type"]
                                
                                row_result["1-Year URL"], row_result["1-Year Price"], row["Machine type"] = row_result["SUD URL"], row_result["SUD Price"], row["Machine type"]
                                row_result["3-Year URL"], row_result["3-Year Price"], row["Machine type"] = row_result["SUD URL"], row_result["SUD Price"], row["Machine type"]
                                break
                        
                        
                        
                        
                        
                    if  machine_class=="regular" and hours_per_day < 730:
                        if series=="E2":
                            if iteration==0:
                                print(f"Iteration {iteration + 1}: Getting on-demand price and link (e2-micro)")
                                row_result["On-Demand URL"], row_result["On-Demand Price"] , row["Machine type"]= get_on_demand_pricing(
                                    os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class
                                )

                            if iteration==1:
                                
                                print(f"Iteration {iteration + 1}: Getting sustained use discount (SUD) price and link")
                                row_result["SUD URL"], row_result["SUD Price"], row["Machine type"] = row_result["On-Demand URL"], row_result["On-Demand Price"], row["Machine type"]
                                
                                row_result["1-Year URL"], row_result["1-Year Price"], row["Machine type"] = row_result["SUD URL"], row_result["SUD Price"], row["Machine type"]
                                row_result["3-Year URL"], row_result["3-Year Price"], row["Machine type"] = row_result["SUD URL"], row_result["SUD Price"], row["Machine type"]
                                break
                        else:
                            
                            if iteration==0:
                                print(f"Iteration {iteration + 1}: Getting on-demand price and link (e2-micro)")
                            row_result["On-Demand URL"], row_result["On-Demand Price"],row["Machine type"] = get_on_demand_pricing(
                                os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class
                            )

                            if iteration==1:
                                
                                if series=="C2D":
                            
                                    print(f"Iteration {iteration + 1}: Getting sustained use discount (SUD) price and link")
                                    row_result["SUD URL"], row_result["SUD Price"],row["Machine type"] = get_on_demand_pricing(
                                        os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class
                                    )
                                    
                                    row_result["1-Year URL"], row_result["1-Year Price"], row["Machine type"] = row_result["SUD URL"], row_result["SUD Price"], row["Machine type"]
                                    row_result["3-Year URL"], row_result["3-Year Price"], row["Machine type"] = row_result["SUD URL"], row_result["SUD Price"], row["Machine type"]
                                    break
                                else:
                                    print(f"Iteration {iteration + 1}: Getting sustained use discount (SUD) price and link")
                                    row_result["SUD URL"], row_result["SUD Price"],row["Machine type"] = get_sud_pricing(
                                        os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class
                                    )
                                    
                                    row_result["1-Year URL"], row_result["1-Year Price"], row["Machine type"] = row_result["SUD URL"], row_result["SUD Price"], row["Machine type"]
                                    row_result["3-Year URL"], row_result["3-Year Price"], row["Machine type"] = row_result["SUD URL"], row_result["SUD Price"], row["Machine type"]
                                    break
                                    
                    
                    else:
                        
                        
                            if iteration == 0:
                                print(f"Iteration {iteration + 1}: Getting on-demand price and link")
                                row_result["On-Demand URL"], row_result["On-Demand Price"],row["Machine type"] = get_on_demand_pricing(
                                    os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class
                                )
                            elif iteration == 1:
                                if series=="E2" or series=="C2D":
                                    print(f"Iteration {iteration + 1}: Getting sustained use discount (SUD) price and link")
                                    row_result["SUD URL"], row_result["SUD Price"], row["Machine type"] = row_result["On-Demand URL"], row_result["On-Demand Price"], row["Machine type"] 
                                    
                                
                                else:
                                    print(f"Iteration {iteration + 1}: Getting sustained use discount (SUD) price and link")
                                    row_result["SUD URL"], row_result["SUD Price"],row["Machine type"] = get_sud_pricing(
                                        os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class
                                    )
                            elif iteration == 2:
                                print(f"Iteration {iteration + 1}: Getting 1-year commitment price and link")
                                row_result["1-Year URL"], row_result["1-Year Price"],row["Machine type"] = get_one_year_pricing(
                                    os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class
                                )
                            elif iteration == 3:
                                print(f"Iteration {iteration + 1}: Getting 3-year commitment price and link")
                                row_result["3-Year URL"], row_result["3-Year Price"] ,row["Machine type"]= get_three_year_pricing(
                                    os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region,machine_class
                                )
                                
                except Exception as e:
                    print(f"Error processing row {index + 1}, iteration {iteration + 1}: {e}")
                    if iteration == 0:
                        row_result["On-Demand URL"] = "Error"
                        row_result["On-Demand Price"] = "Error"
                    elif iteration == 1:
                            row_result["SUD URL"] = "Error"
                            row_result["SUD Price"] = "Error"
                    elif iteration == 2:
                        row_result["1-Year URL"] = "Error"
                        row_result["1-Year Price"] = "Error"
                    elif iteration == 3:
                        row_result["3-Year URL"] = "Error"
                        row_result["3-Year Price"] = "Error"
                finally:
                    time.sleep(2)

            results.append(row_result)
        
        except Exception as e:
            print(f"Critical error processing row {index + 1}: {e}")
            results.append({
                "Row Index": index + 1, 
                "OS with version": row["OS with version"] if pd.notna(row["OS with version"]) else "Unknown", 
                "Error": str(e)
             })

    output_file = "data/ComputeEngine.xlsx"  # Excel file extension

    output_df = pd.DataFrame(results)
    output_df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")
    print("sending mail!!")
    send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, file_path)


@app.route('/calculate',methods=["POST"])
def run_automation():
    sheet = request.form.get('sheet')
    email = request.form.get('email')
    process_status[email] = "Processing"
    main(sheet,email)
    process_status[email] = "Completed"
    return "process completed sucessfully"




if __name__ == "__main__":
    
    app.run(debug=True,use_reloader=False,host='0.0.0.0')
