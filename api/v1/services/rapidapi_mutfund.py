# /api/v1/services/rapidapi_mutfund.py

import httpx
from api.v1.config import CONFIG
import urllib.parse

class RapidAPIService:
    @staticmethod
    async def fetch_latest_open_ended_schemes():
        """
        Fetch all the open ended schemes
        """

        url = f"{CONFIG['RAPID_URL']}/latest?Scheme_Type=Open"
        headers = {
            "X-RapidAPI-Key": CONFIG["RAPID_MUT_FUND_KEY"],
            "X-RapidAPI-Host": "latest-mutual-fund-nav.p.rapidapi.com"
        }

        # Dev for UI
        return 0;

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        
    @staticmethod
    async def fetch_latest_ff_open_ended_schemes(fund_family):
        """
        Fetch latest schemes for the selected fund family from the /latest endpoint.
        Fetches all mutual fund schemes without any built-in filtering 
        """
        # Encode the string for use in a URL
        encoded_fund_family = urllib.parse.quote(fund_family)

        url = f"{CONFIG['RAPID_URL']}/latest?Scheme_Type=Open&Mutual_Fund_Family={encoded_fund_family}"
        headers = {
            "X-RapidAPI-Key": CONFIG["RAPID_MUT_FUND_KEY"],
            "X-RapidAPI-Host": "latest-mutual-fund-nav.p.rapidapi.com"
        }

        # Dev for UI
        return {
            "status": "success",
            "data": [
                {
                    "Scheme_Code": 119551,
                    "ISIN_Div_Payout_ISIN_Growth": "INF209KA12Z1",
                    "ISIN_Div_Reinvestment": "INF209KA13Z9",
                    "Scheme_Name": "Aditya Birla Sun Life Banking & PSU Debt Fund  - DIRECT - IDCW",
                    "Net_Asset_Value": 102.5067,
                    "Date": "14-Jan-2025",
                    "Scheme_Type": "Open Ended Schemes",
                    "Scheme_Category": "Debt Scheme - Banking and PSU Fund",
                    "Mutual_Fund_Family": "Aditya Birla Sun Life Mutual Fund"
                },
                {
                    "Scheme_Code": 119552,
                    "ISIN_Div_Payout_ISIN_Growth": "INF209K01YM2",
                    "ISIN_Div_Reinvestment": "-",
                    "Scheme_Name": "Aditya Birla Sun Life Banking & PSU Debt Fund  - DIRECT - MONTHLY IDCW",
                    "Net_Asset_Value": 115.5344,
                    "Date": "14-Jan-2025",
                    "Scheme_Type": "Open Ended Schemes",
                    "Scheme_Category": "Debt Scheme - Banking and PSU Fund",
                    "Mutual_Fund_Family": "Aditya Birla Sun Life Mutual Fund"
                }
                ]
            }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()