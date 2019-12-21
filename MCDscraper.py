from selenium import webdriver
from bs4 import BeautifulSoup

#Multiprocessing component
from multiprocessing import Process, Lock

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

def scrape(lock, category):
    try:
        #driver = webdriver.Firefox()
        options = Options()
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        #driver = webdriver.Chrome()
        driver.get("https://www.mcdonalds.com/us/en-us/about-our-food/nutrition-calculator.html")
        #Grabs button for each category then will press it
        #button = i.find_element_by_class_name("btn-category-nav")
        time.sleep(6)

        button = driver.find_element_by_class_name('btn-category-nav')
#        button = category
        driver.execute_script("arguments[0].click();", button)
        #driver.execute_script("arguments[0].click();", category)
        #time.sleep(6)
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
            print(name + ", " + calorie + ",\n")
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
#f = open("output.txt", "a")
#parentDriver = webdriver.Chrome(chrome_options=options)
parentDriver = webdriver.Chrome()

parentDriver.get("https://www.mcdonalds.com/us/en-us/about-our-food/nutrition-calculator.html")

#This grabs all the categories on the page
#categories = driver.find_elements_by_class_name('mcd-nutrition-calculator__category-item')
categories = parentDriver.find_elements_by_class_name('btn-category-nav')

#Grab number of processes
#processes = len(categories)

lock = Lock()
#Load up n'th number of processes for scraping
for category in categories:
        Process(target=scrape, args=(lock, category)).start()
        break
        #Closes processes after done

#for i in categories:

parentDriver.close()




