import time

import selenium.webdriver.chrome.service
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

chromePath = "C:/JUMP/chromedriver.exe"
chromeService = selenium.webdriver.chrome.service.Service(chromePath)
driver = webdriver.Chrome(service=chromeService)

driver.get("https://itiamping.cloud.pge.com/idp/startSSO.ping?PartnerSpId=urn%3Aamazon%3Awebservices%3A739846873405")

username = driver.find_element(by=By.ID, value="username")
password = driver.find_element(by=By.ID, value="password")
f = open("C:/JUMP/awsLogon.txt", "r")
usernameText = f.readline().strip()
passwordText = f.readline().strip()
username.send_keys(usernameText)
password.send_keys(passwordText)
password.send_keys("\n")
f.close()

try:
    qaRole = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
        (By.ID, "arn:aws:iam::739846873405:role/AWS-A1837-QA-GISCOE_Audit")))
except TimeoutException:
    driver.quit()
    exit(1)
else:
    qaRole.click()
    driver.find_element(by=By.ID, value="signin_button").click()

try:
    navUsernameMenu = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
        (By.ID, "nav-usernameMenu")))
except TimeoutException:
    driver.quit()
    exit(1)
else:
    navUsernameMenu.click()
    driver.find_element(by=By.LINK_TEXT, value="Switch role").click()

try:
    switchRole = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
        (By.ID, "switchrole_firstrun_button")))
except TimeoutException:
    driver.quit()
    exit(1)
else:
    switchRole.click()

try:
    account = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id='input_account']/div[1]/input")))
except TimeoutException:
    driver.quit()
    exit(1)
else:
    account.send_keys("719465802387")
    driver.find_element(by=By.ID, value="roleName").send_keys("GISCOE_Audit")
    driver.find_element(by=By.ID, value="displayName").send_keys("GISCOE QA- Audit\n")

f = open("P:/My documents/testManifest.csv", encoding='utf-8-sig')
csvreader = csv.reader(f, delimiter=',')
log = open("log.txt", "w")
for csvLine in csvreader:
    # firstLine = csvreader.__next__()
    driver.get('https://s3.console.aws.amazon.com/s3/buckets/remote-sensing-datastore-qa?region=us-west-2&prefix='
               + csvLine[0] + '/&showversions=false')
    time.sleep(5)
    file_objects = driver.find_elements(
        by=By.XPATH, value="//*[@id='objects-table']/div/div[@class='awsui-table-container']/table/tbody/tr")
    filesize_list = []
    for obj in file_objects:
        size = obj.find_element(by=By.XPATH, value="./td[5]/span/span[@class='column-Size']/div")
        filesize_list.append(size.text)

    print("Expected objects: " + csvLine[1])
    print("Actual objects: " + str(len(file_objects)))
    print(filesize_list)
    log.write(csvLine[0] + ": " + csvLine[1] + " expected count vs "+ str(len(file_objects)) + " actual count\n")
f.close()

# Log results in another csv
# remote-sensing processed is the process bucket. looking at the staging bucket.
# multiple cases
# check file size as well
# one more test case: if I access processed bucket, there will be a thumbnails folder, need to match count of thumbnails
# to make sure there's 1 folder for each circuit, 1 image for each image in the manifest file (count should match)
# only generated for jpgs.
