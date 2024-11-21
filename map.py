from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
import requests
from time import sleep
from random import randint

import csv
import os


class Map:
    def __init__(self):
        self.write_csv(['Category', 'Name', 'Address', 'Open and Close', 'Website', 'Phone', 'Url'], 'map_output')

    def get_driver(self, headless: bool):
        self.options = webdriver.ChromeOptions()
        if headless is True:
            self.options.add_argument("--headless")
        self.options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("lang=en-GB")
        self.options.add_argument('--ignore-certificate-errors')
        # self.options.add_argument('--lang=en')
        self.options.add_argument('--allow-running-insecure-content')
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--proxy-server='direct://'")
        self.options.add_argument("--proxy-bypass-list=*")
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        # self.options.add_argument("--log-level=OFF")
        self.options.add_argument("--log-level=3")

        path = os.path.join(os.getcwd(), 'chromedriver.exe')
        self.driver = webdriver.Chrome(path, options=self.options)
        return self.driver

    def write_csv(self, data, file_name):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(this_dir, file_name + '.csv')
        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:  # works on windows issue also maybe!?
            writer = csv.writer(csvfile)

            row = []
            # our data can be either list or dictionary
            if isinstance(data, dict):
                # if dictionary getting the values
                for key, value in data.items():
                    temp = [key, value]
                    row.append(temp[1])
            elif isinstance(data, list):
                row = data
            writer.writerow(row)

    def get_csv_list(self):
        id = 1234
        categories = []
        with open('categories.csv', 'r') as file:
            csv_file = csv.reader(file)
            for d in csv_file:
                categories.append(d[0])
        with open('location.csv', 'r') as file:
            csv_file = csv.reader(file)
            for f in csv_file:
                state = f[0]
                kword = f[1]
                for category in categories:
                    search_word = '{} {}, {}'.format(category, state, kword)
                    self.get_url(search_word)
                    sleep(randint(7, 15))

    def get_url(self, keyword):
        print('Searching: ', keyword)
        driver = self.get_driver(True)
        wait = WebDriverWait(driver, 10)
        try:
            driver.get('https://www.google.com/maps')
        except:
            self.internet_connection()
            sleep(4)
            return self.get_url(keyword)
        search_element = driver.find_element(By.XPATH, '//*[@id="searchboxinput"]')
        search_element.clear()
        search_element.send_keys(keyword)
        search_element.send_keys(Keys.ENTER)

        wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]')))
        links = []

        while True:
            sleep(4)
            i = 1
            while True:
                try:

                    element = wait.until(EC.presence_of_element_located(
                        (By.XPATH, f'//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[{i}]')))

                    element.location_once_scrolled_into_view
                    try:
                        link = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        links.append(link)
                    except Exception:
                        pass
                except Exception:
                    break
                i += 1
            try:
                next_page = driver.find_element(By.XPATH, "//button[@id='ppdPk-Ej1Yeb-LgbsSe-tJiF1e']")
                next_page.click()
            except exceptions.ElementClickInterceptedException:
                # print(e)
                break

        links = links[:int(len(links) / 2)]
        for link in links:
            self.get_data(link, driver)

    def get_data(self, url, driver: webdriver):
        wait = WebDriverWait(driver, 10)
        try:
            driver.get(url)
        except:
            self.internet_connection()
            sleep(randint(5, 12))
            driver = self.get_driver(True)
            return self.get_data(url, driver)
        try:
            name = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[1]/h1/span[1]'))).text
        except exceptions.TimeoutException:
            name = ''
        # print(url)
        try:
            # category = driver.find_element(By.XPATH,
            #                            '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[2]/span[1]/span[1]/button').text
            category = driver.find_element(By.XPATH, "//div[@class='gm2-body-2']/span/span/button").text
        except:
            # print('category error: ', url)
            category = ''
        try:
            address = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[@data-item-id='address']//div[@class='rogA2c']"))).text
        except exceptions.TimeoutException:
            address = ''

        try:
            # website = driver.find_element(By.XPATH, "//button[@data-item-id='authority']//div[@class='rogA2c HY5zDd']").text
            website = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[@data-item-id='authority']//div[@class='rogA2c HY5zDd']"))).text
        except exceptions.TimeoutException:
            website = ''
        try:
            mobile = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[@data-tooltip='Copy phone number']//div[@class='rogA2c']"))).text.strip()
        except exceptions.TimeoutException:
            mobile = ''

        # open close time
        cnd = True
        try:
            # open_close_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-item-id='oh']")))
            open_close_button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='OqCZI gm2-body-2 WVXvdc']")))
            open_close_button.click()
            sleep(2)
        except exceptions.TimeoutException:
            try:
                open_close_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//button[@data-item-id='oh']")))
                open_close_button.click()
            except exceptions.TimeoutException:
                cnd = False
                pass
        open_close = []
        sleep(2)
        if cnd:
            trs = wait.until(EC.presence_of_element_located((By.XPATH, '//table/tbody'))).find_elements(By.TAG_NAME,
                                                                                                        'tr')

            for tr in trs:
                tds = tr.find_elements(By.TAG_NAME, 'td')
                # print(tds)
                day = tds[0].text.strip()
                # print(day)
                time = tds[1].text.strip()
                # print(time)
                temp = "{} {}".format(day, time)
                open_close.append(temp)
            # print(open_close)
        open_close = ','.join(open_close)
        self.write_csv([category, name, address, open_close, website, mobile, url], 'map_output')

    def internet_connection(self):
        while True:
            try:
                requests.get('https://xkcd.com/353/')
                print('Internet is available..')
                break
            except Exception:
                print('Internet is not available...', end='\r')
                sleep(10)


if __name__ == '__main__':
    mp = Map()
    mp.get_csv_list()
