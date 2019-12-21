from selenium import webdriver
from bs4 import BeautifulSoup

#Multiprocessing component
from multiprocessing import Process, Lock
import copy

import pandas as pd
import os

#Options for chrome
from selenium.webdriver.chrome.options import Options

#For continually loading new products on page
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape(lock, index):
    try:
        #driver = webdriver.Firefox()
        #options = Options()
        '''options.add_argument('--headless')   
        options.add_argument('--disable-extensions')   
        options.add_argument('--disable-gpu')   
        options.add_argument("--no-sandbox")   
        options.add_argument("--window-size=1920,1080")   
        options.add_argument('--disable-dev-shm-usage') '''
        #driver = webdriver.Chrome(options=options)

        driver = webdriver.Chrome()
        driver.get("https://www.mcdonalds.com/us/en-us/about-our-food/nutrition-calculator.html")
        #Grabs button for each category then will press it
        time.sleep(6)
        button = driver.find_elements_by_class_name('btn-category-nav')
        driver.execute_script("arguments[0].click()", button[index])
        time.sleep(6)
        #Parses the page to just text
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        itemNames = soup.findAll('span', attrs={'class': 'name text-center ng-binding'})
        itemCalories = soup.findAll('span', attrs={'class': 'calory-count text-center ng-binding'})
        for names, calories in zip(itemNames, itemCalories):
            #Finds the items' calories
            name=names.text.strip()
            #strips name string of bad characters
            name=name.replace('®', '')
            name=name.replace('™', '')
            calorie=calories.text.strip()
            #Outputs scraped information to the file
            lock.acquire()
            f = open("output.txt", "a")
            f.write(name + ", " + calorie + ",\n")
            lock.release()
        #Find back button and click that
        #backbutton = i.find_element_by_class_name("btn-back")
        #time.sleep(2)
        #driver.execute_script("arguments[0].click();", backbutton)
        #time.sleep(2)
        driver.close()
    except Exception as e:
        print(e)
        driver.close()

PATIENCE_TIME = 60

#Try to remove old output file 
try:
    os.remove("output.txt")
except Exception as e:
    print(e)
parentDriver = webdriver.Chrome()

parentDriver.get("https://www.mcdonalds.com/us/en-us/about-our-food/nutrition-calculator.html")

#This grabs all the categories on the page
categories = parentDriver.find_elements_by_class_name('mcd-nutrition-calculator__category-item')

#Grab number of processes

#Creating lock for multiprocessing
lock = Lock()
#Load up n'th number of processes for scraping
for i in range(len(categories)):
        Process(target=scrape, args=(lock, i).start()
        #Closes processes after done

parentDriver.close()




