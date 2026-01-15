"""
Quick script to test hotel UI with real API data
"""
import asyncio
from tools_factory.hotels.hotel_search_tool import HotelSearchTool


async def main():
    tool = HotelSearchTool()
    
    # Search for hotels in Mumbai
    result = await tool.execute(
        city_name="Mumbai",
        check_in_date="2026-02-15",
        check_out_date="2026-02-17",
        num_rooms=1,
        num_adults=2,
        _limit=10,  # Limit to 10 hotels for quick testing
        _html=True  # Generate HTML
    )
    
    print(f"Status: {result.response_text}")
    print(f"Error: {result.is_error}")
    print(f"Total Hotels Found: {len(result.structured_content.get('hotels', []))}")

    print(f"Total Hotels Found: {result}")

    if result.html:
        # Save HTML to file
        with open("hotel_results.html", "w", encoding="utf-8") as f:
            f.write(result.html)
        print("\n✅ HTML saved to hotel_results.html")
        print("Open it in your browser to see the UI!")
    else:
        print("\n❌ No HTML generated")
        if result.structured_content:
            print(f"Hotels found: {len(result.structured_content.get('hotels', []))}")


if __name__ == "__main__":
    asyncio.run(main())
