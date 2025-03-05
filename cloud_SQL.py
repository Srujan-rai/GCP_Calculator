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


app=Flask(__name__)


sender_email = "srujan.int@niveussolutions.com"
sender_password = "rmlh ikej rtmz ejme"
subject = "Compute Calculation Results"
body = "Please find the attached file for the results of the computation."
file_path = "output_results.xlsx"




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



def home_page(driver,actions):
        """Navigates to the pricing section."""
        driver.implicitly_wait(5)
        add_to_estimate_button = driver.find_element(By.XPATH, "//span[text()='Add to estimate']")
        add_to_estimate_button.click()
        time.sleep(5)
        div_element = driver.find_element(By.XPATH, "//div[@class='d5NbRd-EScbFb-JIbuQc PtwYlf' and @data-service-form='7']")
        actions.move_to_element(div_element).click().perform()
        time.sleep(2)
        print("✅ home page done")


def service_type(driver,actions,service_type):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Service type')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite(service_type)
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("✅ service type  selected")




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


def advanced_toggle_on(driver,actions):
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Advanced settings')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.ENTER).perform()
    print("✅ Advanced settings turned on")




def cloud_sql_edition(driver,actions,edition):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Cloud SQL  Edition')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    
    
    if edition=="Enterprise":
        pass
    
    elif edition=="Enterprise Plus":
        actions.send_keys(Keys.ARROW_RIGHT).perform()
    
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("✅ Edition selected")


def Specify_usage_time(driver,actions):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Specify usage time for each instance')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    
    actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()

    
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("✅ Usage time selected")


def instance(driver,actions,instance):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Number of instances')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    
    actions.send_keys(instance).perform()
    time.sleep(0.3)
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    print("✅ Instance selected")




def usage_time(driver,actions,usage_time):
    if usage_time==730:
        print("✅ Usage time selected")
        pass
    
    else:
        time.sleep(0.6)
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.6)
        
        pyautogui.typewrite('Total instance usage time')
        time.sleep(0.6)
        
        pyautogui.press('esc')
        time.sleep(0.6)
        
        actions.send_keys(Keys.ENTER).perform()
        
        for _ in range(3):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        time.sleep(0.2)
        actions.send_keys(usage_time).perform()
        time.sleep(0.2)
        for _ in range(2):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        
        print("✅ Usage time selected")





def select_sql_instance_type(driver,actions,instance_type):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Select SQL instance type')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    instance_type=str(instance_type)
    pyautogui.typewrite(instance_type)
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)   
    actions.send_keys(Keys.ENTER).perform()
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.3)
    print("✅ SQL instance type selected")




def vcpu_handle(driver,actions,vcpu,ram):
    if vcpu==0:
        print("Skipped Vcpu as it is default")
        pass
    else:
        time.sleep(0.6)
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.6)
        
        pyautogui.typewrite('Number of vCPUs')
        time.sleep(0.6)
        
        pyautogui.press('esc')
        time.sleep(0.6)
        
        actions.send_keys(Keys.ENTER).perform()
        for _ in range(3):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        
        
            
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(0.3)
        actions.send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.3)
        actions.send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.3)
        
        actions.send_keys("1").perform()
        
        time.sleep(0.6)
                
        steps=(vcpu//2)
        
        for _ in range(int(steps)):
            actions.send_keys(Keys.ARROW_UP).perform()
            time.sleep(0.2)
            
        actions.send_keys(Keys.ENTER).perform()
        
        '''actions.send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.3)
        actions.send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.3)
        actions.send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.6)

        actions.send_keys(Keys.BACKSPACE).perform()
        
        time.sleep(0.6)
        actions.send_keys(vcpu).perform()
        time.sleep(0.2)
        actions.send_keys(Keys.TAB).perform()'''
        
        
        print(f"the vcpu is {vcpu}")
        time.sleep(0.6)
        
        
        print("Vcpu got selected")
    
    if ram==0:
        pass
    
    else:
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
            
    
        time.sleep(0.3)
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(0.3)
        actions.send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.3)
        actions.send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.3)
        actions.send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.3)
        actions.send_keys(Keys.BACKSPACE).perform() 
        time.sleep(0.3)
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
        time.sleep(0.2)
        actions.send_keys(Keys.TAB).perform()
        print("ram is selected")

    
    print("✅ vpcu and ram selected")
        
        
        
    

def enable_high_availability(driver,actions,availability):
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Enable High Availability configuration')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
    time.sleep(0.6)
    actions.send_keys(Keys.ENTER).perform()
    print("✅ Advanced settings turned on")


def handle_Storage(driver,actions,size):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Storage (Provisioned Amount)')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.2)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.2)
    actions.send_keys(Keys.BACKSPACE).perform()

    time.sleep(0.6)
    pyautogui.typewrite(str(size))
    time.sleep(0.6)
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    print("✅ Storage selected")




def handle_storage_type(driver,actions):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Storage Type')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    
    actions.send_keys(Keys.ARROW_RIGHT).perform()
    time.sleep(0.2)
    actions.send_keys(Keys.ENTER).perform()
    
    print("✅ Storage type selected")
    


def backup_size(driver,actions,backup_size_value):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Backup size')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    
    actions.send_keys(backup_size_value).perform()
    time.sleep(0.6)
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    print("✅ Backup size selected")




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
    

def add_to_estimate(driver,actions):
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Add to estimate')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    div_element = driver.find_element(By.XPATH, "//div[@class='d5NbRd-EScbFb-JIbuQc PtwYlf' and @data-service-form='7']")
    actions.move_to_element(div_element).click().perform()
    time.sleep(2)
   
    
    print("✅ Added to estimate")

#========================================================================================================#
def sud_pricing(driver,actions,service_type_value,region,cloud_sql_edition_value,instance_value,usage_time_value,instance_type,HA,storage_type,size,backup_size_value,vcpu,ram):
    service_type(driver,actions,service_type_value)
    select_region(driver,actions,region)
    advanced_toggle_on(driver,actions)
    cloud_sql_edition(driver,actions,cloud_sql_edition_value)
    #Specify_usage_time(driver,actions)
    instance(driver,actions,instance_value)
    time.sleep(0.3)
    usage_time(driver,actions,usage_time_value)
    time.sleep(0.3)
    select_sql_instance_type(driver,actions,instance_type)
    time.sleep(0.3)
    if instance_type.lower()!= "f1-micro" or instance_type.lower()!= "g1-small":
        vcpu_handle(driver,actions,vcpu,ram)
    if HA.upper()=="HA":
        enable_high_availability(driver,actions,HA)
    handle_Storage(driver,actions,size)
    if storage_type=="HDD":
        handle_storage_type(driver,actions) 
    
    backup_size(driver,actions,backup_size_value)
    #time.sleep(10)
    
    current_url = driver.current_url
    time.sleep(10)

    price=get_price_with_js(driver)
    
    print(price,current_url)
    
    
    print("✅ SUD pricing done")
    
    return price, current_url

def one_year_pricing(driver,actions,service_type_value,region,cloud_sql_edition_value,instance_value,usage_time_value,instance_type,HA,storage_type,size,backup_size_value,vcpu,ram):
    service_type(driver,actions,service_type_value)
    select_region(driver,actions,region)
    advanced_toggle_on(driver,actions)
    cloud_sql_edition(driver,actions,cloud_sql_edition_value)
    #Specify_usage_time(driver,actions)
    instance(driver,actions,instance_value)
    usage_time(driver,actions,usage_time_value)
    time.sleep(0.3)
    select_sql_instance_type(driver,actions,instance_type)
    time.sleep(0.3)
    if instance_type.lower()!= "f1-micro" or instance_type.lower()!= "g1-small":
        vcpu_handle(driver,actions,vcpu,ram)
    if HA.upper()=="HA":
        enable_high_availability(driver,actions,HA)
    handle_Storage(driver,actions,size)
    if storage_type.upper()=="HDD":
        handle_storage_type(driver,actions) 
    
    backup_size(driver,actions,backup_size_value)
    
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Committed use discount options')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
    
    actions.send_keys(Keys.ARROW_RIGHT).perform()
    time.sleep(0.4)
    actions.send_keys(Keys.ENTER).perform()
    current_url = driver.current_url
    time.sleep(10)

    price=get_price_with_js(driver)
    
    print(price,current_url)
    print("✅ One year pricing selected")
    return price,current_url

def three_year_pricing(driver,actions,service_type_value,region,cloud_sql_edition_value,instance_value,usage_time_value,instance_type,HA,storage_type,size,backup_size_value,vcpu,ram):
    service_type(driver,actions,service_type_value)
    select_region(driver,actions,region)
    advanced_toggle_on(driver,actions)
    cloud_sql_edition(driver,actions,cloud_sql_edition_value)
    #Specify_usage_time(driver,actions)
    instance(driver,actions,instance_value)
    time.sleep(0.3)
    usage_time(driver,actions,usage_time_value)
    time.sleep(0.3)
    select_sql_instance_type(driver,actions,instance_type)
    time.sleep(5)
    if instance_type.lower()!= "f1-micro" or instance_type.lower()!= "g1-small":
        vcpu_handle(driver,actions,vcpu,ram)
    if HA.upper()=="HA":
        enable_high_availability(driver,actions,HA)
    handle_Storage(driver,actions,size)
    if storage_type=="HDD":
        handle_storage_type(driver,actions) 
    
    backup_size(driver,actions,backup_size_value)
    
    
    
    
    
    time.sleep(0.6)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.6)
    
    pyautogui.typewrite('Committed use discount options')
    time.sleep(0.6)
    
    pyautogui.press('esc')
    time.sleep(0.6)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.6)
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
    
    actions.send_keys(Keys.ARROW_RIGHT).perform()
    time.sleep(0.4)
    actions.send_keys(Keys.ARROW_RIGHT).perform()
    time.sleep(0.4)
    actions.send_keys(Keys.ENTER).perform()
    current_url = driver.current_url
    time.sleep(10)
    price=get_price_with_js(driver)
    
    print(price,current_url)
    print("✅ Three year pricing selected")
    return  price,current_url

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
            tab_name = "CloudSql"
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={tab_name}"
            response = requests.get(csv_url)

            if response.status_code == 200:
                with open("data/cloudSQL_input_sheet.csv", "wb") as f:
                    f.write(response.content)
                print("Google Sheet downloaded as cloudSQL_input_sheet.csv")
            else:
                print("Failed to download sheet. HTTP Status Code:", response.status_code)
        except ValueError as e:
            print(e)
        except Exception as e:
            print("An error occurred:", e)



#========================================================================================================#


def read_input_values(file_path):# Read the input sheet
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
        
    df.fillna({
        "SQL Type": "",
        "Datacenter Location": "",
        "Cloud SQL ": "Enterprise",
        "No. of Instances": 1,
        "Avg no. of hrs": 730,
        "Instance Type": "db-n1-standard-2",
        "HA/Non-HA": "Non-HA",
        "Disk Type": "HDD",
        "Storage Amt": 256,
        "vCPUs":0,
        "RAM":0,
    }, inplace=True)
    
    return df

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

    
def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": os.path.join(os.getcwd(), "downloads"),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get("https://cloud.google.com/products/calculator")
    driver.implicitly_wait(10)
    return driver

def main(sheet,email):
    
    download_sheet(sheet)
    
    file_path = "data/cloudSQL_input_sheet.csv"
    
    
    df = read_input_values(file_path)
    
    results = []
    
    for index, row in df.iterrows(  ):
        # Validation checks
        error_message = []

        if not row["SQL Type"] or not row["Datacenter Location"] or not row["No. of Instances"]:
            error_message.append("Missing required values (SQL Type, Datacenter Location, No. of Instances)")

        if row["SQL Type"].lower() == "postgresql" and row["Storage Amt"] < 10.74:
            error_message.append("Storage amount cannot be less than 10.74")

        if int(row["Avg no. of hrs"]) < 730 and int(row["No. of Instances"]) > 1:
            error_message.append("Invalid configuration: More than one instance running for less than 730 hours is not logical.")
            
        
        row["Error"] = "; ".join(error_message) if error_message else ""
        results.append(row)
        
    df = pd.DataFrame(results)
    save_to_excel(df, "processed_data.xlsx")
    
    if df["Error"].str.contains("Missing required values|Storage Amt must be greater than 10.74").any():
        print("❌ Errors found in some rows. Check 'processed_data.xlsx' for details.")
    else:
        print("✅ All data is valid. Proceeding with processing.")
    
    df = df[df["Error"] == ""]  # Filter out rows with errors
    if df.empty:
        print("⚠ No valid rows to process. Exiting...")
        return

    
    driver = setup_driver()
    actions = ActionChains(driver)
    time.sleep(1)
    home_page(driver, actions)

    for index, row in df.iterrows():
        try:
            print(f"Processing row {index}...")

            sud_price, sud_current_url = sud_pricing(
            driver, actions, 
            row["SQL Type"], row["Datacenter Location"], row["Cloud SQL "], 
            float(row["No. of Instances"]) if not pd.isna(row["No. of Instances"]) else 0, 
            int(row["Avg no. of hrs"]) if not pd.isna(row["Avg no. of hrs"]) else 730, 
            str(row["Instance Type"]), row["HA/Non-HA"], 
            row["Disk Type"], 
            int(row["Storage Amt"]) if not pd.isna(row["Storage Amt"]) else 0, 
            int(row["Backup"]) if not pd.isna(row["Backup"]) else 0, 
            float(row["vCPUs"]) if not pd.isna(row["vCPUs"]) else 0, 
            float(row["RAM"]) if not pd.isna(row["RAM"]) else 0
        )

            results[index] = {
                "SUD Price": sud_price,
                "SUD URL": sud_current_url
            }

            if index < len(df) - 1:
                add_to_estimate(driver, actions)

        except Exception as e:
            print(f"Error at index {index}: {e}")
            continue  # Prevents crashing; moves to next iteration

    driver.quit()
    
    
    
    
    # Processing One-Year Pricing
    driver = setup_driver()
    actions = ActionChains(driver)
    time.sleep(1)
    home_page(driver,actions)
    for index, row in df.iterrows():
        
            
        if int(row["Avg no. of hrs"]) < 730:
            one_year_price, one_year_current_url = sud_pricing(driver, actions, 
            row["SQL Type"], row["Datacenter Location"], row["Cloud SQL "], 
            float(row["No. of Instances"]) if not pd.isna(row["No. of Instances"]) else 0, 
            int(row["Avg no. of hrs"]) if not pd.isna(row["Avg no. of hrs"]) else 730, 
            str(row["Instance Type"]), row["HA/Non-HA"], 
            row["Disk Type"], 
            int(row["Storage Amt"]) if not pd.isna(row["Storage Amt"]) else 0, 
            int(row["Backup"]) if not pd.isna(row["Backup"]) else 0, 
            float(row["vCPUs"]) if not pd.isna(row["vCPUs"]) else 0, 
            float(row["RAM"]) if not pd.isna(row["RAM"]) else 0
        )
            results[index]["One Year Price"] = one_year_price
            results[index]["One Year URL"] = one_year_current_url
            
            
            
            
        else:
            one_year_price, one_year_current_url = one_year_pricing(driver, actions, 
            row["SQL Type"], row["Datacenter Location"], row["Cloud SQL "], 
            float(row["No. of Instances"]) if not pd.isna(row["No. of Instances"]) else 0, 
            int(row["Avg no. of hrs"]) if not pd.isna(row["Avg no. of hrs"]) else 730, 
            str(row["Instance Type"]), row["HA/Non-HA"], 
            row["Disk Type"], 
            int(row["Storage Amt"]) if not pd.isna(row["Storage Amt"]) else 0, 
            int(row["Backup"]) if not pd.isna(row["Backup"]) else 0, 
            float(row["vCPUs"]) if not pd.isna(row["vCPUs"]) else 0, 
            float(row["RAM"]) if not pd.isna(row["RAM"]) else 0
        )
            results[index]["One Year Price"] = one_year_price
            results[index]["One Year URL"] = one_year_current_url
        
        
        
        
        if index < len(df) - 1:
            add_to_estimate(driver,actions)
    driver.quit()
    
    
    
    
    
    # Processing Three-Year Pricing
    driver = setup_driver()
    actions = ActionChains(driver)
    time.sleep(1)
    home_page(driver,actions)
    
    for index, row in df.iterrows():
        
        if int(row["Avg no. of hrs"]) < 730:
            three_year_price, three_year_current_url = sud_pricing(driver, actions, 
            row["SQL Type"], row["Datacenter Location"], row["Cloud SQL "], 
            float(row["No. of Instances"]) if not pd.isna(row["No. of Instances"]) else 0, 
            int(row["Avg no. of hrs"]) if not pd.isna(row["Avg no. of hrs"]) else 730, 
            str(row["Instance Type"]), row["HA/Non-HA"], 
            row["Disk Type"], 
            int(row["Storage Amt"]) if not pd.isna(row["Storage Amt"]) else 0, 
            int(row["Backup"]) if not pd.isna(row["Backup"]) else 0, 
            float(row["vCPUs"]) if not pd.isna(row["vCPUs"]) else 0, 
            float(row["RAM"]) if not pd.isna(row["RAM"]) else 0
        )
            results[index]["three Year Price"] = three_year_price
            results[index]["three Year URL"] = three_year_current_url
            
            
            
            
        else:
            three_year_price, three_year_current_url = three_year_pricing(driver, actions, 
            row["SQL Type"], row["Datacenter Location"], row["Cloud SQL "], 
            float(row["No. of Instances"]) if not pd.isna(row["No. of Instances"]) else 0, 
            int(row["Avg no. of hrs"]) if not pd.isna(row["Avg no. of hrs"]) else 730, 
            str(row["Instance Type"]), row["HA/Non-HA"], 
            row["Disk Type"], 
            int(row["Storage Amt"]) if not pd.isna(row["Storage Amt"]) else 0, 
            int(row["Backup"]) if not pd.isna(row["Backup"]) else 0, 
            float(row["vCPUs"]) if not pd.isna(row["vCPUs"]) else 0, 
            float(row["RAM"]) if not pd.isna(row["RAM"]) else 0
        )
            results[index]["three Year Price"] = three_year_price
            results[index]["three Year URL"] = three_year_current_url
            
        if index < len(df) - 1:
            add_to_estimate(driver,actions)
    driver.quit()
    
    save_to_excel(results, "data/CloudSQL.xlsx")
    send_email_with_attachment(sender_email, sender_password, email, subject, body, "data/CloudSQL.xlsx")
    print("✅ All pricing done and saved in pricing_summary.xlsx")


@app.route('/calculate',methods=["POST"])
def run_automation():
    sheet = request.form.get('sheet')
    email = request.form.get('email')
    
    main(sheet,email)
    
    return "process completed sucessfully"






if __name__ == "__main__":
    app.run(debug=True,use_reloader=False,host='0.0.0.0')
  