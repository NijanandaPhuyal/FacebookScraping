from airtable.airtable import Airtable
from airtable import airtable
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import requests
import json
import time
import datetime
import logging

AIRTABLE_PAGES_TABLE = 'PAGES'
AIRTABLE_FILTER_TABLE = 'FILTER KEYWORDS'
AIRTABLE_OUTPUT_TABLE = 'OUTPUT'
AIRTABLE_BASE_ID = 'appxF2q7K2KVjbGAE'
AIRTABLE_API_KEY = 'keyJtbYuiGN3PoIR1'

FACEBOOK_ACCESS_TOKEN = 'EAAGztMNa1qkBAOQjKZATsrf60b9Njh6APTpZA01XzFARiVWocWL6q86yVsz1PL1FEUIoDgxcXSZAzZBoCO46C2dT5zS7Y6qJJZBYlA4wb0axhHZC9JL3KoW9x7xcNrmjcDVZBPf0CRFTeJdH3JZBfKcOCa0cH9vyiQvidepg1I6DeuHWW2T8kaGke6qqjwJoZBBvvyuUcFxIk0WFKy8lqGKAS'

if __name__ == '__main__':

    format = "%(asctime)s: %(message)s"
    logTime = datetime.datetime.now()

    logfile = "log_" + str(logTime.year) + "_" + str(logTime.month) + "_" + str(logTime.day) + "_" + str(logTime.hour) + "_" + str(logTime.minute) + "_" + str(logTime.second) + ".log"

    logging.basicConfig( filename=logfile, filemode="wt", format=format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("log started")

    airtable = Airtable(AIRTABLE_BASE_ID, AIRTABLE_PAGES_TABLE, AIRTABLE_API_KEY)
    recordsJSON = airtable.get_all()
    recordFields = []

    for record in recordsJSON:
        fieldsElement = record['fields']
        id_value = record['id']
        recordItem = dict()

        if fieldsElement:
            linkAddress = fieldsElement['Link']
            if linkAddress.find("facebook") != -1:
                recordItem['link'] = linkAddress.encode('utf-8')
                recordItem['id'] = id_value
                recordFields.append(recordItem)

    logging.info("Parsed Pages Tab")

    filtertable = Airtable(AIRTABLE_BASE_ID, AIRTABLE_FILTER_TABLE, AIRTABLE_API_KEY)
    filterJson = filtertable.get_all()

    recordsFilters = []

    for record in filterJson:
        fieldsElement = record['fields']
        id_value = record['id']
        recordItem = dict()
        if fieldsElement:
            name = fieldsElement['Name']
            recordItem['id'] = id_value
            recordItem['name'] = name.encode('utf-8')
            recordsFilters.append(recordItem)
            print(recordItem['name'])

    logging.info("Parsed Filter Tab")
    postList = []

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(executable_path = "chromedriver.exe", chrome_options = chrome_options)

    outputTable = Airtable(AIRTABLE_BASE_ID, AIRTABLE_OUTPUT_TABLE, AIRTABLE_API_KEY)    
    engflag = 0

    OutputJson = []

    for record in recordFields:
        try:
            logging.info("Scraping Every Record - %s", record['link'])
            MainUrl = record['link'].decode('utf-8') + "/posts/"
            MainUrl = MainUrl.replace('//posts/', '/posts/')
            driver.get(MainUrl)
            print(record['link'].decode('utf-8') + " - Loaded")

            if engflag == 0:
                try:
                    englishbtn = driver.find_element_by_class_name('_5f4c')
                    if englishbtn:
                        englishbtn.click()
                        engflag = 1
                    driver.find_element_by_id('email').send_keys("nijanphuyal@gmail.com")
                    driver.find_element_by_id('pass').send_keys("password12345678")
                    driver.find_element_by_id('pass').send_keys(Keys.ENTER)
                except:
                    logging.info("englishbtn error")
                time.sleep(3)

            postList = driver.find_elements_by_class_name('_427x')

            first = 0
            second = 0
            third = 0
            fourth = 0
            fifth  = 0
            sixth = 0
            seventh = 0
            now = 0

            if len(postList) == 0:
                MainUrl = record['link'].decode('utf-8')
                driver.get(MainUrl)
                postList = driver.find_elements_by_class_name('_5pcb')
                logging.info('Not Posts page')

                if len(postList) == 0:
                    logging.info('No Posts')
                    continue
                
                starttime = time.time()
                flag = 0
                matchPost = 0

                while (time.time() - starttime) < 30000 and flag == 0:
                    seemoreList = driver.find_elements_by_class_name('see_more_link')
                    print(len(seemoreList))
                    postList = driver.find_elements_by_class_name('_5pcb')
                    print("Page Posts - " + str(len(postList)))

                    now = len(postList)
                    first = second
                    second = third
                    third = fourth
                    fourth = fifth
                    fifth = sixth
                    sixth = seventh
                    seventh = now

                    if len(postList) > 100:
                        logging.info('Posts > 100')
                        break
                    if now == first:
                        page = driver.find_element_by_tag_name('html')
                        page.send_keys(Keys.END)
                        time.sleep(3)
                        postList = driver.find_elements_by_class_name('_5pcb')
                        if len(postList) == first:
                            logging.info('no more posts')
                            break
                    for post in postList:
                        text = post.text.encode('utf-8')
                        innerflag = 0
                        for filItr in recordsFilters:
                            if text.find(filItr['name']) != -1:
                                innerflag = 1
                                print("post found")                        
                                break
                        if innerflag == 1:
                            flag = 1
                            matchPost = post
                            break
                    page = driver.find_element_by_tag_name('html')
                    page.send_keys(Keys.END)
                    print("Page loaded")
                
                if matchPost:
                    dateElement = 0
                    OptionElement = 0
                    try:
                        dateElement = matchPost.find_element_by_class_name('_5ptz')
                        OptionElement = matchPost.find_element_by_class_name('_4xev')
                    except:
                        logging.info('Date Option Element get error')

                    postUrl = ''
                    try:
                        postUrlElement = matchPost.find_element_by_class_name('_5pcq')
                        postUrl = postUrlElement.get_attribute('href')
                    except:
                        logging.info("error Post url")

                    if postUrl.find('posts') == -1:
                        if OptionElement:
                            driver.execute_script("arguments[0].click();", OptionElement)
                            time.sleep(3)
                        NCElements = driver.find_elements_by_class_name('_54nc')
                        postid = ''

                        for element in NCElements:
                            ajaxiattr = element.get_attribute('ajaxify')

                            ajaxifyLink = str(ajaxiattr)
                            if ajaxifyLink.find('ft_id') != -1:
                                ftpos = ajaxifyLink.find('ft_id') + 6
                                endpos = ajaxifyLink.find('&')
                                postid = ajaxifyLink[ftpos:endpos]
                                break

                            ajaxifyLink = str(ajaxiattr)
                            if ajaxifyLink.find('posts') != -1:
                                ftpos = ajaxifyLink.find('posts') + 8
                                postid = ajaxifyLink[ftpos:]
                                break
                        
                        postUrl = record['link'].decode('utf-8') + '/posts/' + postid
                        postUrl = postUrl.replace('//posts', '/posts')

                    logging.info("PostURL %s", postUrl)                
                    PostCreateDate = ''
                    if dateElement:
                        PostCreateDate = dateElement.get_property('title').encode('utf8')
                        logging.info("Post Date %s", PostCreateDate)
                    else:
                        PostCreateDate = PostCreateDate.encode('utf8')
                        logging.info('Post Date Not Found')

                    postContent = ''

                    try:
                        postContentDiv = matchPost.find_element_by_tag_name('p')
                        postContent = postContentDiv.text.encode('utf8')
                        logging.info('Post Content: %s', postContent)
                    except:
                        postContent = postContent.encode('utf8')
                        logging.info('Post Content is missing')
                    
                    outputRecord = { 'Name': record['link'].decode('utf8'), 'Link to post': postUrl, 'Content of post' : postContent.decode('utf8'), 'Time post was created': PostCreateDate.decode('utf8') }

                    OutputJson.append(outputRecord)
            else:

                starttime = time.time()
                flag = 0
                matchPost = 0
                while (time.time() - starttime) < 30000 and flag == 0:
                    seemoreList = driver.find_elements_by_class_name('see_more_link')
                    print(len(seemoreList))
                    postList = driver.find_elements_by_class_name('_427x')
                    print("Page Posts - " + str(len(postList)))

                    now = len(postList)
                    first = second
                    second = third
                    third = fourth
                    fourth = fifth
                    fifth = sixth
                    sixth = seventh
                    seventh = now

                    if len(postList) > 100:
                        logging.info('Posts > 100')
                        break

                    if  now == first:
                        page = driver.find_element_by_tag_name('html')
                        page.send_keys(Keys.END)
                        time.sleep(3)
                        postList = driver.find_elements_by_class_name('_427x')
                        if len(postList) == first:
                            logging.info('no more posts')
                            break

                    for post in postList:
                        text = post.text.encode('utf-8')
                        innerflag = 0
                        for filItr in recordsFilters:
                            if text.find(filItr['name']) != -1:
                                innerflag = 1
                                print("post found")                        
                                break
                        if innerflag == 1:
                            flag = 1
                            matchPost = post
                            break
                    page = driver.find_element_by_tag_name('html')
                    page.send_keys(Keys.END)
                    print("Page loaded")
                
                if matchPost:
                    dateElement = 0
                    OptionElement = 0
                    try:
                        dateElement = matchPost.find_element_by_class_name('_5ptz')
                        OptionElement = matchPost.find_element_by_class_name('_4xev')
                    except:
                        logging.info('Date Option Element get error')

                    if OptionElement:
                        driver.execute_script("arguments[0].click();", OptionElement)
                        time.sleep(3)

                    try:
                        NCElements = driver.find_elements_by_class_name('_54nc')
                    except:
                        logging.info('54NC error')

                    postid = ''
                    for element in NCElements:
                        ajaxiattr = element.get_attribute('ajaxify')

                        ajaxifyLink = str(ajaxiattr)
                        if ajaxifyLink.find('ft_id') == -1:
                            continue
                        
                        ftpos = ajaxifyLink.find('ft_id') + 6
                        endpos = ajaxifyLink.find('&')

                        postid = ajaxifyLink[ftpos:endpos]

                    postUrl = record['link'].decode('utf-8') + '/posts/' + postid
                    postUrl = postUrl.replace('//posts', '/posts')
                    logging.info("PostURL %s", postUrl)
                    
                    PostCreateDate = ''
                    if dateElement:
                        PostCreateDate = dateElement.get_property('title').encode('utf8')
                        logging.info("Post Date %s", PostCreateDate)
                    else:
                        PostCreateDate = PostCreateDate.encode('utf8')
                        logging.info('Post Date Not Found')

                    postContent = ''

                    try:
                        postContentDiv = matchPost.find_element_by_tag_name('p')
                        postContent = postContentDiv.text.encode('utf8')
                        logging.info('Post Content: %s', postContent)
                    except:
                        postContent = postContent.encode('utf8')
                        logging.info('Post Content is missing')

                    try:
                        outputRecord = { 'Name': record['link'].decode('utf8'), 'Link to post': postUrl, 'Content of post' : postContent.decode('utf8'), 'Time post was created': PostCreateDate.decode('utf8') }
                        OutputJson.append(outputRecord)
                    except:
                        logging.info('Table Insert error')
        except:
            print(record['link'].decode('utf-8') + " - Error")
    driver.quit()
    

    recordsOutput = outputTable.get_all()
    recordFields = []

    for record in recordsOutput:
        fieldsElement = record['fields']
        id_value = record['id']
        outputTable.delete(id_value)

    for Ojson in OutputJson:
        outputTable.insert(Ojson)
    
    logging.info('Scraping Finished %d', len(OutputJson))