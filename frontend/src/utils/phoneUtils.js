// File: frontend/src/utils/phoneUtils.js
// Description: Utility functions for phone number normalization and formatting
// Why: Standardizes phone numbers before sending to API and formats for display
// Relevant Files: ProfileInfo.jsx, GeneralSettings.jsx, backend/core/apps/auth/api/serializers.py

/**
 * Normalize phone number to E.164 format or backend-compatible format
 * Accepts various formats: 1234567890, (123) 456-7890, +1234567890, etc.
 * Returns: Digits only with + prefix if applicable
 *
 * @param {string} phone - Phone number in any format
 * @returns {string} - Normalized phone number
 *
 * Examples:
 * - normalizePhone("1234567890") -> "+1234567890"
 * - normalizePhone("(123) 456-7890") -> "+1234567890"
 * - normalizePhone("+1234567890") -> "+1234567890"
 * - normalizePhone("0123456789") -> "+0123456789"
 */
export function normalizePhone(phone) {
  // Return empty string if no phone provided
  if (!phone) return '';

  // Remove all non-digit characters (except +)
  let cleaned = phone.replace(/[^\d+]/g, '');

  // If empty after cleaning, return empty string
  if (!cleaned || cleaned === '+') return '';

  // If already starts with +, return as-is
  if (cleaned.startsWith('+')) {
    return cleaned;
  }

  // Add + prefix for international format
  return `+${cleaned}`;
}

/**
 * Format phone number for display (US format)
 * +1234567890 -> (123) 456-7890
 *
 * @param {string} phone - Phone number in any format
 * @returns {string} - Formatted phone number for display
 */
export function formatPhoneDisplay(phone) {
  if (!phone) return '';

  // Extract only digits
  const digits = phone.replace(/\D/g, '');

  // Format as (XXX) XXX-XXXX for 10-digit US numbers
  if (digits.length === 10) {
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
  }

  // Format as (XXX) XXX-XXXX for 11-digit numbers starting with 1
  if (digits.length === 11 && digits.startsWith('1')) {
    return `(${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7)}`;
  }

  // For other formats, just return the original
  return phone;
}

/**
 * Validate phone number format (basic validation)
 * Checks if phone has minimum required digits
 *
 * @param {string} phone - Phone number to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export function isValidPhoneFormat(phone) {
  if (!phone) return false;

  // Extract only digits
  const digits = phone.replace(/\D/g, '');

  // Phone should have at least 7 digits and max 15 digits (E.164 standard)
  return digits.length >= 7 && digits.length <= 15;
}
