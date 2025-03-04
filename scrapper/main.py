from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import os
import requests
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# PDF folder (inside Docker container or local machine)
download_dir = os.path.expanduser("~/naizaCrochetingDev/scrapper/input_file/{project_type}")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Set Chrome options for headless scraping
chrome_options = Options()
chrome_options.add_argument("--headless")  # Running in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

print("[INFO] Automatically detecting and installing the correct ChromeDriver...")

# Automatically install the matching ChromeDriver version
try:
    service = Service(ChromeDriverManager().install())  
    # Initialize the WebDriver using the chrome_options
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("[INFO] WebDriver started successfully.")
except Exception as e:
    print(f"[ERROR] Failed to start WebDriver: {e}")
    exit()

# Download function
def download_pdf(pdf_url, file_name, project_type):
    print(f"[INFO] Attempting to download {file_name} from {pdf_url}...")
    try:
        # Ensure that the project-specific directory exists
        project_dir = download_dir.format(project_type=project_type)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        # Construct the full path for the PDF file
        pdf_path = os.path.join(project_dir, file_name)
        
        # Download the PDF file in streaming mode
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
        
        with open(pdf_path, 'wb') as pdf_file:
            for chunk in response.iter_content(1024):
                pdf_file.write(chunk)

        print(f"[SUCCESS] Downloaded: {file_name} at {pdf_path}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to download {file_name}: {e}")
    except Exception as e:
        print(f"[ERROR] Error saving {file_name}: {e}")

# Function to scrape and download patterns from Yarnspirations for a given cloth type
def download_yarnspirations(project_type, total_page_num):
    # Note: The base URL doesn't currently change by project_type. 
    # If needed, update the URL to filter by cloth type.
    base_url = "https://www.yarnspirations.com/collections/patterns?filter.p.m.global.project_type={project_type}&page={page_num}"

    print(f"[INFO] Starting scraping for project type: {project_type}, Total pages: {total_page_num}")

    for page_num in range(1, total_page_num + 1):
        print(f"[INFO] Scraping page {page_num} for {project_type}...")
        driver.get(base_url.format(project_type=project_type, page_num=page_num))
        
        # Wait until the "Free Pattern" buttons are loaded
        try:
            print("[INFO] Waiting for pattern elements to load...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'card-button--full')]"))
            )
            print("[INFO] Patterns loaded successfully.")
        except Exception as e:
            print(f"[ERROR] Error while waiting for patterns to load on page {page_num}: {e}")
            continue
        
        # Find "Free Pattern" buttons by XPath
        pattern_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'card-button--full')]")
        print(f"[INFO] Found {len(pattern_links)} pattern links on page {page_num} for {project_type}")

        for pattern_link in pattern_links:
            pdf_url = pattern_link.get_attribute('href')
            # Check if the link is a PDF link
            if pdf_url and pdf_url.endswith('.pdf'):
                file_name = pdf_url.split('/')[-1]
                print(f"[INFO] Found PDF link: {pdf_url} for {project_type} - Downloading...")
                download_pdf(pdf_url, file_name, project_type)
            else:
                print(f"[WARNING] Skipping non-PDF or invalid link: {pdf_url}")

    print(f"[INFO] Completed scraping for project type: {project_type}")

# Quit WebDriver after the task is done
def quit_driver():
    print("[INFO] Quitting WebDriver...")
    driver.quit()
    print("[INFO] WebDriver closed.")

# List of clothing types to scrape
clothes_list = ['Tops', 'Dresses', 'Skirts', 'Pants', 'Jackets']

# Loop through each cloth type with a counter
for index, cloth in enumerate(clothes_list, start=1):
    print(f"\n[INFO] [{index}/{len(clothes_list)}] Starting scraping for cloth type: {cloth}")
    # You can adjust the number of pages for each cloth type as needed.
    download_yarnspirations(cloth, total_page_num=2)
    print(f"[INFO] [{index}/{len(clothes_list)}] Completed scraping for cloth type: {cloth}\n")

# Quit WebDriver after all scraping tasks are finished
quit_driver()
