from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


import time
import random

import undetected_chromedriver as uc


def scrape_latest_results(output_dir):

    url = 'https://www.propertyguru.com.sg'
    driver = uc.Chrome(headless=False,use_subprocess=False)
    driver.get(url)
    time.sleep(random.uniform(3,5))
    buy_btn = driver.find_element(By.XPATH, "//a[@data-automation-id='main-nav-buy-lnk']")
    buy_btn.click()
    time.sleep(random.uniform(3,5))
    sort_by_div = driver.find_element(By.CLASS_NAME, 'new-project-category-filter')
    sort_by_btn = sort_by_div.find_element(By.TAG_NAME, 'button')
    sort_by_btn.click()
    time.sleep(random.uniform(2,4))
    sort_by_btn = sort_by_div.find_element(By.XPATH, "//a[@data-value='Newest']")
    sort_by_btn.click()

    page_count = 1
    while True:
        time.sleep(random.uniform(2, 3))
        page = BeautifulSoup(driver.page_source, 'html.parser')
        if page.find('body', attrs={'class': 'errorPage'})!=None:
            break
        with open(f"{output_dir}/{page_count}_listings.html", "w") as file:
            file.write(str(page.prettify()))

        pagination = driver.find_element(By.XPATH, "//div[@data-automation-id='listing-pagination']")
        actions = ActionChains(driver)
        actions.move_to_element(pagination).perform()
        time.sleep(random.uniform(2,3))
        
        next_page = pagination.find_element(By.CLASS_NAME, 'pagination-next')
        next_page = next_page.find_elements(By.TAG_NAME,'a')

        if len(next_page)==0:
            break
        else:
            next_page = next_page[0]
            next_page.click()
            if len(driver.find_elements(By.CLASS_NAME, 'errorPage'))>0:
                break
            page_count += 1
                
    driver.quit()
