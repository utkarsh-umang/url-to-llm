from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import logging
import time
import random
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_parser.log'),
        logging.StreamHandler()
    ]
)


connect_button_selectors = [
    # Most specific selector first
    "button.artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view",
    # Using the specific aria-label
    "button[aria-label*='Invite'][aria-label*='to connect']",
    # Looking for the span with "Connect" text
    "//button[.//span[@class='artdeco-button__text'][text()='Connect']]",
    # Using the data-test-icon attribute
    "//button[.//svg[@data-test-icon='connect-small']]",
    # Simplest fallback
    "//button[.//span[text()='Connect']]"
    # Original selectors as fallback
    "button[aria-label*='connect']",
    "button[aria-label*='Connect']"
]

def setup_driver():
    """Set up and configure Brave browser WebDriver for macOS"""
    try:
        options = webdriver.ChromeOptions()
        # Essential anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        # Set Brave binary location for macOS
        options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        # Add random user agent
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        # Create and return the driver
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1280, 720)
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize driver: {str(e)}")
        return None
    

def login_to_linkedin(driver, email, password):
    """Log into LinkedIn"""
    try:
        driver.get('https://www.linkedin.com/login')
        # Wait for and fill email
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        email_field.send_keys(email)
        # Fill password
        password_field = driver.find_element(By.ID, 'password')
        password_field.send_keys(password)
        # Click login
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        # Wait for login to complete
        time.sleep(random.uniform(3, 5))
        return True
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        return False


def check_connection_status(driver, profile_url):
    """Check if already connected with the profile"""
    try:
        driver.get(profile_url)
        time.sleep(random.uniform(2, 4))
        # Look for connection status
        connect_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
                "[aria-label*='Connect'],[aria-label*='connect'],[aria-label*='Following'],[aria-label*='Pending']"))
        )
        button_text = connect_button.get_attribute('aria-label').lower()
        if "following" in button_text or "connected" in button_text:
            return "Connected"
        elif "pending" in button_text:
            return "Pending"
        else:
            return "Not Connected"
    except Exception as e:
        logging.error(f"Error checking connection status: {str(e)}")
        return "Error"


def send_connection_request(driver, profile_url, daily_requests_sent, max_daily_requests=15):
    """Send connection request"""
    try:
        if daily_requests_sent >= max_daily_requests:
            return "Daily Limit Reached"

        time.sleep(random.uniform(2, 4))
        
        print("Looking for connect button...")
        connect_button = None
        for selector in connect_button_selectors:
            try:
                print(f"Trying selector: {selector}")
                if selector.startswith("//"):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                # Print all found elements for debugging
                print(f"Found {len(elements)} elements with selector {selector}")
                for elem in elements:
                    print(f"Element text: {elem.text}")
                    print(f"Element aria-label: {elem.get_attribute('aria-label')}")
                    print(f"Element class: {elem.get_attribute('class')}")
                
                if elements:
                    connect_button = elements[0]
                    print(f"Successfully found connect button with selector: {selector}")
                    break
            except Exception as e:
                print(f"Error with selector {selector}: {str(e)}")
                continue

        if not connect_button:
            print("Connect button not found")
            return "Connect button not found"

        print("Found connect button, attempting to click...")
        
        # Ensure button is in view
        driver.execute_script("arguments[0].scrollIntoView(true);", connect_button)
        time.sleep(1)

        # Try multiple click methods
        try:
            print("Attempting regular click...")
            connect_button.click()
        except Exception as e1:
            print(f"Regular click failed: {str(e1)}")
            try:
                print("Attempting JavaScript click...")
                driver.execute_script("arguments[0].click();", connect_button)
            except Exception as e2:
                print(f"JavaScript click failed: {str(e2)}")
                try:
                    print("Attempting ActionChains click...")
                    actions = ActionChains(driver)
                    actions.move_to_element(connect_button).click().perform()
                except Exception as e3:
                    print(f"ActionChains click failed: {str(e3)}")
                    raise Exception("All click methods failed")

        time.sleep(1)
        
        # Look for "Send without a note" button in the modal
        send_without_note_selectors = [
            "button[aria-label*='Send invitation without a note']",
            "//button[contains(text(), 'Send without a note')]",
            "//button[contains(@aria-label, 'Send without a note')]"
        ]
        
        send_button = None
        for selector in send_without_note_selectors:
            try:
                if selector.startswith("//"):
                    send_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))  # Changed to element_to_be_clickable
                    )
                else:
                    send_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))  # Changed to element_to_be_clickable
                    )
                if send_button:
                    print(f"Found 'Send without a note' button using selector: {selector}")
                    break
            except:
                continue
                
        if not send_button:
            print("Send without note button not found")
            return "Send button not found"
            
        # Try multiple ways to click the send button
        try:
            send_button.click()
        except:
            try:
                driver.execute_script("arguments[0].click();", send_button)
            except:
                actions = ActionChains(driver)
                actions.move_to_element(send_button).click().perform()

        time.sleep(2)
        
        return "Request Sent"
        
    except Exception as e:
        print(f"Error sending connection request: {str(e)}")
        return f"Error: {str(e)}"


def validate_profile(driver, profile_url, first_name, last_name):
    """
    Validate if the LinkedIn profile matches the given name by parsing page source
    """
    try:
        time.sleep(random.uniform(2, 4))
        page_source = driver.page_source
        
        if '"firstName":"' not in page_source or '"lastName":"' not in page_source:
            return False, "Could not find name data in profile"

        pos = 0
        while True:
            try:
                # Find next firstName
                first_name_index = page_source.index('"firstName":"', pos) + len('"firstName":"')
                first_name_end = page_source.index('"', first_name_index)
                profile_first_name = page_source[first_name_index:first_name_end].lower()
                
                # Find next lastName
                last_name_index = page_source.index('"lastName":"', pos) + len('"lastName":"')
                last_name_end = page_source.index('"', last_name_index)
                profile_last_name = page_source[last_name_index:last_name_end].lower()
                
                # Skip if it matches your profile
                if profile_first_name == "steven" or profile_last_name == "currid":
                    pos = last_name_end  # Move position past this pair
                    continue
                
                # Clean input names
                expected_first_name = first_name.strip().lower()
                expected_last_name = last_name.strip().lower()
                
                print(f"Expected: First='{expected_first_name}', Last='{expected_last_name}'")
                print(f"Found: First='{profile_first_name}', Last='{profile_last_name}'")
                
                if (profile_first_name == expected_first_name and 
                    profile_last_name == expected_last_name):
                    return True, "Profile validated successfully"
                else:
                    return False, f"Name mismatch: Expected '{expected_first_name} {expected_last_name}', found '{profile_first_name} {profile_last_name}'"
                    
            except ValueError:
                return False, "Could not find matching profile name"
            
    except Exception as e:
        print(f"Error in profile validation: {str(e)}")
        return False, f"Error validating profile: {str(e)}"