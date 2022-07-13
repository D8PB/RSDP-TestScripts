import time

import selenium.webdriver.chrome.service
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from awsLogon import awslogon


chromePath = "C:/JUMP/chromedriver.exe"  # Latest chrome driver, download from the web.
inventoryPath = "C:/Users/D8PB/OneDrive - PGE/Documents/inventory_test1.csv"
metadataPath = "C:/Users/D8PB/OneDrive - PGE/Documents/metadata_test1.csv"


# Adds a string in the form "32 KB" or "5 MB" to an integer number of KB, returns int.
def addFileSize(totalKB, sizeString):
    logStr = str(totalKB) + " + " + sizeString
    size = sizeString.split(" ")
    if size[1] == "KB":
        if "." in size[0]:
            totalKB += int(size[0].split(".")[0])
        else:
            totalKB += int(size[0])
    elif size[1] == "MB":
        splitSize = size[0].split(".")
        totalKB += (int(splitSize[0]) * 1000) + (int(splitSize[1]) * 100)
    logStr += " = " + str(totalKB)
    print(logStr)
    return totalKB


chromeService = selenium.webdriver.chrome.service.Service(chromePath)
driver = webdriver.Chrome(service=chromeService)
awslogon(driver)

defaultDatastorePath = "https://s3.console.aws.amazon.com/s3/buckets/" \
                       "remote-sensing-datastore-dev?region=us-west-2&prefix=%s&showversions=false"
defaultProcessedPath = "https://s3.console.aws.amazon.com/s3/buckets/" \
                       "remote-sensing-processed-files-dev?region=us-west-2&prefix=%s&showversions=false"

inventoryFile = open(inventoryPath, encoding='utf-8-sig')
metadataFile = open(metadataPath, encoding='utf-8-sig')
csvreader = csv.reader(inventoryFile, delimiter=',')
log = open("log.txt", "w")

circuitIdenFileCounts = {}
circuitIdenThumbnailCounts = {}
circuitFileCounts = {}
circuitIdenFileSizes = {}
circuitFileSizes = {}
batchFileSize = [0, 0]  # In kilobytes

# Each dict defined above in the form {string: [int, int]},
# where the first int is the staging size/count and the second int is the processed size/count.
# i represents the index: 0 for staging, 1 for processed.
# [OUTDATED]: If current file is a thumbnail (i.e. "if thumb"), only the circuitIdenThumbnailCounts should be updated.

# Increments some value in given dict, and starts by adding the k/v pair to the dict if it's not present.
def increaseDictCount(someDict, someKey, i):
    if someKey not in someDict.keys():
        if i == 0:
            someDict[someKey] = [1, 0]
        else:
            someDict[someKey] = [0, 1]
    else:
        someDict[someKey][i] += 1

# Adds some storage (moreSize, in form "32 KB" or "5 MB") to given dict,
# and starts by adding k/v pair to dict if not present.
def increaseDictFileSize(someDict, someKey, moreSize, i):
    if someKey not in someDict.keys():
        if i == 0:
            someDict[someKey] = [addFileSize(0, moreSize), 0]
        else:
            someDict[someKey] = [0, addFileSize(0, moreSize)]
    else:
        someDict[someKey][i] = addFileSize(someDict[someKey][i], moreSize)


# Used to ignore non JPG / JPEG files
def isFileJPG(filename):
    return len(filename) > 4 and (filename[-4:].lower() == ".jpg" or filename[-5:].lower() == ".jpeg")


for i in range(2):
    if i == 1:
        csvreader = csv.reader(metadataFile, delimiter=',')
    firstLine = True
    for csvLine in csvreader:
        thumb = False # Is the current file a thumbnail?
        if firstLine and i == 0:  # Skipping the first line in inventory since it's just the column names
            firstLine = False
            continue
        if i == 0:
            stagingPath = csvLine[2].split('/')
            if "__" in stagingPath[3]:
                circuit = stagingPath[3].split("__")[0]
            else:
                circuit = stagingPath[3]
            circuitIden = circuit + "/" + stagingPath[4]
            filename = stagingPath[5]
            if isFileJPG(filename):
                thumb = True
            driver.get(defaultDatastorePath % csvLine[2])  # stagingPath without the split
        else:
            print(csvLine[0])
            stagingPath = csvLine[0].split('/')
            circuit = stagingPath[2]
            if len(stagingPath) >= 9 and stagingPath[5] == 'Rasters':  # Thumbnail path is longer than non-thumb
                circuitIden = circuit + "/" + stagingPath[7]
                if stagingPath[8] == "thumbnail": # TODO - any other thumbnail circuit location / name?
                    thumb = True
            else:
                circuitIden = "" # TODO - What to do if file doesn't have a circuitIden in Aerial/Rasters/Oblique?
            if not thumb:
                driver.get(defaultProcessedPath % csvLine[0])

        if len(circuitIden) > 0:
            if i == 0 or not thumb:
                increaseDictCount(circuitIdenFileCounts, circuitIden, i)
            if thumb:
                increaseDictCount(circuitIdenThumbnailCounts, circuitIden, i)
        if thumb and i == 1:
            continue  # Thumbnails don't count towards total file count or file size.
        increaseDictCount(circuitFileCounts, circuit, i)

        try:
            fileSize = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@class='key-value-group__group']/div/div[4]"))).text.split('\n')[1]
        except TimeoutException:
            # driver.quit()
            print("File size not located")
            exit(1)
        batchFileSize[i] = addFileSize(batchFileSize[i], fileSize)

        if len(circuitIden) > 0:
            increaseDictFileSize(circuitIdenFileSizes, circuitIden, fileSize, i)
        increaseDictFileSize(circuitFileSizes, circuit, fileSize, i)

inventoryFile.close()
metadataFile.close()

for circuit in circuitFileCounts:
    print(circuit, " count = ", circuitFileCounts[circuit],  circuitFileSizes[circuit])
for circuitIden in circuitIdenFileCounts:
    print(circuitIden,  " count = ", circuitIdenFileCounts[circuitIden], "sizes = ", circuitIdenFileSizes[circuitIden])
for circuitIden in circuitIdenThumbnailCounts:
    print(circuitIden, " thumbnail count = ", circuitIdenThumbnailCounts[circuitIden])


printedSummary = False
allDicts = [circuitFileCounts, circuitFileSizes, circuitIdenFileCounts,
            circuitIdenFileSizes, circuitIdenThumbnailCounts]
dictNames = ["Circuit file count", "Circuit file size", "Circuit ID file count",
             "Circuit ID file size", "Circuit ID thumbnail count"]
for i in range(5):
    for j in allDicts[i]:
        val = allDicts[i][j]
        if val[0] != val[1]:
            if not printedSummary:
                printedSummary = True
                log.write("Discrepancies exist.\n")
            log.write(dictNames[i]
                      + " discrepancy: {} has {} in staging vs. {} in processed\n".format(j, val[0], val[1]))

if not printedSummary:
    log.write("All file counts and sizes match.")



