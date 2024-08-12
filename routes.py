from fastapi import APIRouter, Query, Request, Response, status

from models import (
    BookRequest,
    BookResponse,
    CarResponse,
    CarsResponse,
    ResetResponse,
    TickResponse,
)

router = APIRouter()


@router.get("/cars", response_model=CarsResponse)
async def list_cars(
    request: Request,
    is_booked: bool = Query(
        False, description="Filter parameter to show only booked or free cars"
    ),
):
    """Method to list cars in the system"""
    cars = []
    for car in request.app.state.cars:
        if car.is_booked == is_booked:
            cars.append(car)
    return {"cars": cars}


@router.get(
    "/cars/{car_id}", response_model=CarResponse, responses={204: {"model": ""}}
)
async def get_car(car_id: int, request: Request):
    """Method to retrieve a car by id"""
    car = request.app.state.get_car(car_id)
    if not car:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return car


@router.post(
    "/book",
    status_code=status.HTTP_201_CREATED,
    response_model=BookResponse,
    responses={204: {"model": "", "description": "No avaialable cars for booking"}},
)
async def create_book(book_request: BookRequest, request: Request):
    """Method to create new booking"""
    book = request.app.state.book_car(
        pickup=book_request.source, destination=book_request.destination
    )
    if not book:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return book


@router.post("/tick", response_model=TickResponse)
async def tick(request: Request):
    """Method to increment system time"""
    request.app.state.increment_time()

    return request.app.state


@router.put("/reset", response_model=ResetResponse)
async def reset(request: Request):
    """Method to reset system's state"""
    request.app.state.reset()

    return request.app.state