from pydantic import BaseModel

# Define the request model
class FundFamilyRequest(BaseModel):
    fund_family: str