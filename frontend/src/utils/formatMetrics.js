/**
 * Metric Formatting Utilities for FairFlow
 * 
 * These functions round values ONLY for UI display.
 * Full precision is maintained in backend calculations and database.
 */

/**
 * Format effort scores with 1 decimal place
 * @param {number} value - Raw effort score
 * @returns {string} Formatted effort (e.g., "62.4")
 */
export function formatEffort(value) {
    if (value == null || isNaN(value)) return '0.0';
    return Number(value).toFixed(1);
}

/**
 * Format credit values as integers
 * @param {number} value - Raw credits
 * @returns {number} Rounded credits (e.g., 3)
 */
export function formatCredits(value) {
    if (value == null || isNaN(value)) return 0;
    return Math.round(value);
}

/**
 * Format balance as integer
 * @param {number} value - Raw balance
 * @returns {number} Rounded balance (e.g., -2)
 */
export function formatBalance(value) {
    if (value == null || isNaN(value)) return 0;
    return Math.round(value);
}

/**
 * Add sign prefix for credits/balance display
 * @param {number} value - Numeric value
 * @returns {string} Value with + or - prefix (e.g., "+3", "-12")
 */
export function withSign(value) {
    if (value > 0) return `+${value}`;
    return String(value);
}
