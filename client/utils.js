/**
 * Utility functions for Lost & Found application
 */

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} text - Text to escape
 * @returns {string} Escaped HTML string
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Format item label to readable title case
 * @param {string} label - Label to format
 * @returns {string} Formatted label
 */
function formatLabel(label) {
    if (!label || !label.toString().trim()) {
        return 'Unknown Item';
    }
    const normalized = label.toString().replace(/_/g, ' ');
    return normalized
        .split(/\s+/)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Format timestamp to readable date/time string in Eastern Time
 * @param {string} timestamp - Timestamp in format YYYYMMDD_HHMMSS (stored as UTC)
 * @returns {string} Formatted date/time string in Eastern Time
 */
function formatTimestamp(timestamp) {
    if (!timestamp) return 'Unknown';
    
    try {
        // Parse timestamp format: YYYYMMDD_HHMMSS
        const year = timestamp.substring(0, 4);
        const month = timestamp.substring(4, 6);
        const day = timestamp.substring(6, 8);
        const hour = timestamp.substring(9, 11);
        const minute = timestamp.substring(11, 13);
        const second = timestamp.substring(13, 15);
        
        // Create date object in UTC (since server stores timestamps in UTC)
        // Using UTC constructor to avoid timezone conversion issues
        const date = new Date(Date.UTC(
            parseInt(year),
            parseInt(month) - 1, // Month is 0-indexed
            parseInt(day),
            parseInt(hour),
            parseInt(minute),
            parseInt(second)
        ));
        
        // Convert to Eastern Time and format
        // Eastern Time: America/New_York (handles EDT/EST automatically)
        const dateStr = date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            timeZone: 'America/New_York'
        });
        const timeStr = date.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit', 
            hour12: true,
            timeZone: 'America/New_York'
        });
        
        return `${dateStr} at ${timeStr}`;
    } catch (error) {
        console.error('Error formatting timestamp:', error);
        return timestamp; // Return original if parsing fails
    }
}

