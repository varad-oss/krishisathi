import logging
logger = logging.getLogger(__name__)

import os
from typing import List

# Attempt to import Earth Engine, but handle environments where it's not installed or authenticated
try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False

class EarthEngineService:
    def __init__(self):
        self.initialized = False
        if EE_AVAILABLE:
            try:
                # In production, this would use a service account key
                # For noncommercial / research use, we authenticate with standard credentials
                ee.Initialize()
                self.initialized = True
            except Exception as e:
                logger.info(f"Earth Engine initialization failed: {e}")
                logger.info("Falling back to simulated NDVI estimation pipeline.")

    def calculate_regional_ndvi(self, region_geometry, start_date: str, end_date: str) -> dict:
        """
        Calculate the mean NDVI for a given geometric region over a time period
        using the Sentinel-2 surface reflectance dataset.
        """
        if not self.initialized:
            return {
                "status": "unavailable",
                "source": "google-earth-engine",
                "message": "Earth Engine credentials not initialized."
            }

        try:
            # Real Earth Engine Pipeline for Noncommercial/Research tier
            # Load Sentinel-2 harmonized surface reflectance
            collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                          .filterBounds(region_geometry)
                          .filterDate(start_date, end_date)
                          # Pre-filter for mostly cloud-free scenes
                          .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

            # Function to calculate NDVI and add it as a band
            def add_ndvi(image):
                ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
                return image.addBands(ndvi)

            # Map the function over the collection and take the median to reduce clouds
            ndvi_collection = collection.map(add_ndvi)
            median_ndvi_image = ndvi_collection.select('NDVI').median()

            # Reduce the region to get the mean NDVI
            mean_dict = median_ndvi_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region_geometry,
                scale=10, # Sentinel-2 resolution is 10m
                maxPixels=1e9
            )
            
            result = mean_dict.getInfo()
            if 'NDVI' not in result or result['NDVI'] is None:
                return {
                    "status": "no-data",
                    "source": "google-earth-engine"
                }
                
            return {
                "status": "available",
                "value": result['NDVI'],
                "source": "sentinel-2",
                "provider": "google-earth-engine"
            }
            
        except Exception as e:
            logger.error(f"Earth Engine calculation error: {e}")
            return {
                "status": "unavailable",
                "source": "google-earth-engine",
                "message": "Earth Engine data is temporarily unavailable."
            }

earth_engine_service = EarthEngineService()
