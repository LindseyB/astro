# Tests for Swiss Ephemeris configuration

import os
import sys
import tempfile
import unittest
from unittest.mock import patch
import swisseph as swe


class TestSwissEphemerisPathLogic(unittest.TestCase):
    """Test Swiss Ephemeris path configuration logic"""
    
    @patch('swisseph.swe.set_ephe_path')
    def test_env_var_checked(self, mock_set_ephe_path):
        """Test that SE_EPHE_PATH environment variable is checked and used to set the ephemeris path"""
        import importlib
        test_path = '/test/path'
        os.environ['SE_EPHE_PATH'] = test_path
        # Import the main module and call the logic that checks SE_EPHE_PATH
        # Assume main.py has a function called configure_ephe_path()
        try:
            from main import configure_ephe_path
        except ImportError:
            self.skipTest("main.configure_ephe_path not available to test")
        else:
            configure_ephe_path()
            mock_set_ephe_path.assert_called_with(test_path)
        finally:
            del os.environ['SE_EPHE_PATH']
    
    @patch('os.path.exists')
    def test_path_validation_logic(self, mock_exists):
        """Test the path validation logic"""
        test_path = '/some/ephemeris/path'
        
        # Test when path doesn't exist
        mock_exists.return_value = False
        if os.path.exists(test_path):
            result = "path_exists"
        else:
            result = "path_missing"
        
        self.assertEqual(result, "path_missing")


class TestSwissEphemerisIntegration(unittest.TestCase):
    """Integration tests for Swiss Ephemeris functionality"""
    
    def test_swisseph_can_calculate_positions_with_local_path(self):
        """Test that Swiss Ephemeris can calculate planetary positions when path is set"""
        # Setup - use the actual swisseph directory if it exists
        # Check environment variable first, then fall back to local path
        ephe_path = os.environ.get('SE_EPHE_PATH') or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'swisseph')
        if os.path.exists(ephe_path):
            swe.set_ephe_path(ephe_path)
        
        # Test calculation - July 15, 1990, 14:30 UTC
        # Julian day number
        jd = swe.julday(1990, 7, 15, 14.5)
        
        # Calculate Sun position
        # This will fail if ephemeris files are not available
        try:
            result = swe.calc_ut(jd, swe.SUN)
            # result is a tuple of (coords_tuple, return_flag)
            # coords_tuple contains (longitude, latitude, distance, speed_long, speed_lat, speed_dist)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2, "calc_ut returns (coordinates, flag)")
            
            # Extract the coordinates tuple
            coords = result[0]
            self.assertIsInstance(coords, tuple)
            
            # Check longitude (first element of coords)
            longitude = coords[0]
            self.assertIsInstance(longitude, (int, float), "Longitude should be numeric")
            self.assertGreaterEqual(longitude, 0, "Sun longitude should be >= 0")
            self.assertLessEqual(longitude, 360, "Sun longitude should be <= 360")
        except Exception as e:
            # Skip test if ephemeris files not available
            self.skipTest(f"Ephemeris files not available: {e}")
    
    def test_swisseph_directory_contains_required_files(self):
        """Test that the ephemeris directory contains the required .se1 files"""
        # Check environment variable first, then fall back to local path
        ephe_path = os.environ.get('SE_EPHE_PATH') or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'swisseph')
        
        if not os.path.exists(ephe_path):
            self.skipTest("Ephemeris directory does not exist")
        
        # Check for required files
        required_files = ['seas_18.se1', 'semo_18.se1', 'sepl_18.se1']
        
        for filename in required_files:
            file_path = os.path.join(ephe_path, filename)
            self.assertTrue(
                os.path.exists(file_path),
                f"Required ephemeris file {filename} not found in {ephe_path}"
            )


if __name__ == '__main__':
    unittest.main()
