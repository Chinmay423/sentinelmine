import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os

# Define the application URL (would be configured based on environment)
BASE_URL = os.environ.get("APP_URL", "http://localhost:3000")

class TestLoginWorkflow:
    """E2E tests for the login workflow using Selenium."""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Set up and tear down the WebDriver."""
        # Set up headless Chrome for CI environments
        chrome_options = Options()
        if os.environ.get("CI") == "true":
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Create the WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        # Return the driver
        yield driver
        
        # Tear down
        driver.quit()
    
    def test_successful_login(self, driver):
        """Test a successful login with valid credentials."""
        # Navigate to the login page
        driver.get(f"{BASE_URL}/login")
        
        # Wait for the login form to load
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Enter credentials
        username_input.send_keys("testuser")
        password_input.send_keys("password123")
        
        # Submit the form
        login_button.click()
        
        # Wait for redirect to dashboard after successful login
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{BASE_URL}/dashboard")
        )
        
        # Verify dashboard elements are visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".dashboard-header"))
        )
        
        # Verify user info is displayed in the UI
        user_info = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".user-profile"))
        )
        assert "testuser" in user_info.text
    
    def test_failed_login(self, driver):
        """Test login failure with invalid credentials."""
        # Navigate to the login page
        driver.get(f"{BASE_URL}/login")
        
        # Wait for the login form to load
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Enter invalid credentials
        username_input.send_keys("testuser")
        password_input.send_keys("wrongpassword")
        
        # Submit the form
        login_button.click()
        
        # Wait for error message to appear
        error_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".error-message"))
        )
        
        # Verify error message
        assert "Invalid credentials" in error_message.text
        
        # Verify we're still on the login page
        assert "/login" in driver.current_url
    
    def test_session_persistence(self, driver):
        """Test that the user session persists after successful login."""
        # First login
        driver.get(f"{BASE_URL}/login")
        
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_input.send_keys("testuser")
        password_input.send_keys("password123")
        login_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{BASE_URL}/dashboard")
        )
        
        # Now navigate to another protected page
        driver.get(f"{BASE_URL}/reports")
        
        # Verify we can access it without re-login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".reports-header"))
        )
        
        # Verify we were not redirected to login
        assert "/login" not in driver.current_url 