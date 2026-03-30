/**
 * Safely format a price value to fixed decimal string.
 * Handles both number and string (from backend Decimal serialization).
 */
export function formatPrice(value: number | string, decimals = 2): string {
  return Number(value).toFixed(decimals)
}

/**
 * Format price integer part only (e.g. "38" from 38.00)
 */
export function formatPriceInt(value: number | string): string {
  return Math.floor(Number(value)).toString()
}

/**
 * Format price decimal part only (e.g. "00" from 38.00)
 */
export function formatPriceDec(value: number | string): string {
  const num = Number(value)
  return Math.round((num % 1) * 100).toString().padStart(2, '0')
}
