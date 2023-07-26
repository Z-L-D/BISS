from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import argparse
import time

# Configure Firefox options
options = Options()
options.add_argument('-headless')  # Remove this line if you want Firefox to run visibly

# Define the webdriver
webdriver_service = Service('env/bin/')
driver = webdriver.Firefox(service=webdriver_service, options=options)

def bing_image_search_url(query):
    url = f'https://www.bing.com/images/search?q={query.replace(" ", "+")}'
    return url

def extract_image_elements(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    img_elements = soup.find_all('img')
    return img_elements

def extract_suggestion_titles(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    suggestion_titles_list = soup.find_all(lambda tag: tag.name == 'a' and tag.get('title', '').startswith('Search for: '))

    # Use regular expression to extract the text in the aria-label element
    pattern = r'aria-label="(.*?)"'
    suggestion_titles = re.findall(pattern, f"{suggestion_titles_list}")
    
    return suggestion_titles

def save_elements_to_file(elements, output_file, mode):
    with open(output_file, mode) as file:
        for element in elements:
            file.write(str(element) + '\n')

def find_matching_image_elements(input_file, output_file):
    # pattern = r"https://(?P<sub>[^.]+).mm.bing.net/th/id/OIP\.(?P<id>[^.]+)"
    pattern = r"https://th.bing.com/th/id/OIP\.(?P<id>[^.]+)"

    with open(input_file, "r") as input_file, open(output_file, "w") as output_file:
        text = input_file.read()
        matches = re.finditer(pattern, text)

        for match in matches:
            image_id = match.group("id")
            url = f"https://th.bing.com/th/id/OIP.{image_id}"
            
            # Truncate the URL to ignore everything from "?w=" onward
            url = url.split("?")[0]
            
            output_file.write(url + "\n")

def download_images_from_urls(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found.")
        return

    # Open the file and read URLs
    with open(file_path, 'r') as file:
        urls = file.read().splitlines()

    # Create a folder to store downloaded images
    folder_name = os.path.splitext(os.path.basename(file_path))[0]
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Download images from each URL
    for i, url in enumerate(urls):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Determine the image format
                file_extension = ".jpg" if response.headers.get("content-type") == "image/jpeg" else ".jpg"
                # Create a filename using the format "searchterm_000.jpg"
                filename = f"{folder_name}/{folder_name}_{str(i).zfill(3)}{file_extension}"
                # Save the image file
                with open(filename, 'wb') as img_file:
                    img_file.write(response.content)
                print(f"Downloaded image {i+1}/{len(urls)}")
            else:
                print(f"Failed to download image from {url}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error while downloading image from {url}: {str(e)}")

def main():
    while True:  # Start of infinite loop
        #PART 1 - gather urls
        search_query = input("Enter your Bing image search query: ")

        if search_query.lower() == 'quit':  # Check if user wants to quit
            break

        url = bing_image_search_url(search_query)

        try:
            # Navigate to a website
            driver.get(url)

            try:
                # Execute JavaScript code
                driver.execute_script("document.getElementById('ss-off').click(); ")
                # Wait for JavaScript execution - Adjust this sleep time as per your needs
                time.sleep(2)
            except:
                print("Safesearch already set.")

            output_img_file = search_query + ".txt"
            output_suggestion_file = search_query + "_suggestions.txt"

            html_content = driver.page_source
            img_elements = extract_image_elements(html_content)
            suggestion_titles = extract_suggestion_titles(html_content)

            save_elements_to_file(img_elements, output_img_file, 'w')
            print(f"Image elements saved to '{output_img_file}' successfully.")

            save_elements_to_file(suggestion_titles, output_suggestion_file, 'w')
            print(f"Suggestion elements saved to '{output_suggestion_file}' successfully.")

            #PART 2 - parse urls
            image_list_input_file = search_query + ".txt"
            image_list_output_file = search_query + "_results.txt"
            find_matching_image_elements(image_list_input_file, image_list_output_file)

            # PART3 - download urls
            download_list = image_list_output_file
            download_images_from_urls(download_list)

        finally:
            # Do not close the browser here
                pass
        
    # Close the browser once the loop is exited
    driver.quit()

if __name__ == "__main__":
    main()