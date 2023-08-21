from datetime import datetime
from typing import Annotated
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends
from fastapi_pagination import Page, add_pagination, paginate
from starlette import status
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth_handler import Auth
from models.user_models import User
from models.receipt_models import Receipt, Payment, Product, ReceiptProduct, PaymentTypes
from schemas.user_schemas import UserSchema, UserLoginSchema, UserPydantic, TokenSchema
from schemas.receipt_schemas import ReceiptInputSchema, ReceiptSchema
import json

# FastApi app object
app = FastAPI()


@app.post("/receipt", tags=["Receipts"])
async def create_receipt(
        current_user: Annotated[UserPydantic, Depends(Auth.get_current_user)], receipt_body: ReceiptInputSchema
) -> ReceiptSchema:  # TODO: replace ReceiptSchema with ReceiptPydantic
    """
    POST endpoint for creating Receipt by authorized users

    :param current_user: User object returned by Auth.get_current_user.
    :param receipt_body: ReceiptInputSchema with receipt data.
    """
    payment = await Payment.create(**receipt_body.payment.dict())
    receipt = await Receipt.create(payment=payment, total=0, rest=0, user=current_user)
    receipt_total = 0
    for input_product in receipt_body.products:
        product = await Product.get_or_create(name=input_product.name)
        await ReceiptProduct.create(
            receipt=receipt,
            product=product[0],
            quantity=input_product.quantity,
            price=input_product.price,
        )
        receipt_total += input_product.quantity * input_product.price
    receipt.total = receipt_total
    receipt.rest = receipt_body.payment.amount - receipt_total

    await receipt.save()

    # TODO: fix order of Tortoise-ORM schema generation to move ReceiptPydantic in receipt_schemas.py
    await Tortoise.generate_schemas()
    ReceiptPydantic = pydantic_model_creator(
        Receipt,
        name='Receipt',
    )

    return await ReceiptPydantic.from_tortoise_orm(receipt)


@app.get("/receipts", tags=["Receipts"],
         response_model=Page[ReceiptSchema])  # TODO: replace ReceiptSchema with ReceiptPydantic
async def create_receipt(
        current_user: Annotated[UserPydantic, Depends(Auth.get_current_user)],
        total_gt: int = None,
        total_lt: int = None,
        from_date: datetime = None,
        to_date: datetime = None,
        payment_type: PaymentTypes = None,
):
    """
    GET endpoint for filtering receipts created by authorized user

    :param current_user: User object returned by Auth.get_current_user.
    :param total_gt: int filters receipts where total is greater than given value.
    :param total_lt: int filters receipts where total is lesser than given value.
    :param from_date: datetime filters receipts starting from given value.
    :param to_date: datetime filters receipts until given value.
    :param payment_type: PaymentTypes filters receipts by payment type.
    """
    receipts = Receipt.filter(user=current_user)
    if total_gt is not None:
        receipts = Receipt.filter(total__gt=total_gt)
    if total_lt is not None:
        receipts = Receipt.filter(total__lt=total_lt)
    if to_date is not None:
        receipts = Receipt.filter(date__lte=to_date)
    if from_date is not None:
        receipts = Receipt.filter(date__gte=from_date)
    if payment_type is not None:
        receipts = Receipt.filter(payment__type=payment_type)

    # TODO: fix order of Tortoise-ORM schema generation to move ReceiptPydantic in receipt_schemas.py
    await Tortoise.generate_schemas()
    ReceiptPydantic = pydantic_model_creator(
        Receipt,
        name='Receipt',
    )
    receipts_list = await ReceiptPydantic.from_queryset(receipts)
    return paginate(receipts_list)


@app.get("/receipt/{receipt_id}", tags=["Receipts"])  # TODO: replace ReceiptSchema with ReceiptPydantic
async def get_receipt_in_text_format(
        receipt_id: UUID
):
    """
    GET endpoint for retrieving receipt in text format by unauthorized users by receipt id.

    :param receipt_id:  receipt UUID.
    """
    receipt = await Receipt.get_or_none(id=receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong receipt id",
        )
    await receipt.fetch_related('user', 'receiptproducts', 'payment')

    receipt_str = '{:^32}\n'.format(receipt.user.fullname)
    receipt_str += '='*32 + '\n'
    for receipt_product in receipt.receiptproducts.related_objects:
        await receipt_product.fetch_related('product')
        receipt_str += '{:32}'.format(f'{receipt_product.price}x{receipt_product.quantity}') + '\n'
        receipt_str += '{:16}{:>16}'.format(receipt_product.product.name, receipt_product.total()) + '\n'
        receipt_str += "=" * 32 + '\n'
    receipt_str += '{:16} {:<16}'.format('Sum', receipt.total) + '\n'
    receipt_str += '{:16} {:<16}'.format(receipt.payment.type, receipt.payment.amount) + '\n'
    receipt_str += '{:16} {:<16}'.format('Rest', receipt.rest) + '\n'
    receipt_str += "=" * 32 + '\n'
    receipt_str += '{:^32}'.format(receipt.date.strftime('%m/%d/%Y %H-%M-%S')) + '\n'
    receipt_str += '{:^32}'.format('Thank you for your purchase!') + '\n'
    return {'receipt_in_text_format': receipt_str}


@app.post("/user/signup", tags=["user"])
async def create_user(user_data: UserSchema = Depends()):
    """
    POST endpoint for creating new user and receive user JWT access_token.

    :param user_data:  UserSchema that contains user fullname, email and password.
    """
    if await User.get_or_none(email=user_data.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    user = await User.create(
        fullname=user_data.fullname,
        email=user_data.email,
        password=Auth.get_password_hash(
            user_data.password.get_secret_value()
        )
    )
    await user.save()
    user_json = await UserPydantic.from_tortoise_orm(user)
    return {'access_token': Auth.get_token(data=json.loads(user_json.json()), expires_delta=600),
            "token_type": "bearer"}


@app.post("/user/login", tags=["user"])
async def user_login(user_data: UserLoginSchema = Depends()):
    """
    POST endpoint for user login and receiving user JWT access_token.

    :param user_data:  UserLoginSchema that contains user email and password.
    """
    # TODO: remove code duplicate
    user = await User.get_or_none(email=user_data.email)
    if user and Auth.verify_password(user_data.password, user.password):
        user_json = await UserPydantic.from_tortoise_orm(user)
        return {'access_token': Auth.get_token(data=json.loads(user_json.json()), expires_delta=600),
                "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Wrong login details",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.post("/token", response_model=TokenSchema, tags=["user"])
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    POST endpoint for user login using Swagger (OAuth2PasswordRequestForm).

    :param form_data:  OAuth2PasswordRequestForm that contains user username(email) and password.
    """
    # TODO: remove code duplicate
    user = await User.get_or_none(email=form_data.username)
    if user and Auth.verify_password(form_data.password, user.password):
        user_json = await UserPydantic.from_tortoise_orm(user)
        return {'access_token': Auth.get_token(data=json.loads(user_json.json()), expires_delta=600),
                "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Wrong login details",
        headers={"WWW-Authenticate": "Bearer"},
    )

register_tortoise(
    app,
    db_url="postgres://root:postgres@localhost:5432/postgres",  # TODO: move to .env file
    modules={"models": ["models.user_models", "models.receipt_models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

add_pagination(app)
