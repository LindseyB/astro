"""
Tests for LaunchDarkly service
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from launchdarkly_service import LaunchDarklyService, should_show_chart_wheel, get_launchdarkly_service


class TestLaunchDarklyService:
    """Test cases for LaunchDarkly service"""
    
    def test_service_without_sdk_key(self):
        """Test service initialization without SDK key"""
        with patch.dict(os.environ, {}, clear=True):
            service = LaunchDarklyService()
            assert service.client is None
            
            # Should return default value when client is not available
            result = service.should_show_chart_wheel("test-user")
            assert result is False
    
    def test_service_with_sdk_key_success(self):
        """Test service initialization with valid SDK key"""
        mock_client = MagicMock()
        mock_client.is_initialized.return_value = True
        mock_client.variation.return_value = True
        
        with patch.dict(os.environ, {'LAUNCHDARKLY_SDK_KEY': 'test-key'}):
            with patch('ldclient.Config') as mock_config:
                with patch('ldclient.set_config'):
                    with patch('ldclient.get', return_value=mock_client):
                        service = LaunchDarklyService()
                        assert service.client is not None
                        
                        result = service.should_show_chart_wheel("test-user")
                        assert result is True
                        mock_client.variation.assert_called_once()
                        mock_config.assert_called_once_with('test-key')
    
    def test_service_with_sdk_key_initialization_failure(self):
        """Test service with SDK key but initialization failure"""
        mock_client = MagicMock()
        mock_client.is_initialized.return_value = False
        
        with patch.dict(os.environ, {'LAUNCHDARKLY_SDK_KEY': 'test-key'}):
            with patch('ldclient.Config'):
                with patch('ldclient.set_config'):
                    with patch('ldclient.get', return_value=mock_client):
                        service = LaunchDarklyService()
                        assert service.client is None
                        
                        result = service.should_show_chart_wheel("test-user")
                        assert result is False
    
    def test_flag_evaluation_error_handling(self):
        """Test error handling during flag evaluation"""
        mock_client = MagicMock()
        mock_client.is_initialized.return_value = True
        mock_client.variation.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {'LAUNCHDARKLY_SDK_KEY': 'test-key'}):
            with patch('ldclient.Config'):
                with patch('ldclient.set_config'):
                    with patch('ldclient.get', return_value=mock_client):
                        service = LaunchDarklyService()
                        
                        result = service.should_show_chart_wheel("test-user")
                        assert result is False  # Should return default value on error
    
    def test_convenience_function(self):
        """Test the convenience function"""
        with patch('launchdarkly_service.get_launchdarkly_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.should_show_chart_wheel.return_value = True
            mock_get_service.return_value = mock_service
            
            result = should_show_chart_wheel("test-user")
            assert result is True
            mock_service.should_show_chart_wheel.assert_called_once_with("test-user")
    
    def test_singleton_behavior(self):
        """Test that get_launchdarkly_service returns the same instance"""
        # Clear any existing instance
        import launchdarkly_service
        launchdarkly_service._launchdarkly_service = None
        
        service1 = get_launchdarkly_service()
        service2 = get_launchdarkly_service()
        
        assert service1 is service2
    
    def test_close_method(self):
        """Test the close method"""
        mock_client = MagicMock()
        service = LaunchDarklyService()
        service.client = mock_client
        
        service.close()
        mock_client.close.assert_called_once()
    
    def test_close_method_without_client(self):
        """Test close method when client is None"""
        service = LaunchDarklyService()
        service.client = None
        
        # Should not raise an exception
        service.close()