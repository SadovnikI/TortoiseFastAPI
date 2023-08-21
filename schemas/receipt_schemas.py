from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from models.receipt_models import PaymentTypes

# ==========================================================
#                 Receipt Pydentic Schemas


class ProductInputSchema(BaseModel):
    name: str = Field(...)
    price: float = Field(...)
    quantity: float = Field(...)


class PaymentInputSchema(BaseModel):
    type: PaymentTypes = Field(...)
    amount: float = Field(...)


class ReceiptInputSchema(BaseModel):
    products: List[ProductInputSchema] = Field(...)
    payment: PaymentInputSchema = Field(...)


class PaymentSchema(BaseModel):
    id: UUID
    type: PaymentTypes
    amount: float


class ProductSchema(BaseModel):
    id: UUID
    name: str


class ReceiptProductSchema(BaseModel):
    id: UUID
    product: ProductSchema
    price: float
    quantity: float
    total: float


class ReceiptSchema(BaseModel):
    id: UUID
    date: datetime
    payment: PaymentSchema
    total: float
    rest: float
    receiptproducts: List[ReceiptProductSchema]

    class Config:
        schema_extra = {
            "example": {
                "id": "49a83cc9-dc49-4178-9238-9b562b76a3c1",
                "date": "2023-08-21T11:33:53.503123Z",
                "payment": {
                    "id": "43e1a915-3030-44c4-a8b0-a741873b80bc",
                    "type": "Cash",
                    "amount": 200
                },
                "total": 140,
                "rest": 60,
                "receiptproducts": [
                    {
                        "id": "331bd14a-8499-4bb8-add8-930ef23cfcc9",
                        "product": {
                            "id": "471d4772-daed-41be-9a66-35deaf02855e",
                            "name": "p1"
                        },
                        "quantity": 1,
                        "price": 100,
                        "total": 100
                    },
                    {
                        "id": "a97b4a03-7e40-48d1-b942-511a4e26d5b5",
                        "product": {
                            "id": "a51fe153-090a-4b2c-82e5-e452ddb75ec1",
                            "name": "p2"
                        },
                        "quantity": 2,
                        "price": 20,
                        "total": 40
                    }
                ]
            }
        }


# ==========================================================
#           Receipt Pydentic Tortoise ORM Schemas


# TODO: fix order of Tortoise-ORM schema generation

# ReceiptPydantic = pydantic_model_creator(
#         Receipt,
#         name='Receipt',
#     )
