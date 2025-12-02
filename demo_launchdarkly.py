#!/usr/bin/env python3
"""
Demonstration script for LaunchDarkly integration with the astro app.

This script shows how to:
1. Set up LaunchDarkly environment variables
2. Test the feature flag functionality
3. See how the chart wheel is controlled by the flag

Usage:
    # Set your LaunchDarkly SDK key
    export LAUNCHDARKLY_SDK_KEY="sdk-your-key-here"
    
    # Run the demonstration
    python demo_launchdarkly.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from launchdarkly_service import LaunchDarklyService, should_show_chart_wheel


def demonstrate_launchdarkly():
    """Demonstrate LaunchDarkly functionality"""
    print("🚀 LaunchDarkly Integration Demo for Astro App")
    print("=" * 50)
    
    # Check if SDK key is set
    sdk_key = os.environ.get('LAUNCHDARKLY_SDK_KEY')
    if sdk_key:
        print(f"✅ LaunchDarkly SDK Key is set: {sdk_key[:10]}...")
    else:
        print("⚠️  LaunchDarkly SDK Key not set. Using fallback values.")
        print("   Set LAUNCHDARKLY_SDK_KEY environment variable for live flags.")
    
    print()
    
    # Test the service directly
    print("🔧 Testing LaunchDarkly Service:")
    service = LaunchDarklyService()
    
    if service.client:
        print("✅ LaunchDarkly client initialized successfully")
    else:
        print("⚠️  LaunchDarkly client not initialized (using defaults)")
    
    print()
    
    # Test flag evaluation for different IP addresses
    print("🎛️  Testing 'show-new-chart' feature flag:")
    test_ips = ['192.168.1.100', '10.0.0.50', '203.0.113.195', '127.0.0.1']
    
    for ip in test_ips:
        show_chart = should_show_chart_wheel(ip)
        status = "✅ ENABLED" if show_chart else "❌ DISABLED" 
        print(f"   IP '{ip}': Chart wheel is {status}")
    
    print()
    
    # Demonstrate how the flag affects the application
    print("🎨 How this affects the full chart page:")
    print("   When flag is TRUE:")
    print("   - Chart wheel visualization is displayed")
    print("   - Chart wheel JavaScript is loaded")
    print("   - Interactive planetary chart is available")
    print()
    print("   When flag is FALSE:")
    print("   - Chart wheel is hidden")
    print("   - No chart wheel JavaScript loaded")
    print("   - Only text-based chart data is shown")
    
    print()
    
    # Configuration tips
    print("⚙️  Configuration Tips:")
    print("   1. Set up your LaunchDarkly flag named 'show-new-chart'")
    print("   2. Configure targeting rules based on IP addresses or regions")
    print("   3. Use percentage rollouts to gradually enable the feature")
    print("   4. Set fallback value to 'false' for safety")
    print()
    print("   Environment Variables:")
    print("   - LAUNCHDARKLY_SDK_KEY: Your LaunchDarkly SDK key")
    print()
    print("   IP-based Targeting Examples:")
    print("   - Target specific IP ranges (corporate networks)")
    print("   - Geographic targeting by IP location")
    print("   - A/B test based on IP hash distribution")
    
    # Cleanup
    service.close()
    print()
    print("🎉 Demo completed!")


if __name__ == "__main__":
    demonstrate_launchdarkly()