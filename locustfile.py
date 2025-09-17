# Load Testing dengan Locust untuk HTML File Server
# Dioptimasi untuk UI cantik + request control yang lebih baik

import time
import random
import json
import os
from locust import HttpUser, task, between, events
from locust.env import Environment
import psutil

class BaseUser(HttpUser):
    """Base user class dengan konfigurasi dasar"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """Method yang dipanggil saat user mulai"""
        # Test koneksi awal
        response = self.client.get("/")
        if response.status_code != 200:
            print(f"⚠️ Warning: Homepage tidak accessible (status: {response.status_code})")

class LightLoadUser(HttpUser):
    """User untuk light load testing - fokus file kecil"""
    weight = 3
    wait_time = between(2, 4)
    
    @task(40)
    def test_homepage(self):
        """Test akses homepage"""
        self.client.get("/", name="Homepage")
    
    @task(35)
    def test_small_file(self):
        """Test download file kecil (10KB)"""
        self.client.get("/api/html/small", name="Small File (10KB)")
    
    @task(20)
    def test_api_info(self):
        """Test API info endpoint"""
        self.client.get("/api/info", name="API Info")
    
    @task(5)
    def test_api_status(self):
        """Test API status endpoint"""
        self.client.get("/api/status", name="API Status")

class MediumLoadUser(HttpUser):
    """User untuk medium load testing - mix file size"""
    weight = 4
    wait_time = between(1, 3)
    
    @task(25)
    def test_homepage(self):
        self.client.get("/", name="Homepage")
    
    @task(25)
    def test_small_file(self):
        self.client.get("/api/html/small", name="Small File (10KB)")
    
    @task(25)
    def test_medium_file(self):
        """Test download file medium (100KB)"""
        self.client.get("/api/html/medium", name="Medium File (100KB)")
    
    @task(15)
    def test_large_file(self):
        """Test download file besar (1MB)"""
        self.client.get("/api/html/large", name="Large File (1MB)")
    
    @task(10)
    def test_api_endpoints(self):
        endpoint = random.choice(["/api/info", "/api/status"])
        self.client.get(endpoint, name="API Endpoints")

class HeavyLoadUser(HttpUser):
    """User untuk heavy load testing - fokus file besar"""
    weight = 3
    wait_time = between(0.5, 2)
    
    @task(20)
    def test_homepage(self):
        self.client.get("/", name="Homepage")
    
    @task(15)
    def test_small_file(self):
        self.client.get("/api/html/small", name="Small File (10KB)")
    
    @task(20)
    def test_medium_file(self):
        self.client.get("/api/html/medium", name="Medium File (100KB)")
    
    @task(25)
    def test_large_file(self):
        self.client.get("/api/html/large", name="Large File (1MB)")
    
    @task(15)
    def test_xlarge_file(self):
        """Test download file sangat besar (5MB)"""
        self.client.get("/api/html/xlarge", name="XLarge File (5MB)")
    
    @task(5)
    def test_xxlarge_file(self):
        """Test download file terbesar (10MB)"""
        self.client.get("/api/html/xxlarge", name="XXLarge File (10MB)")

class StressTestUser(HttpUser):
    """User untuk stress testing - maksimal beban"""
    weight = 2
    wait_time = between(0.5, 1.5)
    
    @task(15)
    def test_homepage(self):
        self.client.get("/", name="Homepage")
    
    @task(10)
    def test_small_file(self):
        self.client.get("/api/html/small", name="Small File (10KB)")
    
    @task(15)
    def test_medium_file(self):
        self.client.get("/api/html/medium", name="Medium File (100KB)")
    
    @task(20)
    def test_large_file(self):
        self.client.get("/api/html/large", name="Large File (1MB)")
    
    @task(20)
    def test_xlarge_file(self):
        self.client.get("/api/html/xlarge", name="XLarge File (5MB)")
    
    @task(15)
    def test_xxlarge_file(self):
        self.client.get("/api/html/xxlarge", name="XXLarge File (10MB)")
    
    @task(5)
    def test_random_endpoints(self):
        endpoint = random.choice(["/api/info", "/api/status"])
        self.client.get(endpoint, name="API Endpoints")

# Global variables untuk tracking
request_count = 0
target_requests = None
test_start_time = None

# Event listeners untuk monitoring dan kontrol
@events.request.add_listener
def request_handler(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """Handler untuk setiap request - untuk menghitung total requests"""
    global request_count, target_requests
    
    if exception:
        print(f"❌ Request failed: {name} - {exception}")
    else:
        request_count += 1
        
        # Auto-stop jika mencapai target (untuk exact request count)
        if target_requests and request_count >= target_requests:
            print(f"🎯 Target {target_requests} requests achieved! Stopping test...")
            # Note: Auto-stop bisa diimplementasi dengan custom runner script

@events.test_start.add_listener
def test_start_handler(environment, **kwargs):
    """Handler saat test dimulai"""
    global test_start_time, request_count
    test_start_time = time.time()
    request_count = 0
    
    print("=" * 60)
    print("🚀 LOCUST LOAD TEST STARTED")
    print("=" * 60)
    print(f"🌐 Target: {environment.host}")
    print(f"👥 Users: {environment.parsed_options.num_users if hasattr(environment, 'parsed_options') else 'Unknown'}")
    print(f"📈 Spawn Rate: {environment.parsed_options.spawn_rate if hasattr(environment, 'parsed_options') else 'Unknown'}/s")
    print("📊 Open Web UI: http://localhost:8089")
    print("=" * 60)
    
    # Save sistem info
    system_info = get_system_stats()
    save_test_info({
        'test_start': time.time(),
        'system_info': system_info,
        'test_config': {
            'host': environment.host,
            'users': getattr(environment.parsed_options, 'num_users', None),
            'spawn_rate': getattr(environment.parsed_options, 'spawn_rate', None)
        }
    })

@events.test_stop.add_listener
def test_stop_handler(environment, **kwargs):
    """Handler saat test selesai"""
    global test_start_time, request_count
    test_duration = time.time() - test_start_time if test_start_time else 0
    
    print("=" * 60)
    print("🏁 LOCUST LOAD TEST COMPLETED")
    print("=" * 60)
    print(f"⏱️ Duration: {test_duration:.1f} seconds")
    print(f"📊 Total Requests: {request_count}")
    print(f"📈 Average RPS: {request_count/test_duration:.2f}" if test_duration > 0 else "📈 Average RPS: N/A")
    print("📁 Check Web UI for detailed results")
    print("=" * 60)
    
    # Save final stats
    final_stats = get_system_stats()
    save_test_info({
        'test_end': time.time(),
        'test_duration': test_duration,
        'total_requests': request_count,
        'final_system_stats': final_stats
    })

def get_system_stats():
    """Get current system resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': round(memory.available / 1024**3, 2),
            'memory_total_gb': round(memory.total / 1024**3, 2),
            'disk_percent': disk.percent,
            'timestamp': time.time()
        }
    except Exception as e:
        return {'error': str(e)}

def save_test_info(data, filename='locust_test_info.json'):
    """Save test information to file"""
    try:
        # Load existing data
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}
        
        # Update with new data
        existing_data.update(data)
        
        # Save back to file
        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=2)
    except Exception as e:
        print(f"Error saving test info: {e}")

# Utility function untuk custom test scenarios
def set_target_requests(count):
    """Set target request count untuk auto-stop"""
    global target_requests
    target_requests = count
    print(f"🎯 Target requests set to: {count}")

# Task untuk test spesifik requirement dosen
class RequirementTestUser(HttpUser):
    """
    User khusus untuk testing requirement dosen
    Bisa dikonfigurasi untuk exact request count
    """
    weight = 1
    wait_time = between(1, 2)
    
    @task
    def test_mixed_endpoints(self):
        """Test random endpoint dengan distribusi yang seimbang"""
        endpoints = [
            ("/", "Homepage"),
            ("/api/html/small", "Small File (10KB)"),
            ("/api/html/medium", "Medium File (100KB)"),
            ("/api/html/large", "Large File (1MB)"),
            ("/api/info", "API Info"),
            ("/api/status", "API Status")
        ]
        
        endpoint, name = random.choice(endpoints)
        self.client.get(endpoint, name=name)

