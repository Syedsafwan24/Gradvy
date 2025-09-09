"""
Real-time Data Processing Pipeline
Celery tasks for comprehensive user data collection and analysis
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

from celery import shared_task, group, chain
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db.models import Q, F, Count, Avg, Max, Min
from mongoengine import Q as MongoQ

from .models import UserPreference
from apps.gradvy_auth.models import User

logger = logging.getLogger(__name__)

# =============================================================================
# REAL-TIME EVENT PROCESSING TASKS
# =============================================================================

@shared_task(bind=True, retry_backoff=True, max_retries=3)
def process_analytics_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process individual analytics events in real-time
    Updates user behavioral patterns and triggers further analysis
    """
    try:
        user_id = event_data.get('user_id')
        if not user_id:
            logger.warning(f"Analytics event missing user_id: {event_data}")
            return {'status': 'skipped', 'reason': 'no_user_id'}

        # Get user preference document
        user_pref = UserPreference.objects(user_id=str(user_id)).first()
        if not user_pref:
            logger.warning(f"UserPreference not found for user {user_id}")
            return {'status': 'error', 'reason': 'user_not_found'}

        # Check privacy consent
        if not user_pref.has_analytics_consent():
            return {'status': 'skipped', 'reason': 'no_consent'}

        event_type = event_data.get('event_type')
        properties = event_data.get('properties', {})
        timestamp = datetime.fromisoformat(event_data.get('timestamp', datetime.now().isoformat()))

        # Update behavioral patterns based on event type
        behavioral_update = {}
        
        if event_type == 'course_interaction':
            behavioral_update.update(process_course_interaction_event(user_pref, properties))
        elif event_type == 'learning_session':
            behavioral_update.update(process_learning_session_event(user_pref, properties))
        elif event_type == 'quiz_attempt':
            behavioral_update.update(process_quiz_event(user_pref, properties))
        elif event_type == 'search':
            behavioral_update.update(process_search_event(user_pref, properties))
        elif event_type in ['button_click', 'link_click', 'form_submit']:
            behavioral_update.update(process_ui_interaction_event(user_pref, properties))

        # Apply behavioral updates
        if behavioral_update:
            user_pref.update_behavioral_patterns(**behavioral_update)

        # Trigger downstream processing
        if should_trigger_analysis(event_type, user_pref):
            # Schedule comprehensive analysis
            analyze_user_behavior.delay(str(user_id))

        # Update real-time metrics
        update_realtime_metrics.delay(str(user_id), event_type, properties)

        logger.info(f"Processed event {event_type} for user {user_id}")
        return {
            'status': 'processed',
            'event_type': event_type,
            'user_id': user_id,
            'updates_applied': len(behavioral_update),
            'timestamp': timestamp.isoformat()
        }

    except Exception as exc:
        logger.error(f"Error processing analytics event: {str(exc)}", exc_info=True)
        self.retry(countdown=60 * (self.request.retries + 1))

@shared_task
def batch_process_events(event_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process multiple events in batch for efficiency
    Groups events by user and processes them together
    """
    try:
        user_events = defaultdict(list)
        
        # Group events by user
        for event in event_batch:
            user_id = event.get('user_id')
            if user_id:
                user_events[user_id].append(event)

        processed_count = 0
        results = []

        for user_id, events in user_events.items():
            try:
                # Process all events for this user
                user_result = process_user_event_batch(user_id, events)
                results.append(user_result)
                processed_count += len(events)
            except Exception as e:
                logger.error(f"Error processing batch for user {user_id}: {str(e)}")

        return {
            'status': 'completed',
            'total_events': len(event_batch),
            'processed_events': processed_count,
            'users_affected': len(user_events),
            'results': results
        }

    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def process_user_event_batch(user_id: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process all events for a single user in one go"""
    user_pref = UserPreference.objects(user_id=user_id).first()
    if not user_pref or not user_pref.has_analytics_consent():
        return {'user_id': user_id, 'status': 'skipped', 'reason': 'no_consent_or_user'}

    # Aggregate behavioral changes
    behavioral_changes = defaultdict(list)
    session_data = []

    for event in events:
        event_type = event.get('event_type')
        properties = event.get('properties', {})
        
        if event_type == 'course_interaction':
            changes = process_course_interaction_event(user_pref, properties)
            for key, value in changes.items():
                behavioral_changes[key].append(value)
        
        # Add session tracking
        if 'session_id' in properties:
            session_data.append({
                'session_id': properties['session_id'],
                'timestamp': event.get('timestamp'),
                'event_type': event_type
            })

    # Apply aggregated changes
    for key, values in behavioral_changes.items():
        if key == 'engagement_score':
            # Calculate average engagement
            user_pref.update_behavioral_patterns(engagement_score=np.mean(values))
        elif key == 'learning_velocity':
            # Update velocity with latest measurement
            user_pref.update_behavioral_patterns(learning_velocity=values[-1])

    return {
        'user_id': user_id,
        'status': 'processed',
        'events_processed': len(events),
        'behavioral_updates': len(behavioral_changes)
    }

# =============================================================================
# BEHAVIORAL ANALYSIS TASKS
# =============================================================================

@shared_task(bind=True, retry_backoff=True, max_retries=2)
def analyze_user_behavior(self, user_id: str) -> Dict[str, Any]:
    """
    Comprehensive analysis of user behavior patterns
    Updates AI insights and personalization metrics
    """
    try:
        user_pref = UserPreference.objects(user_id=user_id).first()
        if not user_pref:
            return {'status': 'error', 'reason': 'user_not_found'}

        # Perform comprehensive analysis
        analysis_results = {}

        # 1. Learning Pattern Analysis
        learning_patterns = analyze_learning_patterns(user_pref)
        analysis_results['learning_patterns'] = learning_patterns

        # 2. Engagement Analysis
        engagement_analysis = analyze_engagement_patterns(user_pref)
        analysis_results['engagement'] = engagement_analysis

        # 3. Risk Assessment
        risk_assessment = calculate_dropout_risk(user_pref)
        analysis_results['risk_assessment'] = risk_assessment

        # 4. Personalization Updates
        personalization_updates = generate_personalization_updates(user_pref, analysis_results)
        analysis_results['personalization'] = personalization_updates

        # Update user preferences with insights
        user_pref.update_ai_insights(analysis_results)

        # Cache results for quick access
        cache_key = f"user_analysis_{user_id}"
        cache.set(cache_key, analysis_results, timeout=3600)  # 1 hour

        logger.info(f"Completed behavioral analysis for user {user_id}")
        return {
            'status': 'completed',
            'user_id': user_id,
            'insights_generated': len(analysis_results),
            'timestamp': datetime.now().isoformat()
        }

    except Exception as exc:
        logger.error(f"Error analyzing user behavior: {str(exc)}", exc_info=True)
        self.retry(countdown=300)  # Retry after 5 minutes

@shared_task
def update_realtime_metrics(user_id: str, event_type: str, properties: Dict[str, Any]):
    """
    Update real-time user metrics and trigger alerts if needed
    """
    try:
        # Update Redis-based real-time counters
        cache_key_prefix = f"metrics:{user_id}"
        
        # Daily activity counters
        today = datetime.now().date()
        daily_key = f"{cache_key_prefix}:daily:{today}"
        
        cache.set(f"{daily_key}:last_activity", datetime.now().isoformat(), timeout=86400)
        
        # Increment event counters
        event_counter_key = f"{daily_key}:events:{event_type}"
        current_count = cache.get(event_counter_key, 0)
        cache.set(event_counter_key, current_count + 1, timeout=86400)

        # Session tracking
        session_id = properties.get('session_id')
        if session_id:
            session_key = f"{cache_key_prefix}:session:{session_id}"
            session_events = cache.get(session_key, [])
            session_events.append({
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'properties': properties
            })
            cache.set(session_key, session_events, timeout=3600)  # 1 hour session

        # Check for anomalies or thresholds
        check_user_anomalies.delay(user_id, event_type, current_count + 1)

    except Exception as e:
        logger.error(f"Error updating real-time metrics: {str(e)}")

@shared_task
def check_user_anomalies(user_id: str, event_type: str, event_count: int):
    """
    Check for unusual user behavior patterns and trigger alerts
    """
    try:
        user_pref = UserPreference.objects(user_id=user_id).first()
        if not user_pref:
            return

        anomalies_detected = []

        # Check for unusual activity levels
        if event_type == 'course_interaction' and event_count > 50:
            anomalies_detected.append({
                'type': 'high_interaction_rate',
                'description': f'User has {event_count} course interactions today',
                'severity': 'medium'
            })

        # Check for potential struggling patterns
        if event_type == 'quiz_attempt':
            # Get recent quiz performance
            recent_performance = get_recent_quiz_performance(user_id)
            if recent_performance and recent_performance.get('avg_score', 100) < 40:
                anomalies_detected.append({
                    'type': 'poor_performance',
                    'description': 'User showing signs of struggling with content',
                    'severity': 'high'
                })

        # Process anomalies
        if anomalies_detected:
            process_user_anomalies.delay(user_id, anomalies_detected)

    except Exception as e:
        logger.error(f"Error checking anomalies for user {user_id}: {str(e)}")

@shared_task
def process_user_anomalies(user_id: str, anomalies: List[Dict[str, Any]]):
    """
    Process detected anomalies and take appropriate actions
    """
    try:
        for anomaly in anomalies:
            if anomaly['type'] == 'poor_performance':
                # Trigger intervention recommendations
                generate_intervention_recommendations.delay(user_id, 'performance_support')
            
            elif anomaly['type'] == 'high_interaction_rate':
                # Update engagement score positively
                user_pref = UserPreference.objects(user_id=user_id).first()
                if user_pref:
                    current_score = user_pref.behavioral_patterns.engagement_score
                    new_score = min(1.0, current_score + 0.1)
                    user_pref.update_behavioral_patterns(engagement_score=new_score)

        logger.info(f"Processed {len(anomalies)} anomalies for user {user_id}")

    except Exception as e:
        logger.error(f"Error processing anomalies: {str(e)}")

# =============================================================================
# PERSONALIZATION AND RECOMMENDATION TASKS
# =============================================================================

@shared_task
def generate_intervention_recommendations(user_id: str, intervention_type: str):
    """
    Generate personalized intervention recommendations
    """
    try:
        user_pref = UserPreference.objects(user_id=user_id).first()
        if not user_pref:
            return

        recommendations = []

        if intervention_type == 'performance_support':
            # Analyze weak areas and suggest remedial content
            weak_areas = identify_weak_knowledge_areas(user_pref)
            for area in weak_areas:
                recommendations.append({
                    'type': 'remedial_content',
                    'subject': area,
                    'priority': 'high',
                    'reason': 'performance_improvement'
                })

        elif intervention_type == 'engagement_boost':
            # Suggest more engaging content types
            preferred_formats = user_pref.behavioral_patterns.preferred_content_types
            recommendations.append({
                'type': 'content_format',
                'formats': preferred_formats,
                'priority': 'medium',
                'reason': 'engagement_optimization'
            })

        # Store recommendations
        cache_key = f"recommendations_{user_id}"
        cache.set(cache_key, recommendations, timeout=86400)  # 24 hours

        logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")

    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")

@shared_task
def update_user_segments():
    """
    Update user segments based on behavioral patterns
    Runs periodically to refresh user clustering
    """
    try:
        # Get all users with sufficient data
        users_with_data = UserPreference.objects(
            behavioral_patterns__engagement_score__gt=0
        )

        segment_updates = []
        
        for user_pref in users_with_data:
            # Calculate user segment based on behavior
            segment = calculate_user_segment(user_pref)
            
            # Update if segment changed
            current_segment = user_pref.ai_insights.get('user_segment')
            if segment != current_segment:
                user_pref.update_ai_insights({'user_segment': segment})
                segment_updates.append({
                    'user_id': user_pref.user_id,
                    'old_segment': current_segment,
                    'new_segment': segment
                })

        logger.info(f"Updated segments for {len(segment_updates)} users")
        return {'status': 'completed', 'updates': len(segment_updates)}

    except Exception as e:
        logger.error(f"Error updating user segments: {str(e)}")
        return {'status': 'error', 'error': str(e)}

# =============================================================================
# PERIODIC MAINTENANCE TASKS
# =============================================================================

@shared_task
def cleanup_old_analytics_data():
    """
    Clean up old analytics data to maintain performance
    """
    try:
        # Clean up data older than 90 days
        cutoff_date = datetime.now() - timedelta(days=90)
        
        # Clean up cached metrics
        pattern = "metrics:*"
        keys_deleted = 0
        
        # Note: In production, use more sophisticated cleanup
        # This is a simplified version for demonstration
        
        logger.info(f"Cleaned up {keys_deleted} old analytics keys")
        return {'status': 'completed', 'keys_deleted': keys_deleted}

    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task
def generate_analytics_reports():
    """
    Generate periodic analytics reports
    """
    try:
        # Generate daily summary reports
        today = datetime.now().date()
        
        # Overall platform metrics
        total_users = UserPreference.objects.count()
        active_users_today = get_active_users_count(today)
        
        # Engagement metrics
        avg_engagement = UserPreference.objects.aggregate(
            avg_engagement=Avg('behavioral_patterns.engagement_score')
        )
        
        report_data = {
            'date': today.isoformat(),
            'total_users': total_users,
            'active_users_today': active_users_today,
            'average_engagement': avg_engagement,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache report for dashboard access
        cache.set('daily_analytics_report', report_data, timeout=86400)
        
        logger.info(f"Generated analytics report for {today}")
        return report_data

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return {'status': 'error', 'error': str(e)}

# =============================================================================
# MACHINE LEARNING AND RECOMMENDATION TASKS
# =============================================================================

@shared_task(bind=True, retry_backoff=True, max_retries=2)
def update_recommendation_models(self):
    """
    Update ML models for personalized recommendations
    """
    try:
        import pickle
        import os
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.cluster import KMeans
        import numpy as np

        # Get all users with sufficient interaction data
        users_with_data = UserPreference.objects(
            behavioral_patterns__engagement_score__gt=0.1
        )

        if len(users_with_data) < 10:
            logger.info("Insufficient data for model training")
            return {'status': 'skipped', 'reason': 'insufficient_data'}

        # Prepare feature matrices
        user_features = []
        user_ids = []
        
        for user_pref in users_with_data:
            features = extract_user_features(user_pref)
            user_features.append(features)
            user_ids.append(user_pref.user_id)

        user_features = np.array(user_features)

        # Train clustering model for user segmentation
        kmeans = KMeans(n_clusters=min(5, len(users_with_data)//2), random_state=42)
        user_clusters = kmeans.fit_predict(user_features)

        # Update user segments based on clustering
        for i, user_id in enumerate(user_ids):
            cluster_label = f"cluster_{user_clusters[i]}"
            user_pref = UserPreference.objects(user_id=user_id).first()
            if user_pref:
                user_pref.update_ai_insights({'ml_segment': cluster_label})

        # Save models for inference
        model_data = {
            'kmeans_model': kmeans,
            'feature_names': get_feature_names(),
            'last_updated': datetime.now().isoformat()
        }

        # Cache the model
        cache.set('recommendation_models', model_data, timeout=86400 * 7)  # 1 week

        logger.info(f"Updated ML models with {len(user_features)} users")
        return {
            'status': 'completed',
            'users_processed': len(user_features),
            'clusters_created': len(set(user_clusters)),
            'model_size': len(user_features)
        }

    except Exception as exc:
        logger.error(f"Error updating ML models: {str(exc)}", exc_info=True)
        self.retry(countdown=1800)  # Retry after 30 minutes

@shared_task
def generate_content_recommendations(user_id: str, limit: int = 10):
    """
    Generate personalized content recommendations for a user
    """
    try:
        user_pref = UserPreference.objects(user_id=user_id).first()
        if not user_pref:
            return {'status': 'error', 'reason': 'user_not_found'}

        # Get ML models
        models = cache.get('recommendation_models')
        if not models:
            logger.warning("No ML models available for recommendations")
            return generate_fallback_recommendations(user_pref, limit)

        # Extract user features
        user_features = extract_user_features(user_pref)
        
        # Find similar users using the trained model
        similar_users = find_similar_users(user_features, models, limit=5)
        
        # Generate recommendations based on similar users
        recommendations = []
        for similar_user_id in similar_users:
            similar_user_pref = UserPreference.objects(user_id=similar_user_id).first()
            if similar_user_pref:
                # Add their preferred content types as recommendations
                for content_type in similar_user_pref.behavioral_patterns.preferred_content_types:
                    if content_type not in [r['content_type'] for r in recommendations]:
                        recommendations.append({
                            'content_type': content_type,
                            'reason': 'similar_users_like',
                            'confidence': 0.8,
                            'source': 'collaborative_filtering'
                        })
                        
                        if len(recommendations) >= limit:
                            break

        # Fill remaining slots with content-based recommendations
        if len(recommendations) < limit:
            content_recommendations = generate_content_based_recommendations(
                user_pref, limit - len(recommendations)
            )
            recommendations.extend(content_recommendations)

        # Cache recommendations
        cache_key = f"recommendations_{user_id}"
        cache.set(cache_key, recommendations, timeout=3600)  # 1 hour

        return {
            'status': 'completed',
            'user_id': user_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        }

    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {str(e)}")
        return {'status': 'error', 'error': str(e)}

# =============================================================================
# MONITORING AND SYSTEM HEALTH TASKS
# =============================================================================

@shared_task
def monitor_system_performance():
    """
    Monitor system performance and analytics pipeline health
    """
    try:
        import psutil
        
        # System metrics
        system_metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat()
        }

        # Database metrics
        db_metrics = get_database_metrics()
        
        # Analytics pipeline metrics
        pipeline_metrics = get_pipeline_metrics()
        
        # Cache metrics
        cache_metrics = get_cache_metrics()

        # Combine all metrics
        all_metrics = {
            'system': system_metrics,
            'database': db_metrics,
            'pipeline': pipeline_metrics,
            'cache': cache_metrics
        }

        # Store metrics for monitoring dashboard
        cache.set('system_metrics', all_metrics, timeout=300)  # 5 minutes

        # Check for alerts
        check_system_alerts(all_metrics)

        logger.info("System performance monitoring completed")
        return all_metrics

    except Exception as e:
        logger.error(f"Error monitoring system performance: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task
def privacy_compliance_audit():
    """
    Audit system for privacy compliance and data retention
    """
    try:
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'issues_found': [],
            'users_audited': 0,
            'data_cleaned': 0
        }

        # Check consent compliance
        users_without_consent = UserPreference.objects(
            privacy_settings__analytics_consent=False,
            last_activity_date__lt=datetime.now() - timedelta(days=30)
        )

        # Clean data for users without consent
        for user_pref in users_without_consent:
            if should_clean_user_data(user_pref):
                clean_user_analytics_data(user_pref)
                audit_results['data_cleaned'] += 1

        # Check data retention policies
        old_data_count = check_data_retention_compliance()
        if old_data_count > 0:
            audit_results['issues_found'].append({
                'type': 'data_retention',
                'count': old_data_count,
                'description': 'Old data found beyond retention period'
            })

        # Check for missing privacy settings
        users_missing_privacy = UserPreference.objects(
            privacy_settings__exists=False
        )
        
        if users_missing_privacy.count() > 0:
            audit_results['issues_found'].append({
                'type': 'missing_privacy_settings',
                'count': users_missing_privacy.count(),
                'description': 'Users without privacy settings'
            })

        audit_results['users_audited'] = UserPreference.objects.count()

        # Store audit results
        cache.set('privacy_audit_results', audit_results, timeout=86400)  # 24 hours

        logger.info(f"Privacy compliance audit completed. Issues found: {len(audit_results['issues_found'])}")
        return audit_results

    except Exception as e:
        logger.error(f"Error in privacy compliance audit: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task
def data_quality_assessment():
    """
    Assess data quality and identify anomalies
    """
    try:
        quality_report = {
            'timestamp': datetime.now().isoformat(),
            'total_users': 0,
            'data_quality_issues': [],
            'recommendations': []
        }

        all_users = UserPreference.objects.all()
        quality_report['total_users'] = all_users.count()

        # Check for common data quality issues
        issues_found = 0

        # 1. Check for missing essential data
        users_missing_onboarding = all_users.filter(
            preferences_data__academic_info__exists=False
        )
        if users_missing_onboarding.count() > 0:
            quality_report['data_quality_issues'].append({
                'type': 'missing_onboarding_data',
                'count': users_missing_onboarding.count(),
                'percentage': (users_missing_onboarding.count() / all_users.count()) * 100
            })
            issues_found += 1

        # 2. Check for stale behavioral data
        stale_behavior_cutoff = datetime.now() - timedelta(days=7)
        users_stale_behavior = all_users.filter(
            last_activity_date__lt=stale_behavior_cutoff
        )
        if users_stale_behavior.count() > 0:
            quality_report['data_quality_issues'].append({
                'type': 'stale_behavioral_data',
                'count': users_stale_behavior.count(),
                'percentage': (users_stale_behavior.count() / all_users.count()) * 100
            })

        # 3. Check for extreme values
        extreme_engagement = all_users.filter(
            behavioral_patterns__engagement_score__gt=0.95
        )
        if extreme_engagement.count() > all_users.count() * 0.05:  # More than 5%
            quality_report['data_quality_issues'].append({
                'type': 'extreme_engagement_values',
                'count': extreme_engagement.count(),
                'description': 'Unusually high number of users with perfect engagement'
            })

        # Generate recommendations
        if issues_found > 0:
            quality_report['recommendations'].append(
                'Schedule data collection campaigns for users missing onboarding data'
            )

        if users_stale_behavior.count() > all_users.count() * 0.3:
            quality_report['recommendations'].append(
                'Implement re-engagement campaigns for users with stale data'
            )

        # Store quality report
        cache.set('data_quality_report', quality_report, timeout=86400)  # 24 hours

        logger.info(f"Data quality assessment completed. Issues found: {len(quality_report['data_quality_issues'])}")
        return quality_report

    except Exception as e:
        logger.error(f"Error in data quality assessment: {str(e)}")
        return {'status': 'error', 'error': str(e)}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def process_course_interaction_event(user_pref: UserPreference, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Process course interaction events and return behavioral updates"""
    updates = {}
    
    action = properties.get('action', '')
    course_id = properties.get('course_id')
    
    if action == 'view':
        # Increment view count and update engagement
        updates['engagement_score'] = min(1.0, user_pref.behavioral_patterns.engagement_score + 0.01)
    
    elif action == 'enroll':
        # High engagement signal
        updates['engagement_score'] = min(1.0, user_pref.behavioral_patterns.engagement_score + 0.05)
        
        # Track preferred course categories
        course_category = properties.get('course_category')
        if course_category:
            current_preferences = user_pref.behavioral_patterns.preferred_content_types or []
            if course_category not in current_preferences:
                current_preferences.append(course_category)
                updates['preferred_content_types'] = current_preferences

    return updates

def process_learning_session_event(user_pref: UserPreference, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Process learning session events"""
    updates = {}
    
    duration = properties.get('duration', 0)
    completion_rate = properties.get('completion_rate', 0)
    
    if duration > 0:
        # Calculate learning velocity (content completed per minute)
        velocity = (completion_rate / 100) / (duration / 60)  # percentage per minute
        updates['learning_velocity'] = velocity
        
        # Update engagement based on session quality
        if completion_rate > 80 and duration > 300:  # 5 minutes minimum, 80% completion
            updates['engagement_score'] = min(1.0, user_pref.behavioral_patterns.engagement_score + 0.03)

    return updates

def process_quiz_event(user_pref: UserPreference, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Process quiz attempt events"""
    updates = {}
    
    score = properties.get('score', 0)
    total_questions = properties.get('total_questions', 0)
    
    if total_questions > 0:
        performance_ratio = score / total_questions
        
        # Update dropout risk based on performance
        if performance_ratio < 0.5:  # Below 50%
            risk_increase = 0.05
        elif performance_ratio > 0.8:  # Above 80%
            risk_increase = -0.02  # Reduce risk
        else:
            risk_increase = 0
            
        current_risk = user_pref.behavioral_patterns.dropout_risk_score
        new_risk = max(0.0, min(1.0, current_risk + risk_increase))
        updates['dropout_risk_score'] = new_risk

    return updates

def process_search_event(user_pref: UserPreference, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Process search events"""
    updates = {}
    
    query = properties.get('query', '').lower()
    results_count = properties.get('results_count', 0)
    
    # Track search engagement
    if results_count > 0:
        updates['engagement_score'] = min(1.0, user_pref.behavioral_patterns.engagement_score + 0.005)

    return updates

def process_ui_interaction_event(user_pref: UserPreference, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Process UI interaction events"""
    updates = {}
    
    # Light engagement tracking for UI interactions
    updates['engagement_score'] = min(1.0, user_pref.behavioral_patterns.engagement_score + 0.001)
    
    return updates

def should_trigger_analysis(event_type: str, user_pref: UserPreference) -> bool:
    """Determine if comprehensive analysis should be triggered"""
    # Trigger analysis for high-value events or periodically
    high_value_events = ['course_interaction', 'learning_session', 'quiz_attempt']
    
    if event_type in high_value_events:
        # Check if enough time has passed since last analysis
        last_analysis = user_pref.ai_insights.get('last_analysis_timestamp')
        if not last_analysis:
            return True
            
        last_analysis_time = datetime.fromisoformat(last_analysis)
        if datetime.now() - last_analysis_time > timedelta(hours=1):
            return True
    
    return False

def analyze_learning_patterns(user_pref: UserPreference) -> Dict[str, Any]:
    """Analyze user learning patterns"""
    patterns = user_pref.behavioral_patterns
    
    return {
        'learning_velocity': patterns.learning_velocity,
        'preferred_times': patterns.peak_activity_hours,
        'content_preferences': patterns.preferred_content_types,
        'consistency_score': calculate_learning_consistency(user_pref)
    }

def analyze_engagement_patterns(user_pref: UserPreference) -> Dict[str, Any]:
    """Analyze user engagement patterns"""
    patterns = user_pref.behavioral_patterns
    
    return {
        'current_engagement': patterns.engagement_score,
        'engagement_trend': calculate_engagement_trend(user_pref),
        'peak_engagement_times': patterns.peak_activity_hours
    }

def calculate_dropout_risk(user_pref: UserPreference) -> Dict[str, Any]:
    """Calculate and analyze dropout risk"""
    patterns = user_pref.behavioral_patterns
    
    risk_factors = {
        'low_engagement': patterns.engagement_score < 0.3,
        'high_existing_risk': patterns.dropout_risk_score > 0.7,
        'inconsistent_activity': calculate_learning_consistency(user_pref) < 0.5
    }
    
    return {
        'risk_score': patterns.dropout_risk_score,
        'risk_factors': risk_factors,
        'intervention_recommended': patterns.dropout_risk_score > 0.6
    }

def generate_personalization_updates(user_pref: UserPreference, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate personalization updates based on analysis"""
    updates = {}
    
    # Update content recommendations based on preferences
    preferred_content = user_pref.behavioral_patterns.preferred_content_types
    if preferred_content:
        updates['recommended_content_types'] = preferred_content[:3]  # Top 3

    # Update difficulty recommendations based on performance
    risk_score = analysis['risk_assessment']['risk_score']
    if risk_score > 0.5:
        updates['recommended_difficulty'] = 'easier'
    elif user_pref.behavioral_patterns.engagement_score > 0.8:
        updates['recommended_difficulty'] = 'harder'
    else:
        updates['recommended_difficulty'] = 'current'

    return updates

def calculate_learning_consistency(user_pref: UserPreference) -> float:
    """Calculate learning consistency score (placeholder implementation)"""
    # In a real implementation, this would analyze historical activity patterns
    # For now, return a score based on engagement
    return min(1.0, user_pref.behavioral_patterns.engagement_score * 1.2)

def calculate_engagement_trend(user_pref: UserPreference) -> str:
    """Calculate engagement trend (placeholder implementation)"""
    # In a real implementation, this would analyze historical engagement data
    current_engagement = user_pref.behavioral_patterns.engagement_score
    
    if current_engagement > 0.7:
        return 'increasing'
    elif current_engagement < 0.3:
        return 'decreasing'
    else:
        return 'stable'

def calculate_user_segment(user_pref: UserPreference) -> str:
    """Calculate user segment based on behavioral patterns"""
    patterns = user_pref.behavioral_patterns
    
    if patterns.engagement_score > 0.8 and patterns.dropout_risk_score < 0.2:
        return 'highly_engaged'
    elif patterns.dropout_risk_score > 0.6:
        return 'at_risk'
    elif patterns.learning_velocity > 0.1:
        return 'fast_learner'
    elif patterns.engagement_score < 0.3:
        return 'low_engagement'
    else:
        return 'regular'

def identify_weak_knowledge_areas(user_pref: UserPreference) -> List[str]:
    """Identify areas where user needs support (placeholder)"""
    # In a real implementation, this would analyze quiz performance by topic
    return ['mathematics', 'programming_fundamentals']  # Placeholder

def get_recent_quiz_performance(user_id: str) -> Optional[Dict[str, Any]]:
    """Get recent quiz performance data (placeholder)"""
    # In a real implementation, this would query actual quiz data
    return {'avg_score': 45, 'attempts': 3}  # Placeholder

def get_active_users_count(date) -> int:
    """Get count of active users for a given date (placeholder)"""
    # In a real implementation, this would query actual activity data
    return 150  # Placeholder

# =============================================================================
# ADDITIONAL HELPER FUNCTIONS FOR ML AND MONITORING
# =============================================================================

def extract_user_features(user_pref: UserPreference) -> List[float]:
    """Extract numerical features from user preference for ML models"""
    features = []
    
    # Behavioral features
    patterns = user_pref.behavioral_patterns
    features.extend([
        patterns.learning_velocity,
        patterns.engagement_score,
        patterns.dropout_risk_score,
        len(patterns.preferred_content_types or []),
        len(patterns.peak_activity_hours or [])
    ])
    
    # Academic features (if available)
    academic_info = user_pref.preferences_data.get('academic_info', {})
    features.extend([
        1.0 if academic_info.get('education_level') == 'undergraduate' else 0.0,
        1.0 if academic_info.get('education_level') == 'graduate' else 0.0,
        len(academic_info.get('subjects_of_interest', [])) / 10.0,  # Normalize
    ])
    
    # Privacy features
    privacy_settings = user_pref.privacy_settings
    features.extend([
        1.0 if privacy_settings.analytics_consent else 0.0,
        1.0 if privacy_settings.behavioral_analysis else 0.0,
        1.0 if privacy_settings.personalization_consent else 0.0
    ])
    
    return features

def get_feature_names() -> List[str]:
    """Return names of features extracted by extract_user_features"""
    return [
        'learning_velocity', 'engagement_score', 'dropout_risk_score',
        'preferred_content_count', 'peak_hours_count',
        'is_undergraduate', 'is_graduate', 'subjects_interest_ratio',
        'analytics_consent', 'behavioral_analysis', 'personalization_consent'
    ]

def find_similar_users(user_features: List[float], models: Dict[str, Any], limit: int = 5) -> List[str]:
    """Find similar users using ML models"""
    try:
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        # This is a simplified implementation
        # In practice, you'd use the trained model to find nearest neighbors
        
        # For now, return random user IDs as placeholder
        # In real implementation, compute similarity with all users
        similar_user_ids = []
        
        # Get some users for demonstration
        sample_users = UserPreference.objects.limit(limit)
        for user_pref in sample_users:
            similar_user_ids.append(user_pref.user_id)
            
        return similar_user_ids[:limit]
        
    except Exception as e:
        logger.error(f"Error finding similar users: {str(e)}")
        return []

def generate_fallback_recommendations(user_pref: UserPreference, limit: int) -> Dict[str, Any]:
    """Generate fallback recommendations when ML models are unavailable"""
    recommendations = []
    
    # Use preference-based recommendations
    preferred_types = user_pref.behavioral_patterns.preferred_content_types or []
    
    for content_type in preferred_types:
        recommendations.append({
            'content_type': content_type,
            'reason': 'user_preference',
            'confidence': 0.6,
            'source': 'fallback_algorithm'
        })
        
        if len(recommendations) >= limit:
            break
    
    # Fill with popular content if needed
    popular_content = ['programming', 'data_science', 'mathematics', 'business']
    for content in popular_content:
        if len(recommendations) >= limit:
            break
        if content not in [r['content_type'] for r in recommendations]:
            recommendations.append({
                'content_type': content,
                'reason': 'popular_content',
                'confidence': 0.4,
                'source': 'fallback_algorithm'
            })
    
    return {
        'status': 'completed',
        'recommendations': recommendations[:limit],
        'count': len(recommendations[:limit]),
        'source': 'fallback'
    }

def generate_content_based_recommendations(user_pref: UserPreference, limit: int) -> List[Dict[str, Any]]:
    """Generate content-based recommendations"""
    recommendations = []
    
    # Analyze user's academic interests
    academic_info = user_pref.preferences_data.get('academic_info', {})
    subjects = academic_info.get('subjects_of_interest', [])
    
    for subject in subjects:
        if len(recommendations) >= limit:
            break
        recommendations.append({
            'content_type': subject,
            'reason': 'academic_interest',
            'confidence': 0.7,
            'source': 'content_based_filtering'
        })
    
    return recommendations

def get_database_metrics() -> Dict[str, Any]:
    """Get database performance metrics"""
    try:
        # MongoDB metrics
        total_users = UserPreference.objects.count()
        
        # Recent activity
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_activity = UserPreference.objects(
            last_activity_date__gt=recent_cutoff
        ).count()
        
        return {
            'total_user_preferences': total_users,
            'recent_activity_24h': recent_activity,
            'activity_rate': (recent_activity / total_users * 100) if total_users > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting database metrics: {str(e)}")
        return {'error': str(e)}

def get_pipeline_metrics() -> Dict[str, Any]:
    """Get analytics pipeline metrics"""
    try:
        # Get Celery task metrics from cache or compute
        pipeline_metrics = {
            'pending_events': get_pending_events_count(),
            'processed_events_24h': get_processed_events_count(),
            'failed_tasks': get_failed_tasks_count(),
            'average_processing_time': get_average_processing_time(),
            'timestamp': datetime.now().isoformat()
        }
        
        return pipeline_metrics
        
    except Exception as e:
        logger.error(f"Error getting pipeline metrics: {str(e)}")
        return {'error': str(e)}

def get_cache_metrics() -> Dict[str, Any]:
    """Get cache performance metrics"""
    try:
        # Redis/Cache metrics
        cache_info = {
            'hit_rate': get_cache_hit_rate(),
            'memory_usage': get_cache_memory_usage(),
            'active_keys': get_active_cache_keys_count(),
            'timestamp': datetime.now().isoformat()
        }
        
        return cache_info
        
    except Exception as e:
        logger.error(f"Error getting cache metrics: {str(e)}")
        return {'error': str(e)}

def check_system_alerts(metrics: Dict[str, Any]):
    """Check system metrics for alert conditions"""
    alerts = []
    
    # CPU usage alert
    if metrics['system']['cpu_percent'] > 80:
        alerts.append({
            'type': 'high_cpu_usage',
            'value': metrics['system']['cpu_percent'],
            'threshold': 80,
            'severity': 'warning'
        })
    
    # Memory usage alert
    if metrics['system']['memory_percent'] > 85:
        alerts.append({
            'type': 'high_memory_usage',
            'value': metrics['system']['memory_percent'],
            'threshold': 85,
            'severity': 'critical'
        })
    
    # Disk usage alert
    if metrics['system']['disk_usage'] > 90:
        alerts.append({
            'type': 'high_disk_usage',
            'value': metrics['system']['disk_usage'],
            'threshold': 90,
            'severity': 'critical'
        })
    
    if alerts:
        # Store alerts for monitoring dashboard
        cache.set('system_alerts', alerts, timeout=3600)  # 1 hour
        
        # Log critical alerts
        for alert in alerts:
            if alert['severity'] == 'critical':
                logger.critical(f"System Alert: {alert['type']} - {alert['value']}%")
            else:
                logger.warning(f"System Alert: {alert['type']} - {alert['value']}%")

def should_clean_user_data(user_pref: UserPreference) -> bool:
    """Determine if user data should be cleaned based on privacy settings"""
    privacy_settings = user_pref.privacy_settings
    
    # Clean data if user has revoked all consent and has been inactive
    if (not privacy_settings.analytics_consent and 
        not privacy_settings.behavioral_analysis and
        not privacy_settings.personalization_consent):
        
        # Check inactivity period
        if user_pref.last_activity_date:
            inactive_days = (datetime.now() - user_pref.last_activity_date).days
            return inactive_days > 30  # Clean after 30 days of inactivity
    
    return False

def clean_user_analytics_data(user_pref: UserPreference):
    """Clean user analytics data while preserving essential profile info"""
    try:
        # Reset behavioral patterns
        user_pref.behavioral_patterns.engagement_score = 0.0
        user_pref.behavioral_patterns.learning_velocity = 0.0
        user_pref.behavioral_patterns.preferred_content_types = []
        user_pref.behavioral_patterns.peak_activity_hours = []
        user_pref.behavioral_patterns.dropout_risk_score = 0.0
        
        # Clear AI insights
        user_pref.ai_insights = {}
        
        # Clear external data sources
        user_pref.external_data_sources = []
        
        # Clear device usage patterns
        user_pref.device_usage_patterns = []
        
        # Clear location records (if any)
        user_pref.location_data = []
        
        user_pref.save()
        
        logger.info(f"Cleaned analytics data for user {user_pref.user_id}")
        
    except Exception as e:
        logger.error(f"Error cleaning user data: {str(e)}")

def check_data_retention_compliance() -> int:
    """Check for data that exceeds retention policies"""
    try:
        # Check for data older than retention period (e.g., 2 years)
        retention_cutoff = datetime.now() - timedelta(days=730)  # 2 years
        
        old_data_count = UserPreference.objects(
            last_activity_date__lt=retention_cutoff
        ).count()
        
        return old_data_count
        
    except Exception as e:
        logger.error(f"Error checking data retention: {str(e)}")
        return 0

# Placeholder functions for metrics (implement based on your monitoring system)
def get_pending_events_count() -> int:
    """Get count of pending events in queue"""
    return cache.get('pending_events_count', 0)

def get_processed_events_count() -> int:
    """Get count of events processed in last 24 hours"""
    return cache.get('processed_events_24h', 0)

def get_failed_tasks_count() -> int:
    """Get count of failed Celery tasks"""
    return cache.get('failed_tasks_count', 0)

def get_average_processing_time() -> float:
    """Get average event processing time in seconds"""
    return cache.get('avg_processing_time', 0.0)

def get_cache_hit_rate() -> float:
    """Get cache hit rate percentage"""
    return cache.get('cache_hit_rate', 95.0)

def get_cache_memory_usage() -> float:
    """Get cache memory usage percentage"""
    return cache.get('cache_memory_usage', 25.0)

def get_active_cache_keys_count() -> int:
    """Get count of active cache keys"""
    return cache.get('active_cache_keys', 0)

# =============================================================================
# SOCIAL AUTHENTICATION DATA PROCESSING TASKS
# =============================================================================

@shared_task(bind=True, retry_backoff=True, max_retries=3)
def sync_social_accounts_batch(self, account_ids: List[int]) -> Dict[str, Any]:
    """
    Batch sync multiple social accounts
    """
    try:
        from apps.auth.social_models import SocialAccount
        from apps.auth.social_services import SocialAuthService
        
        auth_service = SocialAuthService()
        results = {
            'total_accounts': len(account_ids),
            'successful_syncs': 0,
            'failed_syncs': 0,
            'errors': []
        }
        
        for account_id in account_ids:
            try:
                social_account = SocialAccount.objects.get(
                    id=account_id,
                    is_active=True,
                    data_collection_consent=True
                )
                
                success = auth_service.sync_social_account(social_account)
                
                if success:
                    results['successful_syncs'] += 1
                    
                    # Update user preferences with new social data
                    update_user_preferences_from_social.delay(social_account.user_id)
                else:
                    results['failed_syncs'] += 1
                    results['errors'].append(f"Sync failed for account {account_id}")
                
            except SocialAccount.DoesNotExist:
                results['failed_syncs'] += 1
                results['errors'].append(f"Social account {account_id} not found")
            except Exception as e:
                results['failed_syncs'] += 1
                results['errors'].append(f"Error syncing account {account_id}: {str(e)}")
        
        logger.info(f"Batch social sync completed: {results['successful_syncs']}/{results['total_accounts']} successful")
        return results
        
    except Exception as exc:
        logger.error(f"Error in batch social sync: {str(exc)}")
        self.retry(countdown=300)

@shared_task
def update_user_preferences_from_social(user_id: int):
    """
    Update user preferences based on social profile data
    """
    try:
        from apps.auth.social_models import SocialAccount, SocialProfileEnrichment
        from apps.preferences.models import UserPreference
        
        # Get user's social accounts
        social_accounts = SocialAccount.objects.filter(
            user_id=user_id,
            is_active=True,
            data_collection_consent=True
        )
        
        if not social_accounts.exists():
            return
        
        # Get user preference document
        user_pref = UserPreference.objects(user_id=str(user_id)).first()
        if not user_pref:
            return
        
        # Aggregate social data
        aggregated_data = {
            'interests': set(),
            'skills': set(),
            'locations': [],
            'companies': [],
            'education': [],
            'languages': set(),
        }
        
        for account in social_accounts:
            profile_data = account.profile_data
            
            # Extract interests
            if 'interests' in profile_data:
                aggregated_data['interests'].update(profile_data['interests'])
            
            if 'topics_of_interest' in profile_data:
                aggregated_data['interests'].update(profile_data['topics_of_interest'])
            
            # Extract skills
            if 'skills' in profile_data:
                aggregated_data['skills'].update(profile_data['skills'])
            
            if 'programming_languages' in profile_data:
                aggregated_data['languages'].update(profile_data['programming_languages'])
            
            # Extract professional info
            if 'current_company' in profile_data:
                aggregated_data['companies'].append(profile_data['current_company'])
            
            if 'location' in profile_data:
                aggregated_data['locations'].append(profile_data['location'])
            
            # Extract education
            if 'education_history' in profile_data:
                aggregated_data['education'].extend(profile_data['education_history'])
        
        # Update user preferences
        preferences_update = {}
        
        # Update interests
        current_interests = user_pref.preferences_data.get('interests', {}).get('areas_of_interest', [])
        new_interests = list(aggregated_data['interests'])[:20]  # Limit to top 20
        combined_interests = list(set(current_interests + new_interests))
        
        if 'interests' not in user_pref.preferences_data:
            user_pref.preferences_data['interests'] = {}
        user_pref.preferences_data['interests']['areas_of_interest'] = combined_interests
        
        # Update professional info
        if aggregated_data['companies']:
            if 'professional_info' not in user_pref.preferences_data:
                user_pref.preferences_data['professional_info'] = {}
            user_pref.preferences_data['professional_info']['current_company'] = aggregated_data['companies'][-1]
        
        # Update skills
        if aggregated_data['skills'] or aggregated_data['languages']:
            all_skills = list(aggregated_data['skills'].union(aggregated_data['languages']))[:30]
            if 'academic_info' not in user_pref.preferences_data:
                user_pref.preferences_data['academic_info'] = {}
            user_pref.preferences_data['academic_info']['technical_skills'] = all_skills
        
        # Save updates
        user_pref.save()
        
        logger.info(f"Updated user preferences from social data for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error updating user preferences from social data: {str(e)}")

@shared_task
def enrich_user_profile_from_social(user_id: int):
    """
    Analyze social profile data and create enrichment insights
    """
    try:
        from apps.auth.social_models import SocialAccount, SocialProfileEnrichment
        from apps.preferences.models import UserPreference
        
        social_accounts = SocialAccount.objects.filter(
            user_id=user_id,
            is_active=True,
            data_collection_consent=True
        )
        
        if not social_accounts.exists():
            return
        
        enrichment_insights = {}
        
        for account in social_accounts:
            profile_data = account.profile_data
            provider = account.provider.name
            
            # Analyze professional level
            if provider == 'linkedin':
                professional_level = analyze_professional_level(profile_data)
                enrichment_insights['professional_level'] = professional_level
            
            # Analyze technical expertise
            if provider == 'github':
                technical_expertise = analyze_technical_expertise(profile_data)
                enrichment_insights['technical_expertise'] = technical_expertise
            
            # Analyze learning preferences
            learning_preferences = infer_learning_preferences(profile_data, provider)
            if learning_preferences:
                enrichment_insights['learning_preferences'] = learning_preferences
        
        # Create or update enrichment records
        for enrichment_type, data in enrichment_insights.items():
            SocialProfileEnrichment.objects.update_or_create(
                user_id=user_id,
                social_account=account,
                enrichment_type=enrichment_type,
                defaults={
                    'enrichment_data': data,
                    'confidence_score': data.get('confidence', 0.7),
                    'extraction_method': 'automated_analysis',
                }
            )
        
        logger.info(f"Created {len(enrichment_insights)} enrichment insights for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error enriching user profile from social data: {str(e)}")

@shared_task
def cleanup_expired_social_tokens():
    """
    Clean up expired OAuth tokens and refresh them where possible
    """
    try:
        from apps.auth.social_models import SocialAccount
        from apps.auth.social_services import SocialAuthService
        
        # Get accounts with expired tokens
        expired_accounts = SocialAccount.objects.filter(
            is_active=True,
            token_expires_at__lt=timezone.now()
        )
        
        auth_service = SocialAuthService()
        refreshed_count = 0
        cleanup_count = 0
        
        for account in expired_accounts:
            try:
                if account.refresh_token:
                    # Try to refresh the token
                    handler = auth_service.get_handler(account.provider.name)
                    token_data = handler.refresh_token(account.refresh_token)
                    
                    # Update account with new token
                    account.access_token = token_data['access_token']
                    if 'expires_in' in token_data:
                        expires_at = timezone.now() + timedelta(seconds=token_data['expires_in'])
                        account.token_expires_at = expires_at
                    if 'refresh_token' in token_data:
                        account.refresh_token = token_data['refresh_token']
                    
                    account.save()
                    refreshed_count += 1
                    
                else:
                    # No refresh token, mark account as needing re-authentication
                    account.is_active = False
                    account.save()
                    cleanup_count += 1
                    
            except Exception as e:
                logger.error(f"Error refreshing token for account {account.id}: {str(e)}")
                account.is_active = False
                account.save()
                cleanup_count += 1
        
        logger.info(f"Token cleanup completed: {refreshed_count} refreshed, {cleanup_count} cleaned up")
        
        return {
            'refreshed_tokens': refreshed_count,
            'cleaned_up_accounts': cleanup_count,
            'total_processed': refreshed_count + cleanup_count
        }
        
    except Exception as e:
        logger.error(f"Error in social token cleanup: {str(e)}")
        return {'error': str(e)}

def analyze_professional_level(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze professional level from LinkedIn data"""
    level_indicators = {
        'entry_level': 0,
        'mid_level': 0,
        'senior_level': 0,
        'executive_level': 0
    }
    
    # Analyze work history
    work_history = profile_data.get('work_history', [])
    total_experience = len(work_history)
    
    if total_experience <= 2:
        level_indicators['entry_level'] += 3
    elif total_experience <= 5:
        level_indicators['mid_level'] += 3
    elif total_experience <= 10:
        level_indicators['senior_level'] += 3
    else:
        level_indicators['executive_level'] += 3
    
    # Analyze titles
    current_title = profile_data.get('current_title', '').lower()
    executive_keywords = ['ceo', 'cto', 'vp', 'director', 'head of', 'chief']
    senior_keywords = ['senior', 'lead', 'principal', 'architect', 'manager']
    
    if any(keyword in current_title for keyword in executive_keywords):
        level_indicators['executive_level'] += 2
    elif any(keyword in current_title for keyword in senior_keywords):
        level_indicators['senior_level'] += 2
    elif 'junior' in current_title or 'intern' in current_title:
        level_indicators['entry_level'] += 2
    else:
        level_indicators['mid_level'] += 1
    
    # Determine primary level
    primary_level = max(level_indicators, key=level_indicators.get)
    confidence = level_indicators[primary_level] / sum(level_indicators.values())
    
    return {
        'primary_level': primary_level,
        'confidence': confidence,
        'level_scores': level_indicators,
        'total_experience_years': total_experience,
    }

def analyze_technical_expertise(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze technical expertise from GitHub data"""
    expertise = {
        'primary_languages': profile_data.get('programming_languages', [])[:5],
        'project_complexity': profile_data.get('total_stars', 0),
        'collaboration_level': profile_data.get('total_forks', 0),
        'consistency': profile_data.get('public_repos', 0),
    }
    
    # Calculate expertise level
    stars = expertise['project_complexity']
    repos = expertise['consistency']
    
    if stars > 1000 or repos > 50:
        expertise_level = 'expert'
        confidence = 0.9
    elif stars > 100 or repos > 20:
        expertise_level = 'advanced'
        confidence = 0.8
    elif stars > 10 or repos > 5:
        expertise_level = 'intermediate'
        confidence = 0.7
    else:
        expertise_level = 'beginner'
        confidence = 0.6
    
    expertise.update({
        'expertise_level': expertise_level,
        'confidence': confidence,
    })
    
    return expertise

def infer_learning_preferences(profile_data: Dict[str, Any], provider: str) -> Optional[Dict[str, Any]]:
    """Infer learning preferences from social profile data"""
    preferences = {}
    
    # Infer from interests and bio
    interests = profile_data.get('interests', [])
    bio = profile_data.get('bio', '').lower()
    
    # Learning style indicators
    if any(keyword in bio for keyword in ['teach', 'mentor', 'coach', 'train']):
        preferences['learning_style'] = 'collaborative'
    elif any(keyword in bio for keyword in ['research', 'analyze', 'study']):
        preferences['learning_style'] = 'analytical'
    elif any(keyword in bio for keyword in ['build', 'create', 'develop']):
        preferences['learning_style'] = 'hands_on'
    
    # Content preferences
    if provider == 'github':
        if profile_data.get('programming_languages'):
            preferences['preferred_content'] = 'technical'
    elif provider == 'linkedin':
        if profile_data.get('industry'):
            preferences['preferred_content'] = 'professional'
    
    # Difficulty preferences
    technical_expertise = analyze_technical_expertise(profile_data)
    if technical_expertise.get('expertise_level') == 'expert':
        preferences['difficulty_preference'] = 'advanced'
    elif technical_expertise.get('expertise_level') == 'beginner':
        preferences['difficulty_preference'] = 'beginner'
    else:
        preferences['difficulty_preference'] = 'intermediate'
    
    return preferences if preferences else None