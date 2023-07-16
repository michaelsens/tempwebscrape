from time import sleep
import pandas as pd
import glob
import os
from datetime import date
from shutil import move
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def find_links(driver, city):
    links = []
    driver.get(f"https://apartments.com/{city}")
    print(type(driver))
    maxpg = int(driver.find_element(By.CLASS_NAME, "pageRange").text.split(" ")[-1])
    for pg in range(1, maxpg):
        driver.get(f"https://apartments.com/{city}/{pg}")
        elements = driver.find_elements(By.CLASS_NAME, "property-link")
        links.extend(list(set([element.get_attribute('href') for element in elements])))
    return links

def main(city='richmond-va'):
    out = f'../output/apartments.com/{city}'
    if not os.path.exists(out):
        os.makedirs(out)

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    #options.add_argument('headless') #removed for debug

    driver = webdriver.Chrome(service=service, options=options)
    aptlinks = find_links(driver, city)
    print(aptlinks) #debug
    print(len(aptlinks)) #debug
    driver.quit()
        
# run main function
if __name__ == '__main__':
    main()