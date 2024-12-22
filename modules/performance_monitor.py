import psutil
import time
from typing import Dict, List
from collections import deque
import threading
import logging

class PerformanceMonitor:
    def __init__(self, history_size: int = 100):
        self.logger = logging.getLogger('canopus.performance')
        self.metrics_history = deque(maxlen=history_size)
        self.is_monitoring = False
        self.monitoring_thread = None
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0
        }
        
    def start_monitoring(self, interval: float = 1.0):
        """Start continuous performance monitoring"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
            
    def _monitoring_loop(self, interval: float):
        while self.is_monitoring:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                self._check_thresholds(metrics)
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                
    def collect_metrics(self) -> Dict:
        """Collect current system metrics"""
        return {
            'timestamp': time.time(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=0.1),
                'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'percent': psutil.disk_usage('/').percent
            }
        }

    def _check_thresholds(self, metrics: Dict):
        """Check if any metrics exceed defined thresholds"""
        alerts = []
        try:
            if metrics['cpu']['percent'] > self.alert_thresholds['cpu_percent']:
                alerts.append(f"CPU usage critical: {metrics['cpu']['percent']}%")
            
            if metrics['memory']['percent'] > self.alert_thresholds['memory_percent']:
                alerts.append(f"Memory usage critical: {metrics['memory']['percent']}%")
            
            if metrics['disk']['percent'] > self.alert_thresholds['disk_percent']:
                alerts.append(f"Disk usage critical: {metrics['disk']['percent']}%")
            
            if alerts:
                self.logger.warning(' | '.join(alerts))
                
        except KeyError as e:
            self.logger.error(f"Missing metric in threshold check: {e}")
        except Exception as e:
            self.logger.error(f"Error in threshold check: {e}")
