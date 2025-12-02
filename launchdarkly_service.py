"""
LaunchDarkly feature flag service
"""
import os
import logging
import ldclient
from ldclient.context import Context

logger = logging.getLogger(__name__)

class LaunchDarklyService:
    def __init__(self):
        """Initialize LaunchDarkly client"""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the LaunchDarkly client with SDK key from environment"""
        sdk_key = os.environ.get('LAUNCHDARKLY_SDK_KEY')
        
        if not sdk_key:
            logger.warning("LAUNCHDARKLY_SDK_KEY environment variable not set. Feature flags will default to fallback values.")
            return
        
        try:
            # Initialize LaunchDarkly client with SDK key
            config = ldclient.Config(sdk_key)
            ldclient.set_config(config)
            self.client = ldclient.get()
            
            if self.client.is_initialized():
                logger.info("LaunchDarkly client initialized successfully")
            else:
                logger.error("LaunchDarkly client failed to initialize")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize LaunchDarkly client: {str(e)}")
            self.client = None
    
    def should_show_chart_wheel(self, user_ip="127.0.0.1"):
        """
        Check the 'show-new-chart' flag to determine if chart wheel should be shown
        
        Args:
            user_ip (str): IP address of the user (defaults to "127.0.0.1")
            
        Returns:
            bool: True if chart wheel should be shown, False otherwise
        """
        flag_key = "show-new-chart"
        default_value = False
        
        if not self.client:
            logger.warning(f"LaunchDarkly client not available, returning default value ({default_value}) for flag '{flag_key}'")
            return default_value
        
        try:
            # Create user context with IP address as key
            context = Context.builder(user_ip).set("ip", user_ip).build()
            
            # Evaluate the flag
            show_chart = self.client.variation(flag_key, context, default_value)
            
            logger.info(f"Feature flag '{flag_key}' evaluated to: {show_chart} for IP: {user_ip}")
            return show_chart
            
        except Exception as e:
            logger.error(f"Error evaluating feature flag '{flag_key}': {str(e)}")
            return default_value
    
    def close(self):
        """Close the LaunchDarkly client"""
        if self.client:
            self.client.close()
            logger.info("LaunchDarkly client closed")

# Global instance
_launchdarkly_service = None

def get_launchdarkly_service():
    """Get the global LaunchDarkly service instance"""
    global _launchdarkly_service
    if _launchdarkly_service is None:
        _launchdarkly_service = LaunchDarklyService()
    return _launchdarkly_service

def should_show_chart_wheel(user_ip="127.0.0.1"):
    """Convenience function to check if chart wheel should be shown"""
    service = get_launchdarkly_service()
    return service.should_show_chart_wheel(user_ip)