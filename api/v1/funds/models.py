from pydantic import BaseModel

# Define the request model
class FundFamilyRequest(BaseModel):
    fund_family: str

class BuyRequest(BaseModel):
    Scheme_Code: int
    Scheme_Name: str
    Date: str
    Scheme_Category: str
    Mutual_Fund_Family: str
    units: int
    nav: float
    ISIN_Div_Payout_ISIN_Growth: str
    ISIN_Div_Reinvestment: str