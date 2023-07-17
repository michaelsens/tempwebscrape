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

df = pd.DataFrame()
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

def add_listings(driver, links):
    global df
    for link in links:
        driver.get(link)
        try:
            units_tab = driver.find_element(By.XPATH, "//*[@data-tab-content-id='all']")
            units = get_units(units_tab)
            if units.size == 0:
                units = get_house(driver)
            df = pd.concat([df, units])
        except:
            pass

def get_house(driver):
    house_dict = {
        'num_beds': [],
        'num_baths': [],
        'sq_ft': [],
        'address': [],
        'price': [],
    }
    try:
        details = driver.find_elements(By.CLASS_NAME, "priceBedRangeInfoInnerContainer")
        price = details[0].find_element(By.CLASS_NAME, "rentInfoDetail").text
        num_beds = details[1].find_element(By.CLASS_NAME, "rentInfoDetail").text
        num_baths = details[2].find_element(By.CLASS_NAME, "rentInfoDetail").text
        sq_ft = details[3].find_element(By.CLASS_NAME, "rentInfoDetail").text

        addr_parts = driver.find_elements(By.XPATH, "//*[@class='propertyAddressContainer']/h2/span")
        print(addr_parts)
        city = addr_parts[0].text
        zipr = addr_parts[1].text
        neighborhood = addr_parts[2].text
        addr = f'{city}, {neighborhood}, {zipr}'

        house_dict['num_beds'].append(num_beds)
        house_dict['num_baths'].append(num_baths)
        house_dict['sq_ft'].append(sq_ft)
        house_dict['address'].append(addr)
        house_dict['price'].append(price)
    except:
        pass
    return pd.DataFrame(house_dict)

def get_units(units_tab):
    units_dict = {
        'num_beds': [],
        'num_baths': [],
        'sq_ft': [],
        'address': [],
        'price': [],
    }
    try:
        floor_plans = units_tab.find_elements(By.CLASS_NAME, "hasUnitGrid")
    except:
        return pd.DataFrame(units_dict)
    for floor_plan in floor_plans:
        try:
            details = floor_plan.find_elements(By.XPATH, ".//*[@class='detailsTextWrapper']/span")
            num_beds = details[0].text
            num_baths = details[1].text
            sq_ft = details[2].text
            units = floor_plan.find_elements(By.CLASS_NAME, "unitContainer")
            for unit in units:
                try:
                    unit_num = unit.find_element(By.XPATH, ".//button[contains(@class,'unitBtn')]/span[2]").text
                    price = unit.find_element(By.XPATH, ".//*[contains(@class,'pricingColumn')]/span[2]").text

                    units_dict['num_beds'].append(num_beds)
                    units_dict['num_baths'].append(num_baths)
                    units_dict['sq_ft'].append(sq_ft)
                    units_dict['address'].append(unit_num)
                    units_dict['price'].append(price)
                except:
                    pass
        except:
            pass

    return pd.DataFrame(units_dict)


def main(city='richmond-va'):
    out = f'../output/apartments.com/{city}'
    if not os.path.exists(out):
        os.makedirs(out)

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') #removed for debug

    driver = webdriver.Chrome(service=service, options=options)
    #
    # driver.get("https://www.apartments.com/ink-at-scotts-collection-richmond-va/j7w4xz5/")
    #
    # units_tab = driver.find_element(By.XPATH, "//*[@data-tab-content-id='all']")
    # units = get_units(units_tab)
    # print(units)
    #
    # driver.get("https://www.apartments.com/2400-perry-st-richmond-va/4xhy6vl/")
    # get_house(driver)

    aptlinks = find_links(driver, city)
    print(aptlinks) #debug
    print(len(aptlinks)) #debug
    add_listings(driver, aptlinks)
    print(df)
    driver.quit()
        
# run main function
if __name__ == '__main__':
    main()