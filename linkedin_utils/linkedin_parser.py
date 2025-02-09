from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time
import os
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

def initialize_driver():
    """Initialize and configure the Chrome WebDriver"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-notifications')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Uncomment for headless mode
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize driver: {str(e)}")
        return None

def login_to_linkedin(driver):
    """Log in to LinkedIn using credentials from environment variables"""
    try:
        load_dotenv()
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            raise ValueError("LinkedIn credentials not found in environment variables")
        
        driver.get('https://www.linkedin.com/login')
        wait = WebDriverWait(driver, 10)
        
        # Wait for and fill in email
        email_field = wait.until(EC.presence_of_element_located((By.ID, 'username')))
        email_field.send_keys(email)
        
        # Fill in password
        password_field = driver.find_element(By.ID, 'password')
        password_field.send_keys(password)
        
        # Click login button
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Wait for login to complete
        time.sleep(3)
        
        return True
    except Exception as e:
        logging.error(f"Failed to login to LinkedIn: {str(e)}")
        return False

def validate_profile(driver, profile_url, first_name, last_name):
    """
    Validate if the LinkedIn profile matches the given name
    
    Args:
        driver: Selenium WebDriver instance
        profile_url (str): LinkedIn profile URL
        first_name (str): Expected first name
        last_name (str): Expected last name
        
    Returns:
        tuple: (is_valid, message)
    """
    try:
        driver.get(profile_url)
        wait = WebDriverWait(driver, 10)
        time.sleep(2)  # Allow time for profile to load
        
        # Wait for and get the name element
        name_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-heading-xlarge"))
        )
        profile_name = name_element.text.strip().lower()
        
        # Clean and compare names
        expected_name = f"{first_name} {last_name}".lower()
        
        if profile_name == expected_name:
            return True, "Profile validated successfully"
        else:
            return False, f"Name mismatch: Expected '{expected_name}', found '{profile_name}'"
            
    except TimeoutException:
        return False, "Profile page took too long to load"
    except NoSuchElementException:
        return False, "Could not find name element on profile"
    except Exception as e:
        return False, f"Error validating profile: {str(e)}"

def process_profiles(profile_data):
    """
    Process a batch of LinkedIn profiles
    
    Args:
        profile_data (list): List of dictionaries containing profile URLs and names
        
    Returns:
        list: List of validation results
    """
    driver = None
    results = []
    
    try:
        driver = initialize_driver()
        if not driver:
            raise Exception("Failed to initialize web driver")
            
        if not login_to_linkedin(driver):
            raise Exception("Failed to login to LinkedIn")
            
        for profile in profile_data:
            is_valid, message = validate_profile(
                driver,
                profile['url'],
                profile['first_name'],
                profile['last_name']
            )
            
            results.append({
                'url': profile['url'],
                'is_valid': is_valid,
                'message': message,
                'row_index': profile.get('row_index')
            })
            
            # Add delay between profile checks
            time.sleep(2)
            
    except Exception as e:
        logging.error(f"Batch processing failed: {str(e)}")
    finally:
        if driver:
            driver.quit()
        
    return results