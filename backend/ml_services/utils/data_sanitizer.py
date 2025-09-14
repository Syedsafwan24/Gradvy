"""
backend/ml_services/utils/data_sanitizer.py
Privacy-compliant data sanitization pipeline for ML services
Ensures user data is properly cleaned and anonymized before processing by AI models
RELEVANT FILES: services/learning_path_service.py, services/question_generator_service.py, services/code_evaluation_service.py, core/apps/preferences/models.py
"""

import re
import logging
import hashlib
import uuid
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field

# Logging configuration
logger = logging.getLogger(__name__)


class SensitivityLevel(Enum):
    """Data sensitivity levels for processing"""
    PUBLIC = "public"           # No sensitive data
    INTERNAL = "internal"       # Internal use only
    CONFIDENTIAL = "confidential"  # User-specific data
    RESTRICTED = "restricted"   # PII or highly sensitive


class DataCategory(Enum):
    """Categories of data being processed"""
    USER_PREFERENCES = "user_preferences"
    LEARNING_CONTENT = "learning_content"
    CODE_SUBMISSION = "code_submission"
    ASSESSMENT_DATA = "assessment_data"
    BEHAVIORAL_DATA = "behavioral_data"
    PROFILE_DATA = "profile_data"


@dataclass
class SanitizationConfig:
    """Configuration for data sanitization"""
    remove_pii: bool = True
    anonymize_identifiers: bool = True
    hash_sensitive_fields: bool = True
    remove_personal_comments: bool = True
    preserve_learning_context: bool = True
    max_text_length: int = 10000
    allowed_data_categories: Set[DataCategory] = field(default_factory=set)
    sensitivity_level: SensitivityLevel = SensitivityLevel.CONFIDENTIAL


@dataclass
class SanitizationResult:
    """Result of data sanitization process"""
    sanitized_data: Dict[str, Any]
    removed_fields: List[str] = field(default_factory=list)
    anonymized_fields: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    original_size_bytes: int = 0
    sanitized_size_bytes: int = 0
    processing_time_ms: float = 0.0
    compliance_score: float = 100.0  # 0-100 compliance rating


class DataSanitizer:
    """
    Privacy-compliant data sanitization for ML processing

    This class ensures that all user data sent to AI models is properly
    sanitized, anonymized, and compliant with privacy regulations like GDPR.
    """

    def __init__(self, config: Optional[SanitizationConfig] = None):
        self.config = config or SanitizationConfig()

        # PII patterns for detection and removal
        self.pii_patterns = self._initialize_pii_patterns()

        # Sensitive field names to watch for
        self.sensitive_fields = {
            'email', 'phone', 'ssn', 'social_security', 'password', 'token',
            'api_key', 'secret', 'private', 'confidential', 'personal',
            'address', 'location', 'ip_address', 'device_id', 'user_agent',
            'browser_fingerprint', 'session_id', 'user_id', 'account_id',
            'first_name', 'last_name', 'full_name', 'name', 'username'
        }

        # Safe fields that can be preserved
        self.safe_fields = {
            'learning_goals', 'skills', 'preferences', 'difficulty_level',
            'experience_level', 'learning_style', 'pace', 'interests',
            'career_goals', 'industry', 'role', 'topics', 'subjects',
            'programming_languages', 'frameworks', 'tools', 'certifications'
        }

        # Anonymization salt for consistent hashing
        self.anonymization_salt = self._generate_session_salt()

    def _initialize_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize regex patterns for PII detection"""
        return {
            'email': re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                re.IGNORECASE
            ),
            'phone': re.compile(
                r'(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}',
                re.IGNORECASE
            ),
            'ssn': re.compile(
                r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b',
                re.IGNORECASE
            ),
            'credit_card': re.compile(
                r'\b(?:\d{4}[-.\s]?){3}\d{4}\b',
                re.IGNORECASE
            ),
            'ip_address': re.compile(
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                re.IGNORECASE
            ),
            'url_with_params': re.compile(
                r'https?://[^\s]+[?&]([^=\s]+=[^&\s]+)',
                re.IGNORECASE
            ),
            'api_key': re.compile(
                r'\b[A-Za-z0-9]{20,}\b',
                re.IGNORECASE
            )
        }

    def _generate_session_salt(self) -> str:
        """Generate a unique salt for this sanitization session"""
        return hashlib.sha256(
            f"gradvy_ml_sanitizer_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

    def sanitize_user_preferences(self, user_preferences: Dict[str, Any]) -> SanitizationResult:
        """
        Sanitize user preference data for ML processing

        Args:
            user_preferences: Raw user preference data from MongoDB

        Returns:
            SanitizationResult with sanitized data
        """
        start_time = datetime.now()

        try:
            original_data = user_preferences.copy()
            original_size = len(str(original_data))

            sanitized_data = {}
            removed_fields = []
            anonymized_fields = []
            warnings = []

            for field, value in user_preferences.items():
                if self._is_sensitive_field(field):
                    if self.config.remove_pii:
                        removed_fields.append(field)
                        warnings.append(f"Removed sensitive field: {field}")
                        continue
                    elif self.config.anonymize_identifiers:
                        sanitized_data[field] = self._anonymize_value(value)
                        anonymized_fields.append(field)
                elif self._is_safe_field(field):
                    # Safe field - sanitize content but preserve structure
                    sanitized_data[field] = self._sanitize_content(value, field)
                else:
                    # Unknown field - apply conservative sanitization
                    sanitized_value = self._sanitize_content(value, field)
                    if sanitized_value != value:
                        warnings.append(f"Modified potentially sensitive field: {field}")
                    sanitized_data[field] = sanitized_value

            # Add learning context preservation
            if self.config.preserve_learning_context:
                sanitized_data = self._preserve_learning_context(sanitized_data, original_data)

            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            sanitized_size = len(str(sanitized_data))
            compliance_score = self._calculate_compliance_score(
                original_data, sanitized_data, removed_fields, anonymized_fields
            )

            return SanitizationResult(
                sanitized_data=sanitized_data,
                removed_fields=removed_fields,
                anonymized_fields=anonymized_fields,
                warnings=warnings,
                original_size_bytes=original_size,
                sanitized_size_bytes=sanitized_size,
                processing_time_ms=processing_time,
                compliance_score=compliance_score
            )

        except Exception as e:
            logger.error(f"Error sanitizing user preferences: {e}")
            return SanitizationResult(
                sanitized_data={},
                warnings=[f"Sanitization failed: {str(e)}"],
                compliance_score=0.0
            )

    def sanitize_code(self, code: str, language: str = "unknown") -> str:
        """
        Sanitize code submissions for evaluation

        Args:
            code: Code content to sanitize
            language: Programming language

        Returns:
            Sanitized code string
        """
        try:
            if not code or not isinstance(code, str):
                return ""

            # Limit code length
            if len(code) > self.config.max_text_length:
                code = code[:self.config.max_text_length]
                logger.warning(f"Code truncated to {self.config.max_text_length} characters")

            sanitized_code = code

            # Remove personal comments if configured
            if self.config.remove_personal_comments:
                sanitized_code = self._remove_personal_comments(sanitized_code, language)

            # Remove embedded sensitive data
            sanitized_code = self._remove_sensitive_patterns(sanitized_code)

            # Remove or anonymize hardcoded credentials
            sanitized_code = self._sanitize_hardcoded_secrets(sanitized_code)

            return sanitized_code

        except Exception as e:
            logger.error(f"Error sanitizing code: {e}")
            return ""

    def sanitize_learning_content(self, content: Dict[str, Any]) -> SanitizationResult:
        """
        Sanitize learning content and objectives

        Args:
            content: Learning content dictionary

        Returns:
            SanitizationResult with sanitized content
        """
        start_time = datetime.now()

        try:
            sanitized_data = {}
            removed_fields = []
            warnings = []

            for field, value in content.items():
                if field in ['learning_goals', 'objectives', 'skills', 'topics', 'description']:
                    # Safe learning content
                    sanitized_data[field] = self._sanitize_text_content(value)
                elif field in ['examples', 'resources', 'materials']:
                    # Content that may contain sensitive references
                    sanitized_data[field] = self._sanitize_content_references(value)
                    if isinstance(value, (list, dict)) and len(str(value)) != len(str(sanitized_data[field])):
                        warnings.append(f"Sanitized content references in {field}")
                else:
                    # Unknown field - conservative approach
                    sanitized_value = self._sanitize_content(value, field)
                    sanitized_data[field] = sanitized_value
                    if sanitized_value != value:
                        warnings.append(f"Modified field: {field}")

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return SanitizationResult(
                sanitized_data=sanitized_data,
                removed_fields=removed_fields,
                warnings=warnings,
                original_size_bytes=len(str(content)),
                sanitized_size_bytes=len(str(sanitized_data)),
                processing_time_ms=processing_time,
                compliance_score=95.0  # Learning content is generally less sensitive
            )

        except Exception as e:
            logger.error(f"Error sanitizing learning content: {e}")
            return SanitizationResult(
                sanitized_data={},
                warnings=[f"Content sanitization failed: {str(e)}"],
                compliance_score=0.0
            )

    def sanitize_assessment_data(self, assessment_data: Dict[str, Any]) -> SanitizationResult:
        """
        Sanitize assessment data while preserving educational value

        Args:
            assessment_data: Assessment or quiz data

        Returns:
            SanitizationResult with sanitized assessment data
        """
        start_time = datetime.now()

        try:
            sanitized_data = {}
            warnings = []

            for field, value in assessment_data.items():
                if field in ['questions', 'answers', 'feedback', 'explanation']:
                    # Educational content - sanitize but preserve structure
                    sanitized_data[field] = self._sanitize_educational_content(value)
                elif field in ['user_id', 'session_id', 'submission_id']:
                    # Anonymize identifiers
                    sanitized_data[field] = self._anonymize_value(value)
                    warnings.append(f"Anonymized identifier: {field}")
                elif field in ['score', 'difficulty', 'category', 'type', 'duration']:
                    # Safe metadata
                    sanitized_data[field] = value
                else:
                    # Default sanitization
                    sanitized_data[field] = self._sanitize_content(value, field)

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return SanitizationResult(
                sanitized_data=sanitized_data,
                warnings=warnings,
                original_size_bytes=len(str(assessment_data)),
                sanitized_size_bytes=len(str(sanitized_data)),
                processing_time_ms=processing_time,
                compliance_score=90.0
            )

        except Exception as e:
            logger.error(f"Error sanitizing assessment data: {e}")
            return SanitizationResult(
                sanitized_data={},
                warnings=[f"Assessment sanitization failed: {str(e)}"],
                compliance_score=0.0
            )

    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if a field name indicates sensitive data"""
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in self.sensitive_fields)

    def _is_safe_field(self, field_name: str) -> bool:
        """Check if a field name indicates safe learning data"""
        field_lower = field_name.lower()
        return any(safe in field_lower for safe in self.safe_fields)

    def _sanitize_content(self, value: Any, field_name: str) -> Any:
        """Apply general content sanitization based on data type"""
        try:
            if isinstance(value, str):
                return self._sanitize_text_content(value)
            elif isinstance(value, dict):
                return {k: self._sanitize_content(v, k) for k, v in value.items()
                       if not self._is_sensitive_field(k)}
            elif isinstance(value, list):
                return [self._sanitize_content(item, field_name) for item in value]
            else:
                # Numbers, booleans, etc. are generally safe
                return value
        except Exception as e:
            logger.error(f"Error sanitizing content for field {field_name}: {e}")
            return None

    def _sanitize_text_content(self, text: str) -> str:
        """Sanitize text content by removing PII patterns"""
        if not isinstance(text, str):
            return str(text) if text is not None else ""

        sanitized = text

        # Apply PII pattern removal
        for pii_type, pattern in self.pii_patterns.items():
            if pii_type == 'email':
                sanitized = pattern.sub('[EMAIL_REMOVED]', sanitized)
            elif pii_type == 'phone':
                sanitized = pattern.sub('[PHONE_REMOVED]', sanitized)
            elif pii_type == 'ssn':
                sanitized = pattern.sub('[SSN_REMOVED]', sanitized)
            elif pii_type == 'credit_card':
                sanitized = pattern.sub('[CARD_REMOVED]', sanitized)
            elif pii_type == 'ip_address':
                sanitized = pattern.sub('[IP_REMOVED]', sanitized)
            elif pii_type == 'api_key':
                # Only remove if it looks like a real API key
                matches = pattern.findall(sanitized)
                for match in matches:
                    if len(match) > 25 and any(c.isdigit() for c in match) and any(c.isalpha() for c in match):
                        sanitized = sanitized.replace(match, '[API_KEY_REMOVED]')

        # Remove URLs with sensitive parameters
        url_pattern = self.pii_patterns['url_with_params']
        sanitized = url_pattern.sub(lambda m: m.group(0).split('?')[0], sanitized)

        return sanitized

    def _remove_personal_comments(self, code: str, language: str) -> str:
        """Remove personal comments from code that might contain PII"""
        try:
            lines = code.split('\n')
            sanitized_lines = []

            comment_patterns = {
                'python': r'^\s*#',
                'javascript': r'^\s*//',
                'java': r'^\s*//',
                'cpp': r'^\s*//',
                'c': r'^\s*//'
            }

            pattern = comment_patterns.get(language.lower(), r'^\s*#')
            comment_regex = re.compile(pattern)

            for line in lines:
                if comment_regex.match(line):
                    # Check if comment contains personal information
                    if self._contains_personal_info(line):
                        sanitized_lines.append(re.sub(r'#.*|//.*', '# [Comment removed for privacy]', line))
                    else:
                        sanitized_lines.append(line)
                else:
                    sanitized_lines.append(line)

            return '\n'.join(sanitized_lines)

        except Exception as e:
            logger.error(f"Error removing personal comments: {e}")
            return code

    def _contains_personal_info(self, text: str) -> bool:
        """Check if text contains personal information patterns"""
        personal_keywords = [
            'name', 'email', 'phone', 'address', 'birthday', 'ssn',
            'personal', 'private', 'confidential', 'my ', 'author:',
            'created by', 'contact', '@', 'tel:', 'mobile'
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in personal_keywords)

    def _remove_sensitive_patterns(self, text: str) -> str:
        """Remove sensitive data patterns from text"""
        sanitized = text

        for pii_type, pattern in self.pii_patterns.items():
            sanitized = pattern.sub(f'[{pii_type.upper()}_REMOVED]', sanitized)

        return sanitized

    def _sanitize_hardcoded_secrets(self, code: str) -> str:
        """Remove hardcoded secrets and credentials from code"""
        try:
            # Patterns for common secret formats
            secret_patterns = [
                (r'password\s*=\s*["\']([^"\']+)["\']', 'password = "[PASSWORD_REMOVED]"'),
                (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', 'api_key = "[API_KEY_REMOVED]"'),
                (r'secret\s*=\s*["\']([^"\']+)["\']', 'secret = "[SECRET_REMOVED]"'),
                (r'token\s*=\s*["\']([^"\']+)["\']', 'token = "[TOKEN_REMOVED]"'),
                (r'database_url\s*=\s*["\']([^"\']+)["\']', 'database_url = "[DATABASE_URL_REMOVED]"'),
            ]

            sanitized_code = code
            for pattern, replacement in secret_patterns:
                sanitized_code = re.sub(pattern, replacement, sanitized_code, flags=re.IGNORECASE)

            return sanitized_code

        except Exception as e:
            logger.error(f"Error sanitizing hardcoded secrets: {e}")
            return code

    def _sanitize_content_references(self, content: Any) -> Any:
        """Sanitize content that may reference external resources"""
        try:
            if isinstance(content, str):
                return self._sanitize_text_content(content)
            elif isinstance(content, dict):
                sanitized = {}
                for key, value in content.items():
                    if key.lower() in ['url', 'link', 'reference', 'source']:
                        # Sanitize URLs and references
                        sanitized[key] = self._sanitize_url(value)
                    else:
                        sanitized[key] = self._sanitize_content_references(value)
                return sanitized
            elif isinstance(content, list):
                return [self._sanitize_content_references(item) for item in content]
            else:
                return content
        except Exception as e:
            logger.error(f"Error sanitizing content references: {e}")
            return content

    def _sanitize_url(self, url: str) -> str:
        """Sanitize URLs by removing sensitive parameters"""
        if not isinstance(url, str):
            return str(url) if url is not None else ""

        try:
            # Remove query parameters that might contain sensitive data
            if '?' in url:
                base_url = url.split('?')[0]
                return base_url
            return url
        except Exception:
            return "[URL_REMOVED]"

    def _sanitize_educational_content(self, content: Any) -> Any:
        """Sanitize educational content while preserving learning value"""
        try:
            if isinstance(content, str):
                # Remove PII but preserve educational examples
                sanitized = self._sanitize_text_content(content)

                # Replace removed placeholders with educational equivalents
                replacements = {
                    '[EMAIL_REMOVED]': 'example@domain.com',
                    '[PHONE_REMOVED]': '(555) 123-4567',
                    '[IP_REMOVED]': '192.168.1.1',
                    '[URL_REMOVED]': 'https://example.com'
                }

                for placeholder, replacement in replacements.items():
                    sanitized = sanitized.replace(placeholder, replacement)

                return sanitized
            elif isinstance(content, dict):
                return {k: self._sanitize_educational_content(v) for k, v in content.items()}
            elif isinstance(content, list):
                return [self._sanitize_educational_content(item) for item in content]
            else:
                return content
        except Exception as e:
            logger.error(f"Error sanitizing educational content: {e}")
            return content

    def _anonymize_value(self, value: Any) -> str:
        """Anonymize a value using consistent hashing"""
        try:
            if value is None:
                return "anonymous_null"

            # Create consistent hash
            value_str = str(value)
            hash_input = f"{value_str}{self.anonymization_salt}"
            hash_object = hashlib.sha256(hash_input.encode())
            return f"anonymous_{hash_object.hexdigest()[:12]}"
        except Exception as e:
            logger.error(f"Error anonymizing value: {e}")
            return "anonymous_error"

    def _preserve_learning_context(self, sanitized_data: Dict[str, Any],
                                 original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preserve important learning context after sanitization"""
        try:
            # Ensure learning-critical fields are preserved
            learning_critical_fields = [
                'learning_goals', 'experience_level', 'preferred_pace',
                'learning_styles', 'career_stage', 'time_availability',
                'difficulty_preferences', 'topics_of_interest'
            ]

            for field in learning_critical_fields:
                if field in original_data and field not in sanitized_data:
                    # Try to preserve in sanitized form
                    sanitized_value = self._sanitize_content(original_data[field], field)
                    if sanitized_value:
                        sanitized_data[field] = sanitized_value

            return sanitized_data

        except Exception as e:
            logger.error(f"Error preserving learning context: {e}")
            return sanitized_data

    def _calculate_compliance_score(self, original_data: Dict[str, Any],
                                  sanitized_data: Dict[str, Any],
                                  removed_fields: List[str],
                                  anonymized_fields: List[str]) -> float:
        """Calculate privacy compliance score (0-100)"""
        try:
            score = 100.0

            # Penalize for sensitive fields that weren't removed or anonymized
            total_fields = len(original_data)
            sensitive_fields_found = sum(1 for field in original_data.keys()
                                       if self._is_sensitive_field(field))
            sensitive_fields_handled = len(removed_fields) + len(anonymized_fields)

            if sensitive_fields_found > 0:
                unhandled_sensitive = sensitive_fields_found - sensitive_fields_handled
                score -= (unhandled_sensitive / sensitive_fields_found) * 30

            # Bonus for proactive anonymization
            if len(anonymized_fields) > 0:
                score += min(10.0, len(anonymized_fields) * 2)

            # Check for potential PII in sanitized data
            sanitized_str = str(sanitized_data).lower()
            pii_indicators = ['email', 'phone', 'ssn', 'password', 'secret']
            pii_found = sum(1 for indicator in pii_indicators if indicator in sanitized_str)
            score -= pii_found * 5

            return max(0.0, min(100.0, score))

        except Exception as e:
            logger.error(f"Error calculating compliance score: {e}")
            return 50.0  # Default moderate score

    def get_sanitization_report(self, results: List[SanitizationResult]) -> Dict[str, Any]:
        """Generate comprehensive sanitization report"""
        try:
            if not results:
                return {"error": "No sanitization results provided"}

            total_original_size = sum(r.original_size_bytes for r in results)
            total_sanitized_size = sum(r.sanitized_size_bytes for r in results)
            total_processing_time = sum(r.processing_time_ms for r in results)
            average_compliance_score = sum(r.compliance_score for r in results) / len(results)

            all_removed_fields = []
            all_anonymized_fields = []
            all_warnings = []

            for result in results:
                all_removed_fields.extend(result.removed_fields)
                all_anonymized_fields.extend(result.anonymized_fields)
                all_warnings.extend(result.warnings)

            return {
                "summary": {
                    "total_datasets_processed": len(results),
                    "total_original_size_bytes": total_original_size,
                    "total_sanitized_size_bytes": total_sanitized_size,
                    "size_reduction_percentage": ((total_original_size - total_sanitized_size) /
                                                max(1, total_original_size)) * 100,
                    "total_processing_time_ms": total_processing_time,
                    "average_compliance_score": round(average_compliance_score, 2)
                },
                "privacy_actions": {
                    "fields_removed": len(set(all_removed_fields)),
                    "fields_anonymized": len(set(all_anonymized_fields)),
                    "unique_removed_fields": list(set(all_removed_fields)),
                    "unique_anonymized_fields": list(set(all_anonymized_fields))
                },
                "warnings": {
                    "total_warnings": len(all_warnings),
                    "unique_warnings": list(set(all_warnings))
                },
                "compliance": {
                    "overall_score": round(average_compliance_score, 2),
                    "privacy_level": self._get_privacy_level(average_compliance_score),
                    "recommendations": self._get_compliance_recommendations(results)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating sanitization report: {e}")
            return {"error": f"Failed to generate report: {str(e)}"}

    def _get_privacy_level(self, score: float) -> str:
        """Get privacy level description based on compliance score"""
        if score >= 90:
            return "Excellent - Highly compliant with privacy regulations"
        elif score >= 80:
            return "Good - Generally compliant with minor areas for improvement"
        elif score >= 70:
            return "Fair - Adequate privacy protection with some concerns"
        elif score >= 60:
            return "Poor - Significant privacy risks present"
        else:
            return "Critical - Major privacy violations possible"

    def _get_compliance_recommendations(self, results: List[SanitizationResult]) -> List[str]:
        """Generate recommendations for improving compliance"""
        recommendations = []

        avg_score = sum(r.compliance_score for r in results) / len(results)
        total_warnings = sum(len(r.warnings) for r in results)

        if avg_score < 80:
            recommendations.append("Increase PII removal and anonymization")

        if total_warnings > len(results) * 2:
            recommendations.append("Review and address frequent sanitization warnings")

        if any(r.processing_time_ms > 1000 for r in results):
            recommendations.append("Optimize sanitization performance for large datasets")

        if not recommendations:
            recommendations.append("Maintain current privacy practices")

        return recommendations


# Convenience functions for easy integration
def sanitize_for_ml(data: Dict[str, Any], data_type: str = "general") -> Dict[str, Any]:
    """
    Convenience function for quick data sanitization

    Args:
        data: Data to sanitize
        data_type: Type of data ('preferences', 'code', 'learning', 'assessment')

    Returns:
        Sanitized data dictionary
    """
    sanitizer = DataSanitizer()

    if data_type == "preferences":
        result = sanitizer.sanitize_user_preferences(data)
    elif data_type == "code":
        # Assuming data contains 'code' field
        code = data.get('code', '')
        language = data.get('language', 'unknown')
        sanitized_code = sanitizer.sanitize_code(code, language)
        result = SanitizationResult(sanitized_data={'code': sanitized_code})
    elif data_type == "learning":
        result = sanitizer.sanitize_learning_content(data)
    elif data_type == "assessment":
        result = sanitizer.sanitize_assessment_data(data)
    else:
        # General sanitization
        result = SanitizationResult(
            sanitized_data=sanitizer._sanitize_content(data, "general")
        )

    return result.sanitized_data


def create_privacy_config(level: str = "standard") -> SanitizationConfig:
    """
    Create predefined sanitization configuration

    Args:
        level: Privacy level ('minimal', 'standard', 'strict', 'maximum')

    Returns:
        SanitizationConfig object
    """
    if level == "minimal":
        return SanitizationConfig(
            remove_pii=True,
            anonymize_identifiers=False,
            hash_sensitive_fields=False,
            remove_personal_comments=False,
            sensitivity_level=SensitivityLevel.PUBLIC
        )
    elif level == "standard":
        return SanitizationConfig(
            remove_pii=True,
            anonymize_identifiers=True,
            hash_sensitive_fields=True,
            remove_personal_comments=True,
            sensitivity_level=SensitivityLevel.INTERNAL
        )
    elif level == "strict":
        return SanitizationConfig(
            remove_pii=True,
            anonymize_identifiers=True,
            hash_sensitive_fields=True,
            remove_personal_comments=True,
            max_text_length=5000,
            sensitivity_level=SensitivityLevel.CONFIDENTIAL
        )
    elif level == "maximum":
        return SanitizationConfig(
            remove_pii=True,
            anonymize_identifiers=True,
            hash_sensitive_fields=True,
            remove_personal_comments=True,
            preserve_learning_context=False,
            max_text_length=2000,
            sensitivity_level=SensitivityLevel.RESTRICTED
        )
    else:
        return SanitizationConfig()  # Default standard config


# Export key classes and functions
__all__ = [
    'DataSanitizer', 'SanitizationConfig', 'SanitizationResult',
    'SensitivityLevel', 'DataCategory',
    'sanitize_for_ml', 'create_privacy_config'
]