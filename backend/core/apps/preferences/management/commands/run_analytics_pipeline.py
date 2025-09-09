"""
Django management command to run and manage the analytics data pipeline
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.cache import cache
from celery import group, chain
import json
import time

from apps.preferences.tasks import (
    process_analytics_event,
    batch_process_events,
    analyze_user_behavior,
    update_user_segments,
    generate_analytics_reports,
    cleanup_old_analytics_data,
    update_recommendation_models,
    monitor_system_performance,
    privacy_compliance_audit,
    data_quality_assessment
)


class Command(BaseCommand):
    help = 'Run and manage the Gradvy analytics data processing pipeline'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=[
                'start', 'stop', 'status', 'test', 'process-events', 
                'analyze-users', 'update-segments', 'generate-reports',
                'cleanup', 'update-models', 'monitor', 'audit',
                'quality-check', 'simulate-data'
            ],
            help='Action to perform'
        )
        
        parser.add_argument(
            '--user-id',
            type=str,
            help='User ID for specific operations'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Batch size for processing operations'
        )
        
        parser.add_argument(
            '--simulate-count',
            type=int,
            default=10,
            help='Number of events to simulate'
        )
        
        parser.add_argument(
            '--queue',
            type=str,
            default='default',
            help='Celery queue to use'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'start':
            self.start_pipeline()
        elif action == 'stop':
            self.stop_pipeline()
        elif action == 'status':
            self.show_status()
        elif action == 'test':
            self.test_pipeline()
        elif action == 'process-events':
            self.process_events(options['batch_size'])
        elif action == 'analyze-users':
            self.analyze_users(options.get('user_id'))
        elif action == 'update-segments':
            self.update_segments()
        elif action == 'generate-reports':
            self.generate_reports()
        elif action == 'cleanup':
            self.cleanup_data()
        elif action == 'update-models':
            self.update_models()
        elif action == 'monitor':
            self.monitor_system()
        elif action == 'audit':
            self.privacy_audit()
        elif action == 'quality-check':
            self.quality_check()
        elif action == 'simulate-data':
            self.simulate_data(options['simulate_count'])

    def start_pipeline(self):
        """Start the analytics pipeline"""
        self.stdout.write("🚀 Starting Gradvy Analytics Pipeline...")
        
        # Set pipeline status
        cache.set('pipeline_status', 'running', timeout=None)
        cache.set('pipeline_start_time', timezone.now().isoformat(), timeout=None)
        
        # Start monitoring
        monitor_task = monitor_system_performance.delay()
        
        self.stdout.write(
            self.style.SUCCESS("✅ Pipeline started successfully!")
        )
        self.stdout.write(f"Monitor task ID: {monitor_task.id}")

    def stop_pipeline(self):
        """Stop the analytics pipeline"""
        self.stdout.write("🛑 Stopping Gradvy Analytics Pipeline...")
        
        # Set pipeline status
        cache.set('pipeline_status', 'stopped', timeout=None)
        cache.set('pipeline_stop_time', timezone.now().isoformat(), timeout=None)
        
        self.stdout.write(
            self.style.SUCCESS("✅ Pipeline stopped successfully!")
        )

    def show_status(self):
        """Show pipeline status and metrics"""
        self.stdout.write("📊 Gradvy Analytics Pipeline Status")
        self.stdout.write("=" * 50)
        
        # Pipeline status
        status = cache.get('pipeline_status', 'unknown')
        start_time = cache.get('pipeline_start_time')
        
        self.stdout.write(f"Status: {status}")
        if start_time:
            self.stdout.write(f"Started: {start_time}")
        
        # System metrics
        system_metrics = cache.get('system_metrics')
        if system_metrics:
            self.stdout.write("\n🔧 System Metrics:")
            sys_data = system_metrics.get('system', {})
            self.stdout.write(f"  CPU: {sys_data.get('cpu_percent', 0)}%")
            self.stdout.write(f"  Memory: {sys_data.get('memory_percent', 0)}%")
            self.stdout.write(f"  Disk: {sys_data.get('disk_usage', 0)}%")
        
        # Database metrics
        if system_metrics and 'database' in system_metrics:
            db_data = system_metrics['database']
            self.stdout.write("\n🗄️ Database Metrics:")
            self.stdout.write(f"  Total Users: {db_data.get('total_user_preferences', 0)}")
            self.stdout.write(f"  Active (24h): {db_data.get('recent_activity_24h', 0)}")
            self.stdout.write(f"  Activity Rate: {db_data.get('activity_rate', 0):.1f}%")
        
        # Pipeline metrics
        if system_metrics and 'pipeline' in system_metrics:
            pipeline_data = system_metrics['pipeline']
            self.stdout.write("\n⚙️ Pipeline Metrics:")
            self.stdout.write(f"  Pending Events: {pipeline_data.get('pending_events', 0)}")
            self.stdout.write(f"  Processed (24h): {pipeline_data.get('processed_events_24h', 0)}")
            self.stdout.write(f"  Failed Tasks: {pipeline_data.get('failed_tasks', 0)}")
        
        # Alerts
        alerts = cache.get('system_alerts', [])
        if alerts:
            self.stdout.write("\n⚠️ Active Alerts:")
            for alert in alerts:
                severity_color = self.style.ERROR if alert['severity'] == 'critical' else self.style.WARNING
                self.stdout.write(
                    severity_color(f"  {alert['type']}: {alert['value']}% (threshold: {alert['threshold']}%)")
                )

    def test_pipeline(self):
        """Test pipeline functionality"""
        self.stdout.write("🧪 Testing Analytics Pipeline...")
        
        # Test event processing
        test_event = {
            'user_id': 'test_user_123',
            'event_type': 'test_event',
            'properties': {
                'test_property': 'test_value',
                'timestamp': timezone.now().isoformat()
            },
            'timestamp': timezone.now().isoformat()
        }
        
        # Process test event
        task = process_analytics_event.delay(test_event)
        result = task.get(timeout=30)  # Wait up to 30 seconds
        
        if result['status'] == 'processed':
            self.stdout.write(
                self.style.SUCCESS("✅ Event processing test passed!")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Event processing test failed: {result}")
            )
        
        # Test system monitoring
        monitor_task = monitor_system_performance.delay()
        monitor_result = monitor_task.get(timeout=30)
        
        if 'system' in monitor_result:
            self.stdout.write(
                self.style.SUCCESS("✅ System monitoring test passed!")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ System monitoring test failed: {monitor_result}")
            )

    def process_events(self, batch_size):
        """Process pending events"""
        self.stdout.write(f"⚡ Processing events (batch size: {batch_size})...")
        
        # Get pending events from cache or simulate
        pending_events = cache.get('pending_events', [])
        
        if not pending_events:
            self.stdout.write("ℹ️ No pending events found. Use 'simulate-data' to create test events.")
            return
        
        # Process in batches
        batches = [pending_events[i:i + batch_size] for i in range(0, len(pending_events), batch_size)]
        
        for i, batch in enumerate(batches):
            task = batch_process_events.delay(batch)
            self.stdout.write(f"Batch {i + 1}/{len(batches)} queued: {task.id}")
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Queued {len(batches)} batches for processing")
        )

    def analyze_users(self, user_id):
        """Analyze user behavior"""
        if user_id:
            self.stdout.write(f"🔍 Analyzing user {user_id}...")
            task = analyze_user_behavior.delay(user_id)
            self.stdout.write(f"Analysis task ID: {task.id}")
        else:
            self.stdout.write("🔍 Starting batch user analysis...")
            # Analyze all users with recent activity
            from apps.preferences.models import UserPreference
            recent_users = UserPreference.objects(
                last_activity_date__gte=timezone.now() - timezone.timedelta(days=7)
            ).limit(100)
            
            tasks = []
            for user_pref in recent_users:
                task = analyze_user_behavior.delay(user_pref.user_id)
                tasks.append(task.id)
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Queued analysis for {len(tasks)} users")
            )

    def update_segments(self):
        """Update user segments"""
        self.stdout.write("👥 Updating user segments...")
        task = update_user_segments.delay()
        self.stdout.write(f"Task ID: {task.id}")

    def generate_reports(self):
        """Generate analytics reports"""
        self.stdout.write("📋 Generating analytics reports...")
        task = generate_analytics_reports.delay()
        result = task.get(timeout=60)
        
        if 'total_users' in result:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Report generated - Total users: {result['total_users']}, "
                    f"Active today: {result['active_users_today']}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Report generation failed: {result}")
            )

    def cleanup_data(self):
        """Clean up old analytics data"""
        self.stdout.write("🧹 Cleaning up old analytics data...")
        task = cleanup_old_analytics_data.delay()
        result = task.get(timeout=120)
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Cleanup completed: {result}")
        )

    def update_models(self):
        """Update ML recommendation models"""
        self.stdout.write("🤖 Updating ML recommendation models...")
        task = update_recommendation_models.delay()
        self.stdout.write(f"Task ID: {task.id}")
        
        # Wait for completion and show result
        try:
            result = task.get(timeout=300)  # 5 minute timeout
            if result['status'] == 'completed':
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Models updated - {result['users_processed']} users, "
                        f"{result['clusters_created']} clusters"
                    )
                )
            else:
                self.stdout.write(f"ℹ️ Model update result: {result}")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Model update failed: {str(e)}")
            )

    def monitor_system(self):
        """Monitor system performance"""
        self.stdout.write("📈 Monitoring system performance...")
        task = monitor_system_performance.delay()
        result = task.get(timeout=30)
        
        if 'system' in result:
            sys_data = result['system']
            self.stdout.write(f"CPU: {sys_data['cpu_percent']}%")
            self.stdout.write(f"Memory: {sys_data['memory_percent']}%")
            self.stdout.write(f"Disk: {sys_data['disk_usage']}%")
            
            self.stdout.write(
                self.style.SUCCESS("✅ System monitoring completed")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ System monitoring failed: {result}")
            )

    def privacy_audit(self):
        """Run privacy compliance audit"""
        self.stdout.write("🔒 Running privacy compliance audit...")
        task = privacy_compliance_audit.delay()
        result = task.get(timeout=60)
        
        if 'users_audited' in result:
            self.stdout.write(f"Users audited: {result['users_audited']}")
            self.stdout.write(f"Data cleaned: {result['data_cleaned']}")
            self.stdout.write(f"Issues found: {len(result['issues_found'])}")
            
            for issue in result['issues_found']:
                self.stdout.write(
                    self.style.WARNING(f"  - {issue['type']}: {issue['description']}")
                )
            
            self.stdout.write(
                self.style.SUCCESS("✅ Privacy audit completed")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Privacy audit failed: {result}")
            )

    def quality_check(self):
        """Run data quality assessment"""
        self.stdout.write("📊 Running data quality assessment...")
        task = data_quality_assessment.delay()
        result = task.get(timeout=60)
        
        if 'total_users' in result:
            self.stdout.write(f"Total users: {result['total_users']}")
            self.stdout.write(f"Quality issues: {len(result['data_quality_issues'])}")
            
            for issue in result['data_quality_issues']:
                self.stdout.write(
                    self.style.WARNING(
                        f"  - {issue['type']}: {issue['count']} users "
                        f"({issue.get('percentage', 0):.1f}%)"
                    )
                )
            
            if result['recommendations']:
                self.stdout.write("\nRecommendations:")
                for rec in result['recommendations']:
                    self.stdout.write(f"  • {rec}")
            
            self.stdout.write(
                self.style.SUCCESS("✅ Data quality assessment completed")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Data quality assessment failed: {result}")
            )

    def simulate_data(self, count):
        """Simulate test analytics events"""
        self.stdout.write(f"🎭 Simulating {count} analytics events...")
        
        import random
        from datetime import timedelta
        
        event_types = [
            'course_interaction', 'learning_session', 'quiz_attempt',
            'search', 'button_click', 'form_submit'
        ]
        
        simulated_events = []
        
        for i in range(count):
            event = {
                'user_id': f'sim_user_{random.randint(1, 100)}',
                'event_type': random.choice(event_types),
                'properties': {
                    'session_id': f'sim_session_{random.randint(1, 20)}',
                    'course_id': f'course_{random.randint(1, 50)}',
                    'action': random.choice(['view', 'enroll', 'complete']),
                    'score': random.randint(60, 100),
                    'duration': random.randint(300, 3600),
                    'engagement_level': random.choice(['low', 'medium', 'high'])
                },
                'timestamp': (timezone.now() - timedelta(
                    minutes=random.randint(0, 1440)  # Random time in last 24 hours
                )).isoformat()
            }
            simulated_events.append(event)
        
        # Store events for processing
        cache.set('pending_events', simulated_events, timeout=3600)
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Generated {count} simulated events")
        )
        self.stdout.write("Use 'process-events' command to process them")