from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

driver = webdriver.Chrome()

driver.get("https://vinothqaacademy.com/demo-site/")
driver.maximize_window()

time.sleep(3)

# Get all input fields belonging to Registration Form
inputs = driver.find_elements(
    By.XPATH,
    "//h3[contains(normalize-space(),'Registration Form')]/following::input"
)

# -----------------------------
# 1. First Name
# -----------------------------
inputs[0].send_keys("STEPHEN")

# -----------------------------
# 2. Last Name
# -----------------------------
inputs[1].send_keys("RAJ")

# -----------------------------
# 3. Gender - Male
# -----------------------------
inputs[2].click()

# -----------------------------
# 4. Course - Selenium WebDriver
# -----------------------------
inputs[5].click()

# -----------------------------
# 5. Street Address
# -----------------------------
inputs[11].send_keys("123 Main Street")

# -----------------------------
# 6. Apt / Suite
# -----------------------------
inputs[12].send_keys("A101")

# -----------------------------
# 7. City
# -----------------------------
inputs[13].send_keys("Chennai")

# -----------------------------
# 8. State
# -----------------------------
inputs[14].send_keys("Tamil Nadu")

# -----------------------------
# 9. Postal / Zip Code
# -----------------------------
inputs[15].send_keys("600001")

# -----------------------------
# 10. Email
# -----------------------------
inputs[16].send_keys("stephen@gmail.com")

# -----------------------------
# 11. Date of Demo
# -----------------------------
inputs[17].send_keys("10/06/26")

time.sleep(5)