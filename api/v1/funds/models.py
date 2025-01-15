from pydantic import BaseModel

# Define the request model
class FundFamilyRequest(BaseModel):
    fund_family: str

class BuyRequest(BaseModel):
    Scheme_Code: int
    units: int
    nav: float