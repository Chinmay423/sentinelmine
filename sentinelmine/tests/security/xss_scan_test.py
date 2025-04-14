import pytest
import requests
import json
import subprocess
import os
import time
import logging
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL for testing
BASE_URL = os.environ.get("TEST_URL", "http://localhost:3000")

# OWASP ZAP settings
ZAP_PATH = os.environ.get("ZAP_PATH", "/opt/zaproxy/zap.sh")
ZAP_PORT = int(os.environ.get("ZAP_PORT", "8090"))
ZAP_API_KEY = os.environ.get("ZAP_API_KEY", "")

class TestXSSSecurity:
    """Test suite for XSS vulnerability scanning using OWASP ZAP."""
    
    @pytest.fixture(scope="class")
    def zap_instance(self):
        """Start OWASP ZAP as a daemon process for security scanning."""
        # Skip if we're not running security tests
        if os.environ.get("SKIP_SECURITY_TESTS", "false").lower() == "true":
            logger.info("Skipping security tests as per environment configuration.")
            pytest.skip("Security tests disabled via environment variable.")
        
        # Check if ZAP executable exists
        if not os.path.exists(ZAP_PATH):
            logger.error(f"ZAP executable not found at {ZAP_PATH}")
            pytest.skip(f"ZAP executable not found at {ZAP_PATH}")
        
        # Start ZAP as a daemon process
        try:
            logger.info("Starting OWASP ZAP...")
            cmd = [
                ZAP_PATH, 
                "-daemon", 
                "-port", str(ZAP_PORT), 
                "-config", f"api.key={ZAP_API_KEY}",
                "-config", "api.disablekey=false"
            ]
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # Give ZAP time to start
            time.sleep(10)
            
            # Check if ZAP started properly
            try:
                zap_status = requests.get(f"http://localhost:{ZAP_PORT}/JSON/core/view/version/", 
                                        params={"apikey": ZAP_API_KEY})
                if zap_status.status_code != 200:
                    logger.error(f"ZAP failed to start properly. Status code: {zap_status.status_code}")
                    pytest.skip("ZAP failed to start properly")
                
                logger.info(f"ZAP started successfully. Version: {zap_status.json()['version']}")
            except requests.exceptions.ConnectionError:
                logger.error("Could not connect to ZAP after startup")
                pytest.skip("Could not connect to ZAP after startup")
            
            # Return process for cleanup
            yield process
            
            # Clean up
            logger.info("Shutting down ZAP...")
            try:
                requests.get(f"http://localhost:{ZAP_PORT}/JSON/core/action/shutdown/", 
                           params={"apikey": ZAP_API_KEY})
                process.wait(timeout=10)
            except (requests.exceptions.ConnectionError, subprocess.TimeoutExpired):
                # Force kill if graceful shutdown fails
                process.kill()
            
        except Exception as e:
            logger.error(f"Failed to start ZAP: {str(e)}")
            pytest.skip(f"Failed to start ZAP: {str(e)}")
    
    def test_xss_active_scan(self, zap_instance):
        """Perform active XSS scanning on login and dashboard pages."""
        # Set up ZAP API client
        zap_api_url = f"http://localhost:{ZAP_PORT}/JSON"
        
        # Step 1: Access the target application
        logger.info(f"Accessing target application at {BASE_URL}")
        requests.get(
            f"{zap_api_url}/core/action/accessUrl/",
            params={
                "apikey": ZAP_API_KEY,
                "url": BASE_URL,
                "followRedirects": "true"
            }
        )
        
        # Step 2: Spider the target
        logger.info("Starting spider scan...")
        spider_response = requests.get(
            f"{zap_api_url}/spider/action/scan/",
            params={
                "apikey": ZAP_API_KEY,
                "url": BASE_URL,
                "maxChildren": "10",
                "recurse": "true",
                "contextName": "",
                "subtreeOnly": "false"
            }
        )
        
        # Get the spider scan ID
        spider_scan_id = spider_response.json()["scan"]
        logger.info(f"Spider scan ID: {spider_scan_id}")
        
        # Wait for spider to complete
        while True:
            spider_status = requests.get(
                f"{zap_api_url}/spider/view/status/",
                params={
                    "apikey": ZAP_API_KEY,
                    "scanId": spider_scan_id
                }
            ).json()["status"]
            
            if spider_status == "100":
                logger.info("Spider scan completed")
                break
                
            logger.info(f"Spider progress: {spider_status}%")
            time.sleep(5)
        
        # Step 3: Active scan for XSS vulnerabilities
        logger.info("Starting active scan for XSS vulnerabilities...")
        active_scan_response = requests.get(
            f"{zap_api_url}/ascan/action/scan/",
            params={
                "apikey": ZAP_API_KEY,
                "url": BASE_URL,
                "recurse": "true",
                "inScopeOnly": "false",
                "scanPolicyName": "Cross-Site Scripting (XSS)"
            }
        )
        
        # Get the active scan ID
        active_scan_id = active_scan_response.json()["scan"]
        logger.info(f"Active scan ID: {active_scan_id}")
        
        # Wait for active scan to complete
        while True:
            active_scan_status = requests.get(
                f"{zap_api_url}/ascan/view/status/",
                params={
                    "apikey": ZAP_API_KEY,
                    "scanId": active_scan_id
                }
            ).json()["status"]
            
            if active_scan_status == "100":
                logger.info("Active scan completed")
                break
                
            logger.info(f"Active scan progress: {active_scan_status}%")
            time.sleep(5)
        
        # Step 4: Get XSS alerts
        xss_alerts = requests.get(
            f"{zap_api_url}/alert/view/alerts/",
            params={
                "apikey": ZAP_API_KEY,
                "baseurl": BASE_URL,
                "risk": "High"
            }
        ).json()["alerts"]
        
        # Log found XSS vulnerabilities
        xss_count = len(xss_alerts)
        logger.info(f"Found {xss_count} potential XSS vulnerabilities")
        
        for i, alert in enumerate(xss_alerts, 1):
            logger.warning(f"XSS #{i}: {alert['url']} - {alert['name']}")
            logger.warning(f"Description: {alert['description']}")
            logger.warning(f"Solution: {alert['solution']}")
            logger.warning("---")
        
        # Assert no high-risk XSS vulnerabilities
        assert xss_count == 0, f"Found {xss_count} potential XSS vulnerabilities" 