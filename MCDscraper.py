from selenium import webdriver
from bs4 import BeautifulSoup

import pandas as pd
import os

#For continually loading new products on page
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

PATIENCE_TIME = 60

os.remove("output.txt")
f = open("output.txt", "a")
driver = webdriver.Chrome("./chromedriver")

driver.get("https://www.mcdonalds.com/us/en-us/about-our-food/nutrition-calculator.html")

#This grabs all the categories on the page
categories = driver.find_elements_by_class_name('mcd-nutrition-calculator__category-item')

for i in categories:
    #Grabs button for each category then will press it
    button = i.find_element_by_class_name("btn-category-nav")
    #time.sleep(2)
    driver.execute_script("arguments[0].click();", button)
    time.sleep(2)
    #Parses the page to just text
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")
    itemNames = soup.findAll('span', attrs={'class': 'name text-center ng-binding'})
    itemCalories = soup.findAll('span', attrs={'class': 'calory-count text-center ng-binding'})
    for names, calories in zip(itemNames, itemCalories):
        #Finds the items' calories
        name=names.text.strip()
        name=name.replace('®', '')
        name=name.replace('™', '')
        calorie=calories.text.strip()
        #Outputs scraped information to the file
        f.write(name + ", " + calorie + ",\n")
    #Find back button and click that
    backbutton = i.find_element_by_class_name("btn-back")
    time.sleep(2)
    driver.execute_script("arguments[0].click();", backbutton)
    time.sleep(2)

driver.close()




