from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://training2.saveetha.in/mod/assign/view.php?id=24639&action=view")
input("Press Enter to continue...")
driver.quit()