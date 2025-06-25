from typing import List, Optional, Dict
from pydantic import BaseModel

class EmailOrderRequest(BaseModel):
    email_text: str

class OrderProduct(BaseModel):
    product_id: str
    product_name: str
    quantity: int

class ExtractedOrderInfo(BaseModel):
    customer_id: Optional[str] = None
    customer_email: Optional[str] = None
    products: List[OrderProduct]

class ValidationErrorItem(BaseModel):
    product_id: str
    error: str

class ValidationResult(BaseModel):
    customer_info: Dict
    successful_items: List[OrderProduct]
    error_items: List[ValidationErrorItem]
    suggestions: Optional[List[str]] = None
    overall_status: str
    total_items: int
    successful_count: int
    error_count: int

class CustomerMessage(BaseModel):
    subject: str
    body: str
    status: str

class OrderUpdateResult(BaseModel):
    success: bool
    order_id: Optional[str] = None
    details: Optional[str] = None 