// Static catalogues. Place coordinates are district headquarters, used only as query points.

export const CROPS = [
  'Wheat', 'Rice', 'Maize', 'Sorghum', 'Pearl millet', 'Finger millet', 'Chickpea', 'Pigeon pea',
  'Soybean', 'Groundnut', 'Mustard', 'Cotton', 'Sugarcane', 'Potato', 'Tomato', 'Onion',
] as const;
export type Crop = (typeof CROPS)[number];

export const PLACES = [
  { id: 'ludhiana', lat: 30.901, lng: 75.857 },
  { id: 'amritsar', lat: 31.634, lng: 74.872 },
  { id: 'pune', lat: 18.52, lng: 73.856 },
  { id: 'nashik', lat: 19.997, lng: 73.79 },
  { id: 'nagpur', lat: 21.146, lng: 79.088 },
  { id: 'belagavi', lat: 15.85, lng: 74.498 },
  { id: 'mysuru', lat: 12.296, lng: 76.639 },
  { id: 'thanjavur', lat: 10.787, lng: 79.138 },
  { id: 'coimbatore', lat: 11.017, lng: 76.956 },
  { id: 'lucknow', lat: 26.847, lng: 80.946 },
  { id: 'varanasi', lat: 25.318, lng: 82.974 },
  { id: 'indore', lat: 22.72, lng: 75.858 },
  { id: 'bhopal', lat: 23.26, lng: 77.413 },
  { id: 'rajkot', lat: 22.304, lng: 70.802 },
  { id: 'anand', lat: 22.556, lng: 72.951 },
  { id: 'bardhaman', lat: 23.232, lng: 87.863 },
] as const;
export type PlaceId = (typeof PLACES)[number]['id'];

export const STATE_CODES = ['PB', 'MH', 'KA', 'TN', 'UP', 'MP', 'GJ', 'WB'] as const;
