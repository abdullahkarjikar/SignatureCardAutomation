from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()
driver.get("https://campuslink.okstate.edu/forms/actioncenter/organization/campus-life")

try:
    # Wait Until Login page is fully loaded and Enter username and password
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@id='username']"))
    )
    username.send_keys('abdulla.karjikar@okstate.edu')
    password = driver.find_element("xpath", "//*[@id='password']")
    password.send_keys(password)
    driver.find_element("xpath", '/html/body/main/div/div/div/form/div[3]/button').click()

    try:
        # Move ahead by selecting trust browser on duo Security
        element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "trust-browser-button"))
        )
        element.click()

        try:
            # Wait until the Forms' page is fully loaded and click options in Signature card form
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="single-spa-application:@campuslabs/engage-app-forms"]/div/div/div[3]/div[2]/ul/li[3]/div/button'))
            )
            element.click()

            # Select export to excel in Forms options
            export_to_excel = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/ul/li[4]/div[2]/span'))
            )
            export_to_excel.click()

            # Takes 1 second the popup for download to appear
            time.sleep(1)

            go_to_download_button = driver.find_element('xpath',
                                                        '//*[@id="single-spa-application:@campuslabs/engage-app-forms"]/div/div[2]/div/div/div/div/div/div[2]/a')
            print(go_to_download_button.get_attribute('href'))
            driver.get(go_to_download_button.get_attribute('href'))

            print("Found the download button")
            try:

                ############################################
                while True:
                    try:
                        driver.find_element_by_xpath(
                            '//*[@id="layoutPage"]/div[1]/div/div/div[3]/div[4]/div[2]/div/section/div[1]/div/button/div')
                        break
                    except NoSuchElementException:
                        driver.refresh()
                ############################################
                download_report_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//*[@id="report-list"]/tr[1]/td[5]/a[1]')))
                go_to_download_button = driver.find_element('xpath', '//*[@id="report-list"]/tr[1]/td[5]/a[1]')
                print(go_to_download_button.get_attribute('href'))
                driver.get(go_to_download_button.get_attribute('href'))
            except:
                print("Error Occured")
        except:
            driver.quit()
    except:
        driver.quit()
except:
    driver.quit()

# driver.find_element("xpath", '//*[@id="trust-browser-button"]').click()

# try:
#     element = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.LINK_TEXT, "Sign In")))
#     element.click()
# except:
#     pass
