
# import httpx
# class EMTClient:
#     def __init__(self, token_provider):
#         self.token_provider = token_provider

#     async def post(self, url: str, payload: dict, headers: dict | None = None):
#         tokens = await self.token_provider.get_tokens()
#         payload.update(tokens)

#         async with httpx.AsyncClient(timeout=60) as client:
#             res = await client.post(url, json=payload, headers=headers)
#             res.raise_for_status()
#             return res.json()


import httpx


class EMTClient:
    def __init__(self, token_provider=None):
        self.token_provider = token_provider

    async def post(self, url: str, payload: dict) -> dict:
        if self.token_provider:
            tokens = await self.token_provider()
            payload.update(tokens)

        async with httpx.AsyncClient(timeout=60) as client:
            res = await client.post(url, json=payload)
            res.raise_for_status()
            
            # Handle empty responses (204 No Content)
            if res.status_code == 204 or not res.text:
                return {}
            
            return res.json()

