from typing import Dict, Any,List

from .hotel_schema import (
    WhatsappHotelFormat,
    WhatsappHotelFinalResponse,
)
from .hotel_schema import HotelSearchInput
from emt_client.clients.hotel_client import HotelApiClient
from emt_client.config import HOTEL_SEARCH_URL
from emt_client.utils import resolve_city_name, generate_hotel_search_key, generate_short_link
from .hotel_schema import HotelSearchInput
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


class HotelSearchService:
    """Service layer for hotel search operations"""
    def _generate_view_all(self, deeplink: str) -> str:
        """
        Convert a hotel details deeplink into a 'view all hotels' search link.
        """
        if not deeplink:
            return ""

        parsed = urlparse(deeplink)

        # Replace details → search
        new_path = parsed.path.replace("details", "search")

        query_params = parse_qs(parsed.query)

        allowed_keys = {
            "cityName",
            "sText",
            "checkinDate",
            "checkoutDate",
            "Rooms",
            "pax",
        }

        filtered_params = {
            key: value[0]
            for key, value in query_params.items()
            if key in allowed_keys
        }

        new_query = urlencode(filtered_params)

        raw_link = urlunparse(
            parsed._replace(path=new_path, query=new_query)
        )

        try:
            short_link = generate_short_link(
                [{"deepLink": raw_link}],
                product_type="hotel",
            )[0].get("deepLink")
            return short_link or raw_link
        except Exception:
            return raw_link
    

    def __init__(self):
        self.client = HotelApiClient()  # ✅ Use HotelApiClient
    
    async def search(self, search_input: HotelSearchInput) -> Dict[str, Any]:
        """Execute hotel search workflow"""
        
        try:
            # Step 1: Resolve city names
            resolved_city = await resolve_city_name(search_input.city_name)
            
            # Step 2: Generate search key
            search_key = generate_hotel_search_key(
                city_code=resolved_city,
                check_in=search_input.check_in_date,
                check_out=search_input.check_out_date,
                num_rooms=search_input.num_rooms,
                num_adults=search_input.num_adults,
                num_children=search_input.num_children,
            )
            
            # Step 3: Build request payload (tokens auto-injected by client)
            payload = {
                "CheckInDate": search_input.check_in_date,
                "CheckOut": search_input.check_out_date,
                "CityCode": resolved_city,
                "CityName": resolved_city,
                "HotelCount": search_input.hotel_count,
                "PageNo": search_input.page_no,
                "NoOfRooms": search_input.num_rooms,
                "RoomDetails": [
                    {
                        "NoOfRooms": search_input.num_rooms,
                        "NoOfAdult": search_input.num_adults,
                        "NoOfChild": search_input.num_children,
                        "childAge": "",
                    }
                ],
                "SearchKey": search_key,
                "hotelid": [],
                "maxPrice": search_input.max_price,
                "minPrice": search_input.min_price or 1,
                "sorttype": search_input.sort_type,
                "wlcode": "",
                "selectedAmen": search_input.amenities or [],
                "selectedRating": search_input.rating or [],
                "selectedTARating": search_input.user_rating or [],
            }

            print(f"DEBUG: Hotel API payload HotelCount: {payload.get('HotelCount')}")

            #print(payload)
            # Step 4: Call API (tokens injected automatically)
            response = await self.client.search(HOTEL_SEARCH_URL, payload)
            
            # Step 5: Validate response
            if response is None:
                return {
                    "error": "API_ERROR",
                    "message": "Hotel API returned no response",
                    "searchKey": search_key,
                    "city": resolved_city,
                    "city_name": resolved_city,
                    "check_in": search_input.check_in_date,
                    "check_in_date": search_input.check_in_date,
                    "checkIn": search_input.check_in_date,
                    "check_out": search_input.check_out_date,
                    "check_out_date": search_input.check_out_date,
                    "checkOut": search_input.check_out_date,
                    "num_rooms": search_input.num_rooms,
                    "num_adults": search_input.num_adults,
                    "num_children": search_input.num_children,
                    "totalResults": 0,
                    "total_results": 0,
                    "results": [],
                    "hotels": [],
                }
            
            
            # Step 6: Process response
            return self._process_response(response, resolved_city, search_input, search_key)
            
        except Exception as e:
            # Return error with details
            import traceback
            return {
                "error": "SEARCH_ERROR",
                "message": f"{str(e)} - {traceback.format_exc()}",
                "searchKey": "",
                "city": search_input.city_name,
                "city_name": search_input.city_name,
                "check_in": search_input.check_in_date,
                "check_in_date": search_input.check_in_date,
                "checkIn": search_input.check_in_date,
                "check_out": search_input.check_out_date,
                "check_out_date": search_input.check_out_date,
                "checkOut": search_input.check_out_date,
                "num_rooms": search_input.num_rooms,
                "num_adults": search_input.num_adults,
                "num_children": search_input.num_children,
                "totalResults": 0,
                "total_results": 0,
                "results": [],
                "hotels": [],
            }
    
    def _process_response(
    self,
    response: Dict[str, Any],
    resolved_city: str,
    search_input: HotelSearchInput,
    search_key: str
    ) -> Dict[str, Any]:

        print(f"DEBUG: API response keys: {response.keys()}")
        print(f"DEBUG: API response (excluding htllist): { {k: v for k, v in response.items() if k != 'htllist'} }")

        hotels = response.get("htllist", []) or []
        resolved_key = response.get("key") or response.get("SearchKey") or search_key

        results = []
        view_all_link = ""

        for index, hotel in enumerate(hotels):
            deep_link_data = self._build_deep_link(
                city_name=resolved_city,
                check_in=search_input.check_in_date,
                check_out=search_input.check_out_date,
                num_rooms=search_input.num_rooms,
                num_adults=search_input.num_adults,
                num_children=search_input.num_children,
                emt_id=hotel.get("ecid", ""),
                hotel_id=hotel.get("hid", ""),
            )

            if index == 0:
                view_all_link = self._generate_view_all(deep_link_data["deepLink"])

            # Calculate adjusted price (base_price - discount)
            base_price = hotel.get("prc")
            discount = hotel.get("disc") or 0


            try:
                numeric_price = float(base_price) if base_price is not None else None
                numeric_discount = float(discount)
                if numeric_price is not None:
                    adjusted_price = max(0, numeric_price - numeric_discount)
                else:
                    adjusted_price = base_price
            except (TypeError, ValueError):
                adjusted_price = base_price

            results.append({
                "hotelId": hotel.get("hid"),
                "emtId": hotel.get("ecid"),
                "name": hotel.get("nm"),
                "rating": hotel.get("rat"),
                "price": {
                    "amount": adjusted_price,
                    "currency": hotel.get("curr", "INR")
                },
                "discount": hotel.get("disc"),
                "location": hotel.get("loc") or hotel.get("adrs"),
                "highlights": hotel.get("highlt"),
                "hotelImage": hotel.get("imgU"),
                "deepLink": deep_link_data["deepLink"],
                "traceId": deep_link_data["traceId"],
            })

        return {
            "searchKey": resolved_key,
            "city": resolved_city,
            "city_name": resolved_city,
            "check_in": search_input.check_in_date,
            "check_out": search_input.check_out_date,
            "num_rooms": search_input.num_rooms,
            "num_adults": search_input.num_adults,
            "num_children": search_input.num_children,
            "totalResults": len(hotels),
            "hotels": results,
            "viewAll": view_all_link,  
        }
                
    
    def _build_deep_link(self, **kwargs) -> Dict[str, str]:
        """Create the EMT hotel deep-link and trace id."""
        from emt_client.utils import gen_trace_id
        from emt_client.config import HOTEL_DEEPLINK
        from urllib.parse import quote
        from datetime import datetime
        
        city_name = kwargs.get("city_name", "")
        check_in = kwargs.get("check_in", "")
        check_out = kwargs.get("check_out", "")
        num_rooms = kwargs.get("num_rooms", 1)
        num_adults = kwargs.get("num_adults", 2)
        num_children = kwargs.get("num_children", 0)
        emt_id = kwargs.get("emt_id", "")
        hotel_id = kwargs.get("hotel_id", "")
        trace_id = kwargs.get("trace_id")
        
        link_trace_id = trace_id or gen_trace_id()
        total_pax = max(1, num_adults + num_children)
        encoded_city = quote(city_name, safe="")
        check_in_fmt = datetime.strptime(check_in, "%Y-%m-%d").strftime("%d/%m/%Y")
        check_out_fmt = datetime.strptime(check_out, "%Y-%m-%d").strftime("%d/%m/%Y")

        deep_link = (
            f"{HOTEL_DEEPLINK}"
            f"cityName={encoded_city}&"
            f"sText={encoded_city}&"
            f"checkinDate={check_in_fmt}&"
            f"checkoutDate={check_out_fmt}&"
            f"Rooms={num_rooms}&"
            f"pax={total_pax}&"
            f"emthid={emt_id}&"
            f"hid={hotel_id}&"
            f"tid={link_trace_id}"
        )

        return {"deepLink": deep_link, "traceId": link_trace_id}
    

    def build_whatsapp_hotel_response(
            self,
    results: Dict[str, Any],
    search_input: HotelSearchInput,
    ) -> WhatsappHotelFinalResponse:
        """
        Build WhatsApp-specific hotel response.

        IMPORTANT:
        - Assumes hotels are ALREADY limited by parent
        - No slicing / UI limits enforced here
        """
        hotels = results.get("hotels", [])
        whatsapp_hotels = []

        for idx, hotel in enumerate(hotels, start=1):
            whatsapp_hotels.append({
                "option_id": idx,
                "hotel_name": hotel.get("name"),
                "location": hotel.get("location"),
                "rating": hotel.get("rating"),
                "price": hotel.get("price", {}).get("amount", ""),
                "price_unit": "per night",
                "image_url": hotel.get("hotelImage"),
                "amenities": hotel.get("highlights") or "Not specified",
                "booking_url": hotel.get("deepLink"),
            })

        whatsapp_json = WhatsappHotelFormat(
            type="hotel_collection",
            options=whatsapp_hotels,
            check_in_date=search_input.check_in_date,
            check_out_date=search_input.check_out_date,
            currency=hotel.get("currency", "INR"),
            view_all_hotels_url=results.get("viewAll", ""),
        )

        return WhatsappHotelFinalResponse(
            response_text=f"Here are the best hotels options in {search_input.city_name}",
            whatsapp_json=whatsapp_json,
        )