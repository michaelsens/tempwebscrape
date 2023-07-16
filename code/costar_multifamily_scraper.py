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
#from settings import *

pd.set_option('display.max_columns', None)


# define web driver class
class Driver:
    """
    options: list of web driver options
    browser: Browser Type: Chrome, Firefox
    This creates a webdriver object with options.
    """

    def __init__(self, options=(), browser='chrome', web_driver_path=None):
        self.options = options
        self.browser = browser
        if self.browser == "firefox":
            web_driver_path = 'drivers\FirefoxDriver\geckodriver\geckodriver.exe'
            self.driver = webdriver.Firefox(executable_path=web_driver_path)
        elif self.browser == "chrome":
            if (web_driver_path is None):
                web_driver_path = 'drivers\ChromeDriver\chromedriver_win32\chromedriver.exe'
            self.driver = webdriver.Chrome(service=Service(executable_path=web_driver_path))

    def set_zoom_value(self, zoom_value):
        # Zoom In and Out
        self.driver.execute_script("document.body.style.zoom='" + str(zoom_value) + "%'")
        sleep(1)
        self.driver.set_window_size(1980, 1200)
        sleep(1)
        self.driver.maximize_window()
        sleep(10)

    def send_keys(self, tag_value, key_value):
        """Finds the element using xpath. If found, send_keys it."""
        elements = self.driver.find_elements('xpath', tag_value)
        if len(elements) > 0:
            elements[0].clear()
            elements[0].send_keys(key_value)

    def clear_keys(self, tag_value):
        """Finds the element using xpath. If found, send_keys it."""
        elements = self.driver.find_elements('xpath', tag_value)
        if len(elements) > 0:
            elements[0].clear()

    def click_button_xpath_with_script(self, tag_value):
        """Finds the element using xpath. If found, clicks it."""
        buttons = self.driver.find_elements('xpath', tag_value)
        if len(buttons) > 0:
            self.driver.execute_script("arguments[0].click();", buttons[0])

    def click_button_xpath(self, tag_value):
        """Finds the element using xpath. If found, clicks it."""
        buttons = self.driver.find_elements('xpath', tag_value)
        if len(buttons) > 0:
            buttons[0].click()

    def get_element_list(self, tag_value):
        """Get a list of elements from an xpath"""
        return self.driver.find_elements('xpath', tag_value)

    def execute_script(self, code, element):
        """Executes script"""
        return self.driver.execute_script(code, element)

    def current_url(self):
        """Gets current URL"""
        return self.driver.current_url

    def page_source(self):
        """Gets page source"""
        return self.driver.page_source

    def back(self):
        """Takes the driver 1 page back"""
        return self.driver.back()

    def close(self):
        """closes the driver"""
        return self.driver.close()


# Costar Login
def costar_login(driver):
    driver.driver.get('https://product.costar.com')
    driver.driver.maximize_window()
    sleep(3)
    driver.send_keys("//input[@id='username']", USER_NAME)
    driver.send_keys("//input[@id='password']", PASSWORD)
    driver.click_button_xpath("//span[@class='login-footer-remember-me']")
    driver.click_button_xpath("//button[@id='loginButton']")


# open CoStar property page
def get_property(driver, address):
    driver.click_button_xpath("//button[@automation-id='uui-tab-tier-1-PROPERTIES']")
    sleep(2)
    driver.click_button_xpath("//button[@automation-id='uui-tab-tier-2-MULTI_FAMILY']")
    sleep(5)
    driver.send_keys("//input[@placeholder='Address or Location']", address)
    sleep(3)
    driver.click_button_xpath("//span[@data-action='select google geocode']")
    driver.click_button_xpath("//span[@data-action='select single property']")
    sleep(3)

    placards = driver.driver.find_elements('xpath', f"//div[@automation-id='placardTitle']")
    for i in range(len(placards)):
        if placards[i].text in address:
            placards[i].click()
            break


# Open multifamily page, starting with analytics
def get_analytics(driver, mf_id, out):
    #driver.driver.get(f'https://product.costar.com/detail/multi-family/{mf_id}/analytics')
    driver.click_button_xpath("//a[@automation-id='detail-tab-analytics']")
    sleep(5)
    driver.click_button_xpath("//a[@class='ovrd-cspd-anlytc-navbar-link']")
    sleep(3)
    driver.click_button_xpath("//span[@class='csg-tui-text csg-css-anlytics-detail-1ixw8ou']")
    sleep(2)
    try:
        newfile = max(glob.glob(DOWNLOAD_PATH + '/PropertyDetail*.xlsx'), key=os.path.getctime)
    except ValueError:
        sleep(5)
        driver.click_button_xpath("//span[@class='csg-tui-text csg-css-anlytics-detail-1ixw8ou']")
        sleep(2)
        newfile = max(glob.glob(DOWNLOAD_PATH + '/PropertyDetail*.xlsx'), key=os.path.getctime)
    move(os.path.join(DOWNLOAD_PATH, newfile), 
        os.path.join(out, f'{os.path.basename(newfile)[:-5]}_{date.today().strftime("%Y%m%d")}_{mf_id}.xlsx'))


# download unit listings
def get_listings(driver, out):

    driver.click_button_xpath("//a[@automation-id='detail-tab-unitmix']")
    sleep(3)
        
    try:
        test = driver.driver.find_elements('xpath', '//span[@class="span__span--x217E info-grid__info--D3FJp"]')[0].text
        if 'Units data not available' in test:
            return None
    except IndexError:
        driver.click_button_xpath("//button[@class='unit-mix-ic__export-btn--IZk0Y']")
        sleep(2)
        try:
            newfile = max(glob.glob(DOWNLOAD_PATH + '/Unit Mix*.xlsx'), key=os.path.getctime)
        except ValueError:
            sleep(2)
            newfile = max(glob.glob(DOWNLOAD_PATH + '/Unit Mix*.xlsx'), key=os.path.getctime)
        move(os.path.join(DOWNLOAD_PATH, newfile), 
            os.path.join(out, f'{os.path.basename(newfile)[:-5]}_{date.today().strftime("%Y%m%d")}.xlsx'))


# download financials
def get_financials(driver, mf_id, out):
    driver.click_button_xpath("//a[@automation-id='detail-tab-cmbs-financials']")
    sleep(3)
    try:
        tbl = driver.driver.find_element(by=By.CLASS_NAME, value='csg-rc-table-container')
        pd.read_html(tbl.get_attribute('outerHTML'))[0].to_csv(
            os.path.join(out, f'financials_{date.today().strftime("%Y%m%d")}_{mf_id}.csv'),
            index=False
        )
    except IndexError:
        sleep(3)
        tbl = driver.driver.find_element(by=By.CLASS_NAME, value='csg-rc-table-container')
        pd.read_html(tbl.get_attribute('outerHTML'))[0].to_csv(
            os.path.join(out, f'financials_{date.today().strftime("%Y%m%d")}_{mf_id}.csv'),
            index=False
        )


# download comps
def get_comps(driver, out):
    driver.click_button_xpath("//a[@automation-id='detail-tab-comps']")
    sleep(5)
    driver.click_button_xpath("//button[@class='csg-tui-button css-tf04jy']")
    sleep(5)
    try:
        newfile = max(glob.glob(DOWNLOAD_PATH + '/Rent Comp*.xlsx'), key=os.path.getctime)
    except ValueError:
        sleep(2)
        driver.click_button_xpath("//button[@class='csg-tui-button css-tf04jy']")
        sleep(5)
        newfile = max(glob.glob(DOWNLOAD_PATH + '/Rent Comp*.xlsx'), key=os.path.getctime)
    move(os.path.join(DOWNLOAD_PATH, newfile), 
        os.path.join(out, f'{os.path.basename(newfile)[:-5]}_{date.today().strftime("%Y%m%d")}.xlsx'))


# download all data
def download_costar_data(driver, mf_id, address, out):
    get_property(driver, address)
    sleep(5)
    try:
        get_analytics(driver, mf_id, out)
    except ValueError:
        return None
    sleep(2)
    get_listings(driver, out)
    sleep(5)
    get_financials(driver, mf_id, out)
    sleep(2)
    get_comps(driver, out)
    sleep(2)
    driver.click_button_xpath("//a[@automation-id='uui-back-button']")
    sleep(5)
    driver.click_button_xpath("//a[@class='icon-button__icon-button--I_Ooo clear-button hoverable active']")
   

# load list of property IDs
def load_id_list(city):
    city_files = glob.glob(f'../data/costar_properties/CostarExport_{city}_*.xlsx')
    out = {}
    for city_file in city_files:
        df = pd.read_excel(city_file, usecols=['PropertyID', 'Property Address', 'City', 'State', 'Zip'])
        out.update({
            int(row['PropertyID']): f"{row['Property Address']}, {row['City']}, {row['State']} {row['Zip']}" 
            for i, row in df.iterrows()
        })     
    return out


# load list of property IDs already downloaded
def load_documentation(city):
    fname = f'../documentation/costar/{city}.txt'
    if os.path.isfile(fname):
        with open(fname, 'r') as file:
            done_ids = [int(line.strip()) for line in file.readlines()]
    return fname, done_ids
        
        
# main function
def main(city='Richmond'):
    out = f'../output/costar/{city}'
    if not os.path.exists(out):
        os.makedirs(out)
    
    doc_file, completed = load_documentation(city)
    
    driver_options = ('--ignore-certificate-errors'
                        # '--kiosk',
                        # '--incognito',
                        # '--headless'
                    )

    driver = Driver(driver_options, 'chrome', web_driver_path=DRIVER_PATH)
    costar_login(driver)
    sleep(15)
    properties = load_id_list(city)
    id_list = list(set(properties.keys()) - set(completed))
    
    for id in id_list[:1999]: # stay within 2000 daily download limit
        print(f'Downloading {id}...')
        sleep(5)
        download_costar_data(driver, id, properties[id], out)
        with open(doc_file, 'a') as f:
            f.write(f'{id}\n')
        sleep(2)

        
# run main function
if __name__ == '__main__':
    main()