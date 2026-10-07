from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs, unquote
import time

# ─────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────
SEARCH_KEYWORD = "wireless bluetooth headphones"   # <- change product here
WAIT_TIMEOUT   = 15

# CSS selectors tried in order to find title text inside a result card
TITLE_SELECTORS = [
    "h2 a span",
    "h2 span",
    "[data-cy='title-recipe-title'] span",
    "span.a-text-normal",
]

# CSS selectors tried in order to find the anchor tag inside a result card
LINK_SELECTORS = [
    "h2 a",
    "a.a-link-normal[href*='/dp/']",
    "a.a-link-normal.s-underline-text",
]

# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────
def find_first_elem(card, selectors):
    """Return the first non-empty element matched by any selector."""
    for sel in selectors:
        try:
            for el in card.find_elements(By.CSS_SELECTOR, sel):
                if el.text.strip():
                    return el
        except Exception:
            pass
    return None


def clean_amazon_url(href):
    """
    Convert an Amazon /sspa/click?... redirect URL into a clean
    https://www.amazon.in/dp/<ASIN> URL.
    Returns the original href unchanged if it already looks like a dp URL.
    """
    if not href:
        return href
    if "sspa/click" in href:
        try:
            params  = parse_qs(urlparse(href).query)
            raw_url = unquote(params.get("url", [""])[0])  # e.g. /product/dp/B0CQXMXJC5/...
            # strip query string from the embedded url
            path = raw_url.split("?")[0].split("#")[0]
            return "https://www.amazon.in" + path
        except Exception:
            return href
    return href


# ─────────────────────────────────────────
#  1. LAUNCH BROWSER & OPEN AMAZON
# ─────────────────────────────────────────
driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, WAIT_TIMEOUT)

print("[*] Opening Amazon...")
driver.get("https://www.amazon.in")

# ─────────────────────────────────────────
#  2. SEARCH FOR A PRODUCT
# ─────────────────────────────────────────
print(f"[*] Searching for: {SEARCH_KEYWORD}")

search_box = wait.until(
    EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
)
search_box.clear()
search_box.send_keys(SEARCH_KEYWORD)
search_box.send_keys(Keys.RETURN)

# ─────────────────────────────────────────
#  3. WAIT FOR SEARCH RESULTS
# ─────────────────────────────────────────
print("[*] Waiting for search results...")
wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
    )
)
time.sleep(2)

# ─────────────────────────────────────────
#  4. FIND FIRST VALID PRODUCT
#     Skips cards that have no title/link, collects the clean /dp/ URL
# ─────────────────────────────────────────
cards = driver.find_elements(
    By.CSS_SELECTOR,
    "div[data-component-type='s-search-result']"
)
print(f"[+] Found {len(cards)} product cards.")

product_title = None
product_url   = None

for i, card in enumerate(cards):
    title_el = find_first_elem(card, TITLE_SELECTORS)
    link_el  = find_first_elem(card, LINK_SELECTORS)

    if not (title_el and link_el):
        continue

    raw_href = link_el.get_attribute("href") or ""
    clean_url = clean_amazon_url(raw_href)

    # Make sure we resolved to a real product page
    if "/dp/" not in clean_url:
        continue

    product_title = title_el.text.strip()
    product_url   = clean_url
    print(f"[+] Chosen product (card index {i}):")
    print(f"    Title : {product_title}")
    print(f"    URL   : {product_url}")
    break

if not product_url:
    print("[!] ERROR: No valid product found. Exiting.")
    driver.quit()
    raise SystemExit(1)

# ─────────────────────────────────────────
#  5. NAVIGATE DIRECTLY TO THE PRODUCT PAGE
#     Using driver.get() avoids sspa redirect issues
# ─────────────────────────────────────────
print("[*] Navigating to the product page...")
driver.get(product_url)

# ─────────────────────────────────────────
#  6. READ PRODUCT DETAILS
# ─────────────────────────────────────────
wait.until(EC.presence_of_element_located((By.ID, "productTitle")))

page_title = driver.find_element(By.ID, "productTitle").text.strip()
print(f"\n[+] Product Page Loaded!")
print(f"    Title : {page_title}")

try:
    price = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
    print(f"    Price : Rs.{price}")
except Exception:
    print("    Price : Not available on this page")

# ─────────────────────────────────────────
#  7. ADD PRODUCT TO CART
# ─────────────────────────────────────────
print("[*] Adding product to cart...")

try:
    # Click the 'Add to Cart' button (Amazon's standard id)
    add_to_cart_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "add-to-cart-button"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_to_cart_btn)
    time.sleep(0.5)
    add_to_cart_btn.click()
    print("[+] Clicked 'Add to Cart' button.")

    # Amazon sometimes shows a popup/modal after adding to cart.
    # Close it if it appears so we can verify the cart.
    try:
        no_thanks_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-action='a-popover-close'], #attachSiNoCoverage, #siNoCoverage-btn")
            )
        )
        no_thanks_btn.click()
        print("[+] Dismissed add-on / protection-plan popup.")
    except Exception:
        pass  # No popup appeared — that's fine

    # Confirm the cart badge updated
    try:
        cart_count = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.ID, "nav-cart-count"))
        )
        print(f"[+] Product added to cart! Cart count: {cart_count.text}")
    except Exception:
        print("[+] Product added to cart! (cart badge not detectable)")

except Exception as e:
    print(f"[!] Could not add to cart: {e}")

# ─────────────────────────────────────────
#  8. DONE
# ─────────────────────────────────────────
print("\n[+] Done! Keeping browser open for 10 seconds...")
time.sleep(10)

driver.quit()
print("[*] Browser closed.")
