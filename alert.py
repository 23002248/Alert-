from selenium import webdriver
import time

driver = webdriver.Chrome()

driver.get("https://www.saucedemo.com/")


driver.execute_script(
    "alert('Welcome to SauceDemo');"
)

time.sleep(2)


alert = driver.switch_to.alert


print("Alert Message:", alert.text)

alert.accept()



print("Alert accepted successfully")

input("Press Enter to close...")
driver.quit()