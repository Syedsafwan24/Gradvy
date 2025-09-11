// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/utils/accessibility.js
// Accessibility utilities and helpers for WCAG 2.1 AA compliance
// Provides reusable functions for keyboard navigation, ARIA attributes, and screen readers
// RELEVANT FILES: All UI components, Button.jsx, Input.jsx, CourseCard.jsx

'use client';

/**
 * Generate unique IDs for ARIA labels and descriptions
 */
export const generateId = (prefix = 'gradvy') => {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Create ARIA label props for components
 */
export const createAriaProps = (label, describedBy = null, labelledBy = null) => {
  const props = {};
  
  if (label) {
    props['aria-label'] = label;
  }
  
  if (describedBy) {
    props['aria-describedby'] = describedBy;
  }
  
  if (labelledBy) {
    props['aria-labelledby'] = labelledBy;
  }
  
  return props;
};

/**
 * Handle keyboard navigation for interactive elements
 */
export const handleKeyboardNavigation = (event, actions = {}) => {
  const { onEnter, onSpace, onEscape, onArrowUp, onArrowDown, onArrowLeft, onArrowRight } = actions;
  
  switch (event.key) {
    case 'Enter':
      event.preventDefault();
      onEnter && onEnter(event);
      break;
    case ' ': // Space
      event.preventDefault();
      onSpace && onSpace(event);
      break;
    case 'Escape':
      event.preventDefault();
      onEscape && onEscape(event);
      break;
    case 'ArrowUp':
      event.preventDefault();
      onArrowUp && onArrowUp(event);
      break;
    case 'ArrowDown':
      event.preventDefault();
      onArrowDown && onArrowDown(event);
      break;
    case 'ArrowLeft':
      event.preventDefault();
      onArrowLeft && onArrowLeft(event);
      break;
    case 'ArrowRight':
      event.preventDefault();
      onArrowRight && onArrowRight(event);
      break;
    default:
      // Allow default behavior for other keys
      break;
  }
};

/**
 * Manage focus for modals and overlays
 */
export class FocusManager {
  constructor() {
    this.focusableElements = [
      'button',
      '[href]',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable]'
    ].join(', ');
  }

  getFocusableElements(container) {
    return container.querySelectorAll(this.focusableElements);
  }

  trapFocus(container) {
    const focusableElements = this.getFocusableElements(container);
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (event) => {
      if (event.key !== 'Tab') return;

      if (event.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);
    
    // Focus first element
    if (firstElement) {
      firstElement.focus();
    }

    // Return cleanup function
    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  }

  restoreFocus(element) {
    if (element && element.focus) {
      element.focus();
    }
  }
}

/**
 * Announce messages to screen readers
 */
export const announceToScreenReader = (message, priority = 'polite') => {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};

/**
 * Check color contrast ratio (basic implementation)
 */
export const checkContrast = (foreground, background) => {
  // Convert hex to RGB
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  };

  const getLuminance = (rgb) => {
    const { r, g, b } = rgb;
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };

  const fg = hexToRgb(foreground);
  const bg = hexToRgb(background);
  
  if (!fg || !bg) return false;

  const l1 = getLuminance(fg);
  const l2 = getLuminance(bg);
  
  const contrast = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  
  return {
    ratio: contrast,
    AA: contrast >= 4.5,
    AAA: contrast >= 7
  };
};

/**
 * Skip link component props
 */
export const createSkipLinkProps = (targetId, text = 'Skip to main content') => ({
  href: `#${targetId}`,
  className: 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded z-50',
  children: text,
  onFocus: (e) => e.target.scrollIntoView({ behavior: 'smooth' })
});

/**
 * ARIA live region for dynamic content updates
 */
export const createLiveRegion = (type = 'polite') => {
  const region = document.createElement('div');
  region.setAttribute('aria-live', type);
  region.setAttribute('aria-atomic', 'true');
  region.className = 'sr-only';
  region.id = `live-region-${type}`;
  
  if (!document.getElementById(region.id)) {
    document.body.appendChild(region);
  }
  
  return {
    announce: (message) => {
      region.textContent = message;
      setTimeout(() => {
        region.textContent = '';
      }, 1000);
    },
    remove: () => {
      if (region.parentNode) {
        region.parentNode.removeChild(region);
      }
    }
  };
};

/**
 * Enhanced button props for accessibility
 */
export const createAccessibleButtonProps = ({
  onClick,
  disabled = false,
  ariaLabel,
  ariaPressed,
  ariaExpanded,
  role = 'button',
  type = 'button'
}) => ({
  type,
  role,
  disabled,
  'aria-label': ariaLabel,
  'aria-pressed': ariaPressed,
  'aria-expanded': ariaExpanded,
  'aria-disabled': disabled,
  tabIndex: disabled ? -1 : 0,
  onClick: disabled ? undefined : onClick,
  onKeyDown: disabled ? undefined : (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onClick && onClick(event);
    }
  }
});

export default {
  generateId,
  createAriaProps,
  handleKeyboardNavigation,
  FocusManager,
  announceToScreenReader,
  checkContrast,
  createSkipLinkProps,
  createLiveRegion,
  createAccessibleButtonProps
};