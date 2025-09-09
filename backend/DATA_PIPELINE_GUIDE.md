# Gradvy Analytics Data Pipeline Guide

## Overview

The Gradvy Analytics Data Pipeline is a comprehensive real-time data processing system built with Celery that handles user behavior analysis, machine learning model updates, privacy compliance, and system monitoring.

## Architecture

```
Frontend Events → API → Celery Tasks → MongoDB → ML Models → Insights
                         ↓
                   Redis Cache ← System Monitoring
```

## Components

### 1. Real-time Event Processing
- `process_analytics_event`: Processes individual user events
- `batch_process_events`: Handles bulk event processing
- `update_realtime_metrics`: Updates real-time user metrics

### 2. Behavioral Analysis
- `analyze_user_behavior`: Comprehensive user behavior analysis
- `check_user_anomalies`: Detects unusual behavior patterns
- `process_user_anomalies`: Takes action on detected anomalies

### 3. Machine Learning
- `update_recommendation_models`: Updates ML models for personalization
- `generate_content_recommendations`: Creates personalized recommendations
- `update_user_segments`: Updates user clustering/segmentation

### 4. System Monitoring
- `monitor_system_performance`: Monitors CPU, memory, disk usage
- `privacy_compliance_audit`: Ensures GDPR compliance
- `data_quality_assessment`: Checks data quality and integrity

### 5. Maintenance
- `cleanup_old_analytics_data`: Removes old data per retention policies
- `generate_analytics_reports`: Creates daily/periodic reports

## Setup

### 1. Install Dependencies

```bash
# Add to your requirements.txt
pip install -r analytics_requirements.txt
```

### 2. Configure Redis

The pipeline uses Redis as both cache and message broker. Ensure Redis is running:

```bash
# Docker (recommended for development)
docker run -d -p 6380:6379 --name gradvy-redis redis:latest

# Or install locally
sudo apt-get install redis-server
```

### 3. Start Celery Workers

```bash
# Start main worker
celery -A core worker --loglevel=info

# Start worker with specific queues
celery -A core worker --loglevel=info -Q realtime,analytics,ml,reports

# Start beat scheduler (for periodic tasks)
celery -A core beat --loglevel=info

# Optional: Start Flower for monitoring (development)
celery -A core flower
```

## Usage

### Management Command

Use the Django management command to interact with the pipeline:

```bash
# Start the pipeline
python manage.py run_analytics_pipeline start

# Check status
python manage.py run_analytics_pipeline status

# Test the pipeline
python manage.py run_analytics_pipeline test

# Process pending events
python manage.py run_analytics_pipeline process-events --batch-size 100

# Analyze specific user
python manage.py run_analytics_pipeline analyze-users --user-id user123

# Generate reports
python manage.py run_analytics_pipeline generate-reports

# Update ML models
python manage.py run_analytics_pipeline update-models

# Run privacy audit
python manage.py run_analytics_pipeline audit

# Simulate test data
python manage.py run_analytics_pipeline simulate-data --simulate-count 50
```

### Programmatic Usage

```python
from apps.preferences.tasks import process_analytics_event

# Process a single event
event_data = {
    'user_id': 'user123',
    'event_type': 'course_interaction',
    'properties': {
        'course_id': 'course456',
        'action': 'enroll',
        'timestamp': datetime.now().isoformat()
    },
    'timestamp': datetime.now().isoformat()
}

task = process_analytics_event.delay(event_data)
result = task.get()
```

## Event Types

### Supported Event Types

1. **course_interaction**
   - Properties: `course_id`, `action` (view/enroll/complete), `duration`
   - Updates: engagement score, preferred content types

2. **learning_session**
   - Properties: `duration`, `completion_rate`, `content_type`
   - Updates: learning velocity, engagement score

3. **quiz_attempt**
   - Properties: `score`, `total_questions`, `time_taken`
   - Updates: dropout risk score, performance metrics

4. **search**
   - Properties: `query`, `results_count`, `filters`
   - Updates: search patterns, content preferences

5. **button_click/link_click/form_submit**
   - Properties: `element_id`, `page_url`, `session_id`
   - Updates: engagement score, UI interaction patterns

### Event Properties

All events should include:
- `user_id`: User identifier
- `event_type`: Type of event
- `properties`: Event-specific data
- `timestamp`: ISO format timestamp
- `session_id`: Session identifier (optional)

## Queue Configuration

### Queues and Priorities

- **realtime**: High-priority real-time event processing
- **analytics**: User behavior analysis and insights
- **ml**: Machine learning model updates
- **reports**: Report generation and data export
- **maintenance**: Data cleanup and system maintenance
- **compliance**: Privacy audits and compliance checks
- **monitoring**: System health monitoring

### Queue Assignment

```python
# Process event in real-time queue
process_analytics_event.apply_async(
    args=[event_data],
    queue='realtime',
    priority=9
)

# Update ML models in ML queue
update_recommendation_models.apply_async(
    queue='ml',
    priority=5
)
```

## Monitoring

### System Metrics

The pipeline provides comprehensive monitoring:

```python
from django.core.cache import cache

# Get current system metrics
metrics = cache.get('system_metrics')
print(f"CPU: {metrics['system']['cpu_percent']}%")
print(f"Memory: {metrics['system']['memory_percent']}%")

# Check for alerts
alerts = cache.get('system_alerts', [])
for alert in alerts:
    print(f"Alert: {alert['type']} - {alert['value']}%")
```

### Flower Dashboard

For development, use Flower to monitor Celery tasks:

```bash
celery -A core flower
# Visit http://localhost:5555
```

## Privacy Compliance

### GDPR Features

1. **Consent Management**: Respects user privacy settings
2. **Data Retention**: Automatic cleanup of old data
3. **Right to be Forgotten**: Clean user data on request
4. **Privacy Audit**: Regular compliance checks

### Privacy Settings

```python
user_pref = UserPreference.objects(user_id=user_id).first()

# Check consent before processing
if user_pref.has_analytics_consent():
    process_analytics_event.delay(event_data)
else:
    # Skip processing or use minimal data
    pass
```

## Performance Optimization

### Batch Processing

Use batch processing for high-volume scenarios:

```python
from apps.preferences.tasks import batch_process_events

# Process multiple events at once
events = [event1, event2, event3, ...]
batch_process_events.delay(events)
```

### Caching Strategy

The pipeline uses multi-level caching:

1. **Redis Cache**: Real-time metrics and session data
2. **MongoDB**: Persistent user behavior data
3. **Memory Cache**: Frequently accessed insights

### Resource Management

```python
# Task with resource limits
@shared_task(bind=True, time_limit=300, soft_time_limit=240)
def resource_intensive_task(self):
    # Task implementation
    pass
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Reduce batch sizes
   - Increase worker processes
   - Monitor for memory leaks

2. **Task Failures**
   - Check Redis connection
   - Verify MongoDB connectivity
   - Review task logs

3. **Slow Processing**
   - Scale workers horizontally
   - Optimize database queries
   - Use appropriate queue priorities

### Debugging

```bash
# Check worker logs
celery -A core worker --loglevel=debug

# Monitor specific queue
celery -A core events --task=apps.preferences.tasks.process_analytics_event

# Purge queue
celery -A core purge -Q realtime
```

## Best Practices

### Event Design

1. Keep event payloads small
2. Use consistent timestamp formats
3. Include session IDs for correlation
4. Validate data before processing

### Task Design

1. Make tasks idempotent
2. Handle failures gracefully
3. Use appropriate retry policies
4. Monitor task execution times

### Privacy

1. Always check consent before processing
2. Anonymize data when possible
3. Regular privacy audits
4. Document data retention policies

## Development Workflow

### Testing Pipeline

```bash
# 1. Simulate test data
python manage.py run_analytics_pipeline simulate-data --simulate-count 10

# 2. Process the events
python manage.py run_analytics_pipeline process-events

# 3. Check status
python manage.py run_analytics_pipeline status

# 4. Run analysis
python manage.py run_analytics_pipeline analyze-users
```

### Adding New Event Types

1. Update `process_analytics_event` task
2. Add event-specific processing function
3. Update behavioral pattern calculations
4. Add tests and documentation

### Scaling

1. **Horizontal Scaling**: Add more worker processes
2. **Queue Separation**: Use dedicated queues for different task types
3. **Database Optimization**: Add appropriate indexes
4. **Caching**: Cache frequently accessed data

## Maintenance

### Regular Tasks

1. **Daily**: Run privacy audits and reports
2. **Weekly**: Update ML models and user segments
3. **Monthly**: Clean old data and optimize database
4. **Quarterly**: Review and update privacy policies

### Monitoring Checklist

- [ ] CPU and memory usage
- [ ] Queue lengths and processing times
- [ ] Database performance
- [ ] Privacy compliance metrics
- [ ] ML model accuracy
- [ ] Data quality scores

## Support

For issues or questions about the data pipeline:

1. Check the logs: `celery -A core worker --loglevel=debug`
2. Monitor system metrics: `python manage.py run_analytics_pipeline status`
3. Run diagnostics: `python manage.py run_analytics_pipeline test`
4. Review privacy compliance: `python manage.py run_analytics_pipeline audit`