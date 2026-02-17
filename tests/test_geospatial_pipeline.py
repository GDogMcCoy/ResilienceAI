"""
Tests for Geospatial Pipeline
"""
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

import numpy as np
import rasterio
from rasterio.transform import from_bounds

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from geospatial.usgs_3dep import (
    USGS3DEPClient, 
    DEMProcessor, 
    BoundingBox
)
from geospatial.naip import NAIPClient, NAIPProcessor
from geospatial.gee_integration import GEEClient, MockGEEClient, get_gee_client
from geospatial.pipeline import (
    GeospatialPipeline,
    PipelineConfig,
    PipelineResult,
    DataSource,
    ProcessingStep,
    BuildingFootprintExtractor,
    LandCoverClassifier
)


class TestBoundingBox(unittest.TestCase):
    """Test BoundingBox class"""
    
    def test_creation(self):
        bbox = BoundingBox(min_x=-90, min_y=38, max_x=-89, max_y=39)
        self.assertEqual(bbox.min_x, -90)
        self.assertEqual(bbox.min_y, 38)
        self.assertEqual(bbox.max_x, -89)
        self.assertEqual(bbox.max_y, 39)
    
    def test_to_list(self):
        bbox = BoundingBox(min_x=-90, min_y=38, max_x=-89, max_y=39)
        self.assertEqual(bbox.to_list(), [-90, 38, -89, 39])
    
    def test_center(self):
        bbox = BoundingBox(min_x=-90, min_y=38, max_x=-89, max_y=39)
        self.assertEqual(bbox.center, (-89.5, 38.5))
    
    def test_area(self):
        bbox = BoundingBox(min_x=-90, min_y=38, max_x=-89, max_y=39)
        self.assertEqual(bbox.area, 1.0)


class TestUSGS3DEPClient(unittest.TestCase):
    """Test USGS 3DEP client"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.client = USGS3DEPClient(cache_dir=self.temp_dir)
    
    def test_initialization(self):
        self.assertIsNotNone(self.client.cache_dir)
        self.assertTrue(self.client.cache_dir.exists())
    
    def test_missouri_test_bbox(self):
        bbox = self.client.MISSOURI_TEST_BBOX
        self.assertIsInstance(bbox, BoundingBox)
        self.assertEqual(bbox.min_x, -90.5)
        self.assertEqual(bbox.min_y, 38.5)
    
    @patch('geospatial.usgs_3dep.requests.Session.get')
    def test_search_products(self, mock_get):
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"title": "Test DEM 1", "downloadURL": "http://example.com/1.tif"},
                {"title": "Test DEM 2", "downloadURL": "http://example.com/2.tif"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        bbox = BoundingBox(min_x=-90, min_y=38, max_x=-89, max_y=39)
        products = self.client.search_products(bbox)
        
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]["title"], "Test DEM 1")
    
    @patch('geospatial.usgs_3dep.requests.Session.get')
    def test_search_products_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        
        bbox = BoundingBox(min_x=-90, min_y=38, max_x=-89, max_y=39)
        products = self.client.search_products(bbox)
        
        self.assertEqual(len(products), 0)


class TestDEMProcessor(unittest.TestCase):
    """Test DEM processing functions"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.dem_path = Path(self.temp_dir) / "test_dem.tif"
        
        # Create test DEM
        self.create_test_dem()
    
    def create_test_dem(self):
        """Create a simple test DEM"""
        # Create a sloped surface
        x = np.linspace(0, 100, 100)
        y = np.linspace(0, 100, 100)
        xx, yy = np.meshgrid(x, y)
        dem = xx * 0.5 + yy * 0.3  # Simple slope
        
        transform = from_bounds(-90, 38, -89, 39, 100, 100)
        
        with rasterio.open(
            self.dem_path,
            'w',
            driver='GTiff',
            height=100,
            width=100,
            count=1,
            dtype=dem.dtype,
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            dst.write(dem, 1)
    
    def test_slope_calculation(self):
        output_path = Path(self.temp_dir) / "slope.tif"
        
        with DEMProcessor(self.dem_path) as processor:
            result = processor.calculate_slope(output_path)
            
            self.assertTrue(result.exists())
            
            with rasterio.open(result) as src:
                self.assertEqual(src.count, 1)
                slope = src.read(1)
                self.assertTrue(np.all(slope >= 0))
    
    def test_aspect_calculation(self):
        output_path = Path(self.temp_dir) / "aspect.tif"
        
        with DEMProcessor(self.dem_path) as processor:
            result = processor.calculate_aspect(output_path)
            
            self.assertTrue(result.exists())
            
            with rasterio.open(result) as src:
                self.assertEqual(src.count, 1)
    
    def test_hillshade_calculation(self):
        output_path = Path(self.temp_dir) / "hillshade.tif"
        
        with DEMProcessor(self.dem_path) as processor:
            result = processor.calculate_hillshade(output_path)
            
            self.assertTrue(result.exists())
            
            with rasterio.open(result) as src:
                self.assertEqual(src.count, 1)
                hillshade = src.read(1)
                self.assertTrue(np.all((hillshade >= 0) & (hillshade <= 255)))
    
    def test_tpi_calculation(self):
        output_path = Path(self.temp_dir) / "tpi.tif"
        
        with DEMProcessor(self.dem_path) as processor:
            result = processor.calculate_tpi(output_path)
            
            self.assertTrue(result.exists())
    
    def test_elevation_stats(self):
        with DEMProcessor(self.dem_path) as processor:
            stats = processor.get_elevation_stats()
            
            self.assertIn("min", stats)
            self.assertIn("max", stats)
            self.assertIn("mean", stats)
            self.assertIn("std", stats)


class TestNAIPClient(unittest.TestCase):
    """Test NAIP client"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.client = NAIPClient(cache_dir=self.temp_dir)
    
    def test_initialization(self):
        self.assertIsNotNone(self.client.cache_dir)
        self.assertTrue(self.client.cache_dir.exists())
    
    @patch('geospatial.naip.requests.Session.post')
    def test_search_stac(self, mock_post):
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "features": [
                {
                    "id": "test-1",
                    "properties": {"eo:cloud_cover": 5},
                    "assets": {"image": {"href": "http://example.com/1.tif"}}
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        bbox = (-90, 38, -89, 39)
        items = self.client.search_stac(bbox)
        
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "test-1")


class TestNAIPProcessor(unittest.TestCase):
    """Test NAIP processing functions"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.naip_path = Path(self.temp_dir) / "test_naip.tif"
        
        # Create test 4-band NAIP image
        self.create_test_naip()
    
    def create_test_naip(self):
        """Create a test 4-band NAIP image"""
        # Create simple test data
        red = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        green = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        blue = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        nir = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        transform = from_bounds(-90, 38, -89, 39, 100, 100)
        
        with rasterio.open(
            self.naip_path,
            'w',
            driver='GTiff',
            height=100,
            width=100,
            count=4,
            dtype=np.uint8,
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            dst.write(red, 1)
            dst.write(green, 2)
            dst.write(blue, 3)
            dst.write(nir, 4)
    
    def test_ndvi_calculation(self):
        output_path = Path(self.temp_dir) / "ndvi.tif"
        
        with NAIPProcessor(self.naip_path) as processor:
            result = processor.calculate_ndvi(output_path)
            
            self.assertTrue(result.exists())
            
            with rasterio.open(result) as src:
                self.assertEqual(src.count, 1)
                ndvi = src.read(1)
                self.assertTrue(np.all((ndvi >= -1) & (ndvi <= 1)))
    
    def test_ndwi_calculation(self):
        output_path = Path(self.temp_dir) / "ndwi.tif"
        
        with NAIPProcessor(self.naip_path) as processor:
            result = processor.calculate_ndwi(output_path)
            
            self.assertTrue(result.exists())
    
    def test_texture_calculation(self):
        output_path = Path(self.temp_dir) / "texture.tif"
        
        with NAIPProcessor(self.naip_path) as processor:
            result = processor.calculate_texture(output_path)
            
            self.assertTrue(result.exists())
    
    def test_water_mask(self):
        output_path = Path(self.temp_dir) / "water_mask.tif"
        
        with NAIPProcessor(self.naip_path) as processor:
            result = processor.detect_water_bodies(output_path)
            
            self.assertTrue(result.exists())
            
            with rasterio.open(result) as src:
                mask = src.read(1)
                self.assertTrue(np.all(np.isin(mask, [0, 1])))


class TestGEEIntegration(unittest.TestCase):
    """Test GEE integration"""
    
    def test_mock_client_creation(self):
        client = MockGEEClient()
        self.assertTrue(client.is_initialized())
    
    def test_mock_client_bbox(self):
        client = MockGEEClient()
        bbox = client.MISSOURI_TEST_BBOX
        self.assertIn("west", bbox)
        self.assertIn("south", bbox)
    
    def test_mock_get_collection(self):
        client = MockGEEClient()
        result = client.get_sentinel2_collection({}, "2020-01-01", "2020-12-31")
        self.assertIsNotNone(result)
    
    def test_get_gee_client_mock(self):
        client = get_gee_client(use_mock=True)
        self.assertIsInstance(client, MockGEEClient)


class TestGeospatialPipeline(unittest.TestCase):
    """Test main pipeline"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = PipelineConfig(
            output_dir=Path(self.temp_dir),
            max_workers=1
        )
    
    def test_pipeline_initialization(self):
        pipeline = GeospatialPipeline(self.config)
        self.assertIsNotNone(pipeline.usgs_client)
        self.assertIsNotNone(pipeline.naip_client)
        self.assertIsNotNone(pipeline.gee_client)
    
    def test_default_bbox(self):
        pipeline = GeospatialPipeline(self.config)
        bbox = pipeline.DEFAULT_BBOX
        self.assertIsInstance(bbox, BoundingBox)
        self.assertEqual(bbox.min_x, -90.5)
    
    @patch.object(GeospatialPipeline, '_acquire_data')
    @patch.object(GeospatialPipeline, '_process_data')
    @patch.object(GeospatialPipeline, '_create_cogs')
    def test_run_pipeline(self, mock_cogs, mock_process, mock_acquire):
        # Mock return values
        mock_acquire.return_value = {"dem": Path("/tmp/test_dem.tif")}
        mock_process.return_value = {"slope": Path("/tmp/test_slope.tif")}
        mock_cogs.return_value = {"slope_cog": Path("/tmp/test_slope_cog.tif")}
        
        pipeline = GeospatialPipeline(self.config)
        result = pipeline.run(region_name="test_region")
        
        self.assertIsInstance(result, PipelineResult)
        self.assertTrue(result.success)
    
    def test_list_products_empty(self):
        pipeline = GeospatialPipeline(self.config)
        products = pipeline.list_products("nonexistent")
        self.assertEqual(len(products), 0)


class TestBuildingFootprintExtractor(unittest.TestCase):
    """Test building footprint extraction"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = BuildingFootprintExtractor(cache_dir=Path(self.temp_dir))
    
    def test_initialization(self):
        self.assertTrue(self.extractor.cache_dir.exists())


class TestLandCoverClassifier(unittest.TestCase):
    """Test land cover classification"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.classifier = LandCoverClassifier()
        
        # Create test NAIP image
        self.naip_path = Path(self.temp_dir) / "test_naip.tif"
        self.create_test_naip()
    
    def create_test_naip(self):
        """Create test 4-band image"""
        transform = from_bounds(-90, 38, -89, 39, 100, 100)
        
        with rasterio.open(
            self.naip_path,
            'w',
            driver='GTiff',
            height=100,
            width=100,
            count=4,
            dtype=np.uint8,
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            for i in range(1, 5):
                dst.write(np.random.randint(0, 255, (100, 100), dtype=np.uint8), i)
    
    def test_nlcd_classes(self):
        self.assertIn(11, self.classifier.NLCD_CLASSES)
        self.assertIn(82, self.classifier.NLCD_CLASSES)
        self.assertEqual(self.classifier.NLCD_CLASSES[11][0], "Open Water")
    
    @patch('geospatial.pipeline.KMeans')
    def test_classify_from_naip(self, mock_kmeans):
        # Mock KMeans
        mock_kmeans_instance = Mock()
        mock_kmeans_instance.fit_predict.return_value = np.zeros(10000, dtype=int)
        mock_kmeans.return_value = mock_kmeans_instance
        
        output_path = Path(self.temp_dir) / "land_cover.tif"
        result = self.classifier.classify_from_naip(
            self.naip_path,
            output_path=output_path
        )
        
        self.assertTrue(result.exists())


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_workflow_mock(self):
        """Test full workflow with mocked data"""
        temp_dir = tempfile.mkdtemp()
        
        # Create test DEM
        dem_path = Path(temp_dir) / "dem.tif"
        transform = from_bounds(-90.5, 38.5, -90.0, 39.0, 100, 100)
        
        with rasterio.open(
            dem_path,
            'w',
            driver='GTiff',
            height=100,
            width=100,
            count=1,
            dtype=np.float32,
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            dem = np.random.rand(100, 100).astype(np.float32) * 100
            dst.write(dem, 1)
        
        # Process DEM
        with DEMProcessor(dem_path) as processor:
            slope_path = Path(temp_dir) / "slope.tif"
            processor.calculate_slope(slope_path)
            self.assertTrue(slope_path.exists())
            
            aspect_path = Path(temp_dir) / "aspect.tif"
            processor.calculate_aspect(aspect_path)
            self.assertTrue(aspect_path.exists())
            
            hillshade_path = Path(temp_dir) / "hillshade.tif"
            processor.calculate_hillshade(hillshade_path)
            self.assertTrue(hillshade_path.exists())
            
            tpi_path = Path(temp_dir) / "tpi.tif"
            processor.calculate_tpi(tpi_path)
            self.assertTrue(tpi_path.exists())
        
        # Create test NAIP
        naip_path = Path(temp_dir) / "naip.tif"
        with rasterio.open(
            naip_path,
            'w',
            driver='GTiff',
            height=100,
            width=100,
            count=4,
            dtype=np.uint8,
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            for i in range(1, 5):
                dst.write(np.random.randint(0, 255, (100, 100), dtype=np.uint8), i)
        
        # Process NAIP
        with NAIPProcessor(naip_path) as processor:
            ndvi_path = Path(temp_dir) / "ndvi.tif"
            processor.calculate_ndvi(ndvi_path)
            self.assertTrue(ndvi_path.exists())
            
            ndwi_path = Path(temp_dir) / "ndwi.tif"
            processor.calculate_ndwi(ndwi_path)
            self.assertTrue(ndwi_path.exists())


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBoundingBox))
    suite.addTests(loader.loadTestsFromTestCase(TestUSGS3DEPClient))
    suite.addTests(loader.loadTestsFromTestCase(TestDEMProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestNAIPClient))
    suite.addTests(loader.loadTestsFromTestCase(TestNAIPProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestGEEIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestGeospatialPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestBuildingFootprintExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestLandCoverClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
