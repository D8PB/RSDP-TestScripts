import selenium.webdriver.chrome.service
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def awslogon(driver):
    driver.get(
        "https://itiamping.cloud.pge.com/idp/startSSO.ping?PartnerSpId=urn:amazon:webservices:739846873405LanIDRoles")

    username = driver.find_element(by=By.ID, value="username")
    # password = driver.find_element(by=By.ID, value="password")
    password = driver.find_element(by=By.ID, value="passcode")
    f = open("C:/JUMP/awsLogon.txt", "r")
    usernameText = f.readline().strip()
    # passwordText = input("Enter passcode from SecurID: ")
    username.send_keys(usernameText)
    password.click()
    # password.send_keys(passwordText)
    # password.send_keys("\n")
    f.close()

    try:
        # qaRole = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
        #    (By.ID, "arn:aws:iam::739846873405:role/AWS-A1837-QA-GISCOE_Audit")))
        devRole = WebDriverWait(driver, 45).until(EC.presence_of_element_located(
            (By.ID, "arn:aws:iam::739846873405:role/AWS-A1837-Dev-GISCOE_Audit")))
    except TimeoutException:
        driver.quit()
        exit(1)
    else:
        devRole.click()
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
        # account.send_keys("719465802387") #QA
        account.send_keys("412551746953")
        driver.find_element(by=By.ID, value="roleName").send_keys("GISCOE_Audit")
        driver.find_element(by=By.ID, value="displayName").send_keys("GISCOE Dev- Audit\n")


# Easy launch AWS for testing
if __name__ == "__main__":
    print("Easy launch for testing")
    chromePath = "C:/JUMP/chromedriver.exe"
    chromeService = selenium.webdriver.chrome.service.Service(chromePath)
    driver = webdriver.Chrome(service=chromeService)
    awslogon(driver)
