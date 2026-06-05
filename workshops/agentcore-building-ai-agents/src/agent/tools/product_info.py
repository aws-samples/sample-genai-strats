from strands.tools import tool
from logger import get_logger

l = get_logger("product_info")

@tool
def get_product_info(product_type: str) -> str:
    """
    Get detailed technical specifications and information for electronics products.

    Args:
        product_type: Electronics product type (e.g., 'laptops', 'smartphones', 'headphones', 'monitors')
    Returns:
        Formatted product information including warranty, features, and policies
    """
    # Mock product catalog - in real implementation, this would query a product database
    products = {
        "laptops": {
            "warranty": "1-year manufacturer warranty + optional extended coverage",
            "specs": "Intel/AMD processors, 8-32GB RAM, SSD storage, various display sizes",
            "features": "Backlit keyboards, USB-C/Thunderbolt, Wi-Fi 6, Bluetooth 5.0",
            "compatibility": "Windows 11, macOS, Linux support varies by model",
            "support": "Technical support and driver updates included",
        },
        "smartphones": {
            "warranty": "1-year manufacturer warranty",
            "specs": "5G/4G connectivity, 128GB-1TB storage, multiple camera systems",
            "features": "Wireless charging, water resistance, biometric security",
            "compatibility": "iOS/Android, carrier unlocked options available",
            "support": "Software updates and technical support included",
        },
        "headphones": {
            "warranty": "1-year manufacturer warranty",
            "specs": "Wired/wireless options, noise cancellation, 20Hz-20kHz frequency",
            "features": "Active noise cancellation, touch controls, voice assistant",
            "compatibility": "Bluetooth 5.0+, 3.5mm jack, USB-C charging",
            "support": "Firmware updates via companion app",
        },
        "monitors": {
            "warranty": "3-year manufacturer warranty",
            "specs": "4K/1440p/1080p resolutions, IPS/OLED panels, various sizes",
            "features": "HDR support, high refresh rates, adjustable stands",
            "compatibility": "HDMI, DisplayPort, USB-C inputs",
            "support": "Color calibration and technical support",
        },
    }
    product = products.get(product_type.lower())
    if not product:
        return f"Technical specifications for {product_type} not available. Please contact our technical support team for detailed product information and compatibility requirements."

    return (
        f"Technical Information - {product_type.title()}:\n\n"
        f"• Warranty: {product['warranty']}\n"
        f"• Specifications: {product['specs']}\n"
        f"• Key Features: {product['features']}\n"
        f"• Compatibility: {product['compatibility']}\n"
        f"• Support: {product['support']}"
    )


l.info("✅ get_product_info tool ready")