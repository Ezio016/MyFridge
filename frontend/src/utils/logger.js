/**
 * Logger utility for consistent logging across the application
 * 
 * In development: logs everything to console
 * In production: only logs errors
 */

const isDev = import.meta.env.DEV;

export const logger = {
  /**
   * Debug-level logging (development only)
   */
  debug: (...args) => {
    if (isDev) {
      console.log('[DEBUG]', ...args);
    }
  },

  /**
   * Info-level logging (development only)
   */
  log: (...args) => {
    if (isDev) {
      console.log('[INFO]', ...args);
    }
  },

  /**
   * Warning-level logging (always logged)
   */
  warn: (...args) => {
    console.warn('[WARN]', ...args);
  },

  /**
   * Error-level logging (always logged)
   * TODO: Send to error tracking service (Sentry, LogRocket, etc.)
   */
  error: (...args) => {
    console.error('[ERROR]', ...args);
    
    // Future: Send to error tracking
    // if (window.Sentry) {
    //   window.Sentry.captureException(args[0]);
    // }
  },

  /**
   * Performance logging (development only)
   */
  perf: (label) => {
    if (isDev) {
      return {
        start: () => console.time(label),
        end: () => console.timeEnd(label),
      };
    }
    return { start: () => {}, end: () => {} };
  },
};

export default logger;

