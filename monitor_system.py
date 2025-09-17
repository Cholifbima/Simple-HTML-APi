#!/usr/bin/env python3
"""
Script untuk monitoring sistem selama load testing
Menggunakan psutil untuk track CPU, Memory, dan resource lainnya
"""

import psutil
import time
import json
import os
import argparse
from datetime import datetime
import threading

class SystemMonitor:
    def __init__(self, interval=1, output_file='system_monitor.json'):
        self.interval = interval
        self.output_file = output_file
        self.running = False
        self.data = []
        
    def get_system_info(self):
        """Ambil informasi sistem saat ini"""
        try:
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            # Network info
            network = psutil.net_io_counters()
            
            # Process info (untuk Flask app)
            flask_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower() or 'flask' in proc.info['name'].lower() or 'locust' in proc.info['name'].lower():
                        flask_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                'timestamp': datetime.now().isoformat(),
                'epoch': time.time(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency_mhz': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total_gb': round(memory.total / 1024**3, 2),
                    'available_gb': round(memory.available / 1024**3, 2),
                    'used_gb': round(memory.used / 1024**3, 2),
                    'percent': memory.percent,
                    'swap_percent': swap.percent
                },
                'disk': {
                    'total_gb': round(disk.total / 1024**3, 2),
                    'free_gb': round(disk.free / 1024**3, 2),
                    'used_gb': round(disk.used / 1024**3, 2),
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': {
                    'total_count': len(psutil.pids()),
                    'test_related': flask_processes  # Flask + Locust processes
                }
            }
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def start_monitoring(self):
        """Mulai monitoring sistem"""
        print(f"🔍 Starting system monitoring...")
        print(f"📊 Interval: {self.interval} seconds")
        print(f"💾 Output file: {self.output_file}")
        print("📈 Monitoring CPU, Memory, Disk, Network...")
        print("⏹️  Press Ctrl+C to stop\n")
        
        self.running = True
        self.data = []
        
        try:
            while self.running:
                info = self.get_system_info()
                self.data.append(info)
                
                # Print real-time stats
                if 'error' not in info:
                    cpu = info['cpu']['percent']
                    memory = info['memory']['percent']
                    disk = info['disk']['percent']
                    
                    # Color coding for different levels
                    cpu_color = "🔴" if cpu > 80 else "🟡" if cpu > 60 else "🟢"
                    mem_color = "🔴" if memory > 80 else "🟡" if memory > 60 else "🟢"
                    
                    print(f"{info['timestamp'][:19]} | "
                          f"CPU: {cpu_color} {cpu:5.1f}% | "
                          f"MEM: {mem_color} {memory:5.1f}% | "
                          f"DISK: {disk:5.1f}% | "
                          f"Test Processes: {len(info['processes']['test_related'])}")
                else:
                    print(f"❌ Error: {info['error']}")
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitoring...")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring dan save data"""
        self.running = False
        
        if self.data:
            try:
                with open(self.output_file, 'w') as f:
                    json.dump(self.data, f, indent=2)
                print(f"💾 Data saved to {self.output_file}")
                print(f"📊 Total samples: {len(self.data)}")
                
                # Print summary
                self.print_summary()
                
            except Exception as e:
                print(f"❌ Error saving data: {e}")
    
    def print_summary(self):
        """Print summary statistik"""
        if not self.data:
            return
            
        print("\n" + "="*50)
        print("📊 MONITORING SUMMARY")
        print("="*50)
        
        # Filter out error entries
        valid_data = [d for d in self.data if 'error' not in d]
        
        if not valid_data:
            print("❌ No valid data collected")
            return
        
        # Calculate stats
        cpu_values = [d['cpu']['percent'] for d in valid_data]
        memory_values = [d['memory']['percent'] for d in valid_data]
        
        print(f"⏱️  Duration: {len(valid_data) * self.interval} seconds")
        print(f"📈 Samples: {len(valid_data)}")
        print()
        print("CPU Usage:")
        print(f"  📊 Average: {sum(cpu_values)/len(cpu_values):.1f}%")
        print(f"  📈 Maximum: {max(cpu_values):.1f}%")
        print(f"  📉 Minimum: {min(cpu_values):.1f}%")
        print()
        print("Memory Usage:")
        print(f"  📊 Average: {sum(memory_values)/len(memory_values):.1f}%")
        print(f"  📈 Maximum: {max(memory_values):.1f}%")
        print(f"  📉 Minimum: {min(memory_values):.1f}%")
        print()
        
        # System info
        last_sample = valid_data[-1]
        print("System Info:")
        print(f"  🖥️  CPU Cores: {last_sample['cpu']['count']}")
        print(f"  💾 Total RAM: {last_sample['memory']['total_gb']} GB")
        print(f"  💿 Total Disk: {last_sample['disk']['total_gb']} GB")
        print("="*50)

def main():
    parser = argparse.ArgumentParser(description='Monitor sistem selama load testing')
    parser.add_argument('-i', '--interval', type=float, default=1.0, 
                       help='Interval monitoring dalam detik (default: 1.0)')
    parser.add_argument('-o', '--output', type=str, default='system_monitor.json',
                       help='File output untuk data monitoring (default: system_monitor.json)')
    parser.add_argument('--summary-only', action='store_true',
                       help='Hanya tampilkan summary dari file yang sudah ada')
    
    args = parser.parse_args()
    
    monitor = SystemMonitor(interval=args.interval, output_file=args.output)
    
    if args.summary_only:
        if os.path.exists(args.output):
            try:
                with open(args.output, 'r') as f:
                    monitor.data = json.load(f)
                monitor.print_summary()
            except Exception as e:
                print(f"❌ Error loading file: {e}")
        else:
            print(f"❌ File {args.output} tidak ditemukan")
    else:
        monitor.start_monitoring()

if __name__ == "__main__":
    main()
