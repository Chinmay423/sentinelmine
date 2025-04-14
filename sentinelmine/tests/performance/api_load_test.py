from locust import HttpUser, task, between
import json
import random
import time

class APILoadTest(HttpUser):
    """Locust load testing class for API endpoints."""
    
    # Wait time between tasks (1-5 seconds)
    wait_time = between(1, 5)
    
    # Login credentials - would be pulled from environment in real tests
    username = "testuser"
    password = "password123"
    
    # JWT token for authenticated requests
    token = None
    
    def on_start(self):
        """Execute when user starts - login to get JWT token."""
        response = self.client.post(
            "/api/auth/login",
            json={
                "username": self.username,
                "password": self.password
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            self.token = result.get("token")
            if not self.token:
                self.environment.runner.quit()
                raise Exception("Login failed - no token received")
        else:
            self.environment.runner.quit()
            raise Exception(f"Login failed with status code {response.status_code}")
    
    @task(5)  # Higher weight means this task is executed more frequently
    def get_dashboard_metrics(self):
        """Get dashboard metrics - frequent operation."""
        if not self.token:
            return
            
        self.client.get(
            "/api/dashboard/metrics",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(3)
    def get_recent_alerts(self):
        """Get recent alerts - medium frequency operation."""
        if not self.token:
            return
            
        self.client.get(
            "/api/alerts/recent",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def predict_threat(self):
        """Predict threat level - less frequent operation."""
        if not self.token:
            return
            
        # Generate random test data for prediction
        test_data = {
            "source_ip": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "destination_ip": f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "packet_size": random.randint(64, 8192),
            "protocol": random.choice(["TCP", "UDP", "ICMP", "HTTP"]),
            "port": random.choice([22, 80, 443, 3306, 8080, 8443]),
            "duration": random.randint(1, 600),
            "frequency": random.randint(1, 100),
            "bytes_transferred": random.randint(100, 10000000),
            "time_of_day": random.uniform(0, 24),
            "day_of_week": random.randint(0, 6)
        }
        
        self.client.post(
            "/api/predictions/threat",
            json=test_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def generate_report(self):
        """Generate report - least frequent, resource-intensive operation."""
        if not self.token:
            return
            
        # Parameters for report generation
        report_params = {
            "start_date": "2023-01-01",
            "end_date": "2023-01-31",
            "report_type": random.choice(["summary", "detailed", "executive"]),
            "include_metrics": True,
            "include_predictions": True,
            "include_alerts": True
        }
        
        self.client.post(
            "/api/reports/generate",
            json=report_params,
            headers={"Authorization": f"Bearer {self.token}"}
        )

    def on_stop(self):
        """Execute when user stops - logout."""
        if self.token:
            self.client.post(
                "/api/auth/logout",
                headers={"Authorization": f"Bearer {self.token}"}
            )


# To run this test:
# locust -f api_load_test.py --host=http://localhost:5000

# Command line example for headless mode with 100 users, 10 users spawned per second, run for 5 minutes:
# locust -f api_load_test.py --host=http://localhost:5000 --headless -u 100 -r 10 --run-time 5m 