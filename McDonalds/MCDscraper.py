from selenium import webdriver
from bs4 import BeautifulSoup

#Multiprocessing component
from multiprocessing import Process, Lock
import copy

import pandas as pd
import os

#Downloading images from website
import urllib

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
        options = Options()
        '''options.add_argument('--headless')   
        options.add_argument('--disable-extensions')   
        options.add_argument('--disable-gpu')   
        options.add_argument("--no-sandbox")   
        options.add_argument("--window-size=1920,1080")   
        options.add_argument('--disable-dev-shm-usage') '''
        driver = webdriver.Chrome(options=options)

        #driver = webdriver.Chrome()
        driver.get("https://www.mcdonalds.com/us/en-us/about-our-food/nutrition-calculator.html")
        #Grabs button for each category then will press it
        time.sleep(6)
        button = driver.find_elements_by_class_name('btn-category-nav')
        driver.execute_script("arguments[0].click()", button[index])
        time.sleep(6)

        #Page with all items on it
        #Find number of items and will re-loop based on how many there are
        listOfItems = driver.find_element_by_class_name('mcd-nutrition-calculator__product-selection-container')
        items = listOfItems.find_elements_by_class_name('btn-category-nav')
        #Buffer amount to basically pad existing items
        buffer = 0
        #Grab global curIndex
        global curIndex
        for i in range(len(items)):
            driver.execute_script("arguments[0].click()", items[i])
            time.sleep(6)
            #Check if item has sizes
            sizes = True
            sizeChoices = None
            try:
                sizeChoices = driver.find_elements_by_class_name("ncselect")
            except Exception as f:
                print(f)
                sizes = False
            #Grab item info and then refresh page and repeat stuff above
            #Keep repeating item details for size
            repeat = True

            lock.acquire()
            #Grab image and save the filepath
            imgTmp = driver.find_element_by_class_name("prod-image")
            img = imgTmp.find_element_by_tag_name("img")
            src = img.get_attribute('src')
            imgpath = "McDonalds/" + str(curIndex) + "k.jpg"
            urllib.request.urlretrieve(src, imgpath)
            #Increment curIndex
            curIndex+=1
            lock.release()
            #Sizes with index attached
            sizeIndex = 0
            while (repeat):
                stats = driver.find_element_by_class_name('nutrition-calculator-alter')
                page = stats.find_elements_by_class_name('ng-binding')
                #Title
                title = driver.find_element_by_class_name('prod-name')
                title = title.text.strip()
                title = title.replace('®', '')
                title = title.replace('™', '')
                if (sizes):
                    #Grabs size name from the a tag
                    dropdown = driver.find_element_by_class_name('dropdown-toggle')
                    size = dropdown.find_element_by_class_name('ng-binding').text
                    #print("Size Name: " + size)
                    title = title + " (" + size + ")"
                    sizeIndex+=1
                    time.sleep(1)
                    if sizeIndex+buffer >= len(sizeChoices):
                        repeat = False
                    else:
                        #Clicks onto the next size for the next loop
                        driver.execute_script("arguments[0].click()", sizeChoices[sizeIndex].find_element_by_class_name('ng-binding'))
                        time.sleep(2)
                else:
                    repeat = False
                #print(title)
                #Fat
                fat = page[5]
                fat = fat.text.strip()
                #print("Fat " + fat)
                #Sodium
                sodium = page[34]
                sodium = sodium.text.strip()
                #print("Sodium " + sodium)
                #Carbs
                carbs = page[9]
                carbs = carbs.text.strip()
                #print("Carbs " + carbs)
                #Fiber
                fiber = page[19]
                fiber = fiber.text.strip()
                #print("Fiber " + fiber)
                #Sugar
                sugar = page[26]
                sugar = sugar.text.strip()
                #print("Sugar " + sugar)
                #Protein
                protein = page[13]
                protein = protein.text.strip()
                #print("Protein " + protein)
                #Calories
                calories = page[1]
                calories = calories.text.strip()
                #print("Calories " + calories)
                #Output to file
                lock.acquire()
                f = open("output.txt", "a")
                f.write(title + ", " + fat + ", ")
                f.write(sodium + ", " + carbs + ", ")
                f.write(fiber + ", " + sugar + ", ")
                f.write(protein + ", " + calories + ", ")
                f.write(imgpath + ",\n")
                f.close()
                lock.release()
            #After done with item; exclude it
            excludes = driver.find_elements_by_class_name("custom-checkmark")
            driver.execute_script("arguments[0].click()", excludes[0])
            buffer += sizeIndex
            sizeIndex = 0
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

#Close parent
parentDriver.close()

#Create global index for img paths
curIndex = 1

#Creating lock for multiprocessing
lock = Lock()

scrape(lock, 0)
'''
#Load up n'th number of processes for scraping
for i in range(len(categories)):
        Process(target=scrape, args=(lock, i)).start()
        #Closes processes after done
'''
