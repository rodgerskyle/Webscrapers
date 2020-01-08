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
        print("hey")
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
        #driver.get("https://www.mcdonalds.com/us/en-us/about-our-food/nutrition-calculator.html")
        driver.get("https://www.mcdonalds.com/us/en-us/full-menu.html")
        #Grabs button for each category then will press it
        time.sleep(6)
        #button = driver.find_elements_by_class_name('btn-category-nav')
        button = driver.find_elements_by_class_name('category-link')
        #Name of Category
        category = button[index].text.lower()
        driver.execute_script("arguments[0].click()", button[index])
        time.sleep(6)
        #Link to page
        pageLink = driver.current_url

        #Page with all items on it
        #Find number of items and will re-loop based on how many there are
        #listOfItems = driver.find_element_by_class_name('mcd-nutrition-calculator__product-selection-container')
        #items = listOfItems.find_elements_by_class_name('btn-category-nav')
        items = driver.find_elements_by_class_name('categories-item-link')
        #Buffer amount to basically pad existing items
        #buffer = 0
        #Grab global curIndex
        global curIndex
        for i in range(len(items)):
            items = driver.find_elements_by_class_name('categories-item-link')
            driver.execute_script("arguments[0].click()", items[i])
            time.sleep(6)
            #Check if item has sizes
            sizes = True
            sizeChoices = None
            try:
                #sizeChoices = driver.find_elements_by_class_name("ncselect")
                tempFinder = driver.find_element_by_class_name("product-size-wrapper")
                sizeChoices = tempFinder.find_elements_by_class_name("ng-scope")
            except Exception as f:
                print(f)
                sizes = False
            #Grab item info and then refresh page and repeat stuff above
            #Keep repeating item details for size
            repeat = True

            lock.acquire()
            #Grab image and save the filepath
            imgTmp = driver.find_element_by_class_name("product-detail__main-content-img")
            img = imgTmp.find_element_by_tag_name("img")
            src = img.get_attribute('srcset')
            src = "https://www.mcdonalds.com" + src
            imgpath = "McDonalds/" + str(curIndex) + "k.jpg"
            urllib.request.urlretrieve(src, imgpath)
            #Increment curIndex
            curIndex+=1
            lock.release()
            #Sizes with index attached
            sizeIndex = 0
            while (repeat):
                content = driver.page_source
                soup = BeautifulSoup(content, "html.parser")
                stats = driver.find_element_by_class_name('mcd-panel')
                page = stats.find_elements_by_class_name('ng-binding')
                #Title
                #title = driver.find_element_by_class_name('typo-h1')
                title = soup.find('h1', attrs={'class':'heading'}).text.strip()
                title = title.replace('®', '')
                title = title.replace('™', '')
                print(title)
                if (sizes):
                    #Grabs sizes choices
                    tempFinder = driver.find_element_by_class_name("product-size-wrapper")
                    sizeChoices = tempFinder.find_elements_by_class_name("ng-scope")
                    #Grabs size name from the span tag
                    size = soup.find('span', attrs={'class':'product-size-text'}).text.strip()
                    title = title + " (" + size + ")"
                    time.sleep(1)
                    if sizeIndex >= len(sizeChoices):
                        repeat = False
                    else:
                        #Clicks onto the next size for the next loop
                        driver.execute_script("arguments[0].click()", sizeChoices[sizeIndex].find_element_by_class_name('ng-binding'))
                        sizeIndex+=1
                        time.sleep(2)
                else:
                    repeat = False
                #Grab pages new information just in case
                #stats = driver.find_element_by_class_name('mcd-panel')
                #page = stats.find_elements_by_class_name('sr-only')
                content = driver.page_source
                soup = BeautifulSoup(content, "html.parser")
                page = soup.findAll('span', attrs={'class':'sr-only'})
                #Description
                #description = driver.find_element_by_class_name("product-detail__description").text.strip()
                description = soup.find('p', attrs={'class':'product-detail__description'}).text.strip()
                description = '"' + description + '"'
                #Meal
                if (category.find("breakfast")):
                    meal = "Breakfast"
                elif (category.find("sides")):
                    meal = "Sides"
                elif (category.find("beverages")):
                    meal = "Beverage"
                elif (category.find("desserts")):
                    meal = "Dessert"
                else:
                    meal = "Lunch / Dinner"
                #Fat
                fat = page[4]
                fat = fat.text.strip().split(None, 1)[0]
                #print("Fat " + fat)
                #Sodium
                sodium = page[18]
                sodium = sodium.text.strip().split(None, 1)[0]
                #print("Sodium " + sodium)
                #Carbs
                carbs = page[6]
                carbs = carbs.text.strip().split(None, 1)[0]
                #print("Carbs " + carbs)
                #Fiber
                fiber = page[11]
                fiber = fiber.text.strip().split(None, 1)[0]
                #print("Fiber " + fiber)
                #Sugar
                sugar = page[25]
                sugar = sugar.text.strip().split(None, 1)[0]
                #print("Sugar " + sugar)
                #Protein
                protein = page[8]
                protein = protein.text.strip().split(None, 1)[0]
                #print("Protein " + protein)
                #Calories
                calories = page[0]
                calories = calories.text.strip().split(None, 1)[0]
                #print("Calories " + calories)
                #Output to file
                lock.acquire()
                f = open("output.txt", "a")
                f.write(title + ", " + description + ", ")
                f.write(meal + ", " + fat + ", ")
                f.write(sodium + ", " + carbs + ", ")
                f.write(fiber + ", " + sugar + ", ")
                f.write(protein + ", " + calories + ", ")
                f.write(imgpath + ",\n")
                f.close()
                lock.release()
            #After done with item; exclude it
            #excludes = driver.find_elements_by_class_name("custom-checkmark")
            #driver.execute_script("arguments[0].click()", excludes[0])
            #buffer += sizeIndex
            #driver.back()
            #backScript = "window.history.go(" + str(sizeIndex*-1) + ")"
            #driver.execute_script(backScript)
            driver.get(pageLink)
            sizeIndex = 0
            time.sleep(2)
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

#parentDriver.get("https://www.mcdonalds.com/us/en-us/about-our-food/nutrition-calculator.html")

parentDriver.get("https://www.mcdonalds.com/us/en-us/full-menu.html")

#This grabs all the categories on the page
#categories = parentDriver.find_elements_by_class_name('mcd-nutrition-calculator__category-item')
categories = parentDriver.find_elements_by_class_name('category-link')

#Grabs the category names of each category
content = parentDriver.page_source
soup = BeautifulSoup(content, "html.parser")
categoryName = soup.findAll('span', attrs={'class':'category-title'})

#Close parent
parentDriver.close()

#Create global index for img paths
curIndex = 1

#Creating lock for multiprocessing
lock = Lock()

#Load up n'th number of processes for scraping
for i in range(len(categories)):
    tempS = categoryName[i].text.strip().lower()
    if (i >= 2 and tempS.find("meal") is -1):
        Process(target=scrape, args=(lock, i)).start()

