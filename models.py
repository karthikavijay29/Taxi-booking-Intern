from typing import Any, List, Optional

from pydantic import BaseModel, Field


class EmptyResponse(BaseModel):
    pass


class Location(BaseModel):
    x: int
    y: int

    def __equals__(self, other: Any) -> bool:
        return self.x == other.x and self.y == other.y


class Car(BaseModel):
    car_id: int
    name:str
    location: Location = Location(x=0, y=0)
    is_booked: bool = False
    path_location_index: int = -1


class CarResponse(BaseModel):
    car_id: int
    name:str
    location: Location


class CarsResponse(BaseModel):
    cars: List[Car]


class BookBase(BaseModel):
    source: Location
    destination: Location


class Book(BookBase):
    car_id: int
    path: List[Location] = []
    total_time: int = 0


class BookRequest(BookBase):
    source: Location = Field(description="Source location")
    destination: Location = Field(description="Destination location")


class BookResponse(BaseModel):
    car_id: int
    total_time: int


class StateBase(BaseModel):
    def calc_total_book_time(
        self, car: Car, pickup: Location, destination: Location
    ) -> int:
        """Calculate the total time to book a car that include the time to get to the pickup location
        and the time to get to the destination location

        Args:
            car (Car): Car to book
            pickup (Location): Pickup location
            destination (Location): Destination location

        Returns:
            int: Total time to book a car
        """

        return self.calc_distance(pickup, car.location) + self.calc_distance(
            pickup, destination
        )

    @staticmethod
    def calc_distance(source: Location, destination: Location) -> int:
        """Calculate the distance between two locations using the Manhattan distance

        Args:
            source (Location): Source location
            destination (Location): Destination location

        Returns:
            int: Distance between two locations
        """
        return abs(source.x - destination.x) + abs(source.y - destination.y)

    @staticmethod
    def calc_car_path(
        car_location: Location, pickup: Location, destination: Location
    ) -> List[Location]:
        """Calculate the path for a car to get to the pickup location and then to the destination location

        Args:
            car_location (Location): Car location
            pickup (Location): Pickup location
            destination (Location): Destination location

        Returns:
            List[Location]: Path for a car to get to the pickup location and then to the destination location
        """
        path = StateBase.calc_path(car_location, pickup)

        path_from_pickup_to_destination = StateBase.calc_path(pickup, destination)
        if len(path_from_pickup_to_destination) > 0:
            path_from_pickup_to_destination.pop(0)

        path.extend(path_from_pickup_to_destination)

        return path

    @staticmethod
    def calc_path(start: Location, end: Location) -> List[Location]:
        """Calculate the path to get to the destination location

        Args:
            start (Location): Start location
            end (Location): End location

        Returns:
            List[Location]: List of Location points to get to the end location
        """
        path = []

        dx = abs(end.x - start.x)
        dy = abs(end.y - start.y)

        for i in range(dy + 1):
            if start.y < end.y:
                path.append(Location(x=start.x, y=start.y + i))
            else:
                path.append(Location(x=start.x, y=start.y - i))

        for i in range(1, dx + 1):
            if start.x < end.x:
                path.append(Location(x=start.x + i, y=end.y))
            else:
                path.append(Location(x=start.x - i, y=end.y))

        return path


class State(StateBase):
    cars: List[Car] = []
    bookings: List[Book] = []
    current_time: int = 0

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    def get_car(self, car_id: int) -> Optional[Car]:
        found = None
        for car in self.cars:
            if car.car_id == car_id:
                found = car
                break

        return found

    def get_booking(self, car_id: int) -> Book:
        return next(b for b in self.bookings if b.car_id == car_id)

    def reset(self) -> None:
        self.cars = [
            Car(car_id=1, name="Toyota Prius"),
            Car(car_id=2, name="Honda Civic"),
            Car(car_id=3, name="Ford Mustang"),
            ]
        self.bookings = []
        self.current_time = 0

    def increment_time(self) -> None:
        self.current_time += 1

        for index, book in enumerate(self.bookings):
            car = self.get_car(book.car_id)

            # Move car to next location
            if car:
                car.path_location_index += 1
                car.location = book.path[car.path_location_index]

                # Check if car arrived to destination
                if car.path_location_index == len(book.path) - 1:
                    car.is_booked = False
                    car.path_location_index = -1
                    self.bookings.pop(index)

    def book_car(self, pickup: Location, destination: Location) -> Optional[Book]:
        """Book car method to create new booking if there is available car

        Args:
            pickup (Location): Pick up location
            destination (Location): Destination location

        Returns:
            Optional[Book]: Created book object or None
        """
        nearest_car = self.find_nearest_available_car(pickup=pickup)
        if not nearest_car:
            return None

        nearest_car.is_booked = True
        nearest_car.path_location_index = 0

        book = Book(
            car_id=nearest_car.car_id,
            source=pickup,
            destination=destination,
            total_time=self.calc_total_book_time(nearest_car, pickup, destination),
            path=self.calc_car_path(nearest_car.location, pickup, destination),
        )
        self.bookings.append(book)

        return book

    def find_nearest_available_car(self, pickup: Location) -> Optional[Car]:
        """Find nearest available car to the pickup location.
        If no car is available, return None.
        If multiple cars are available, return the one with the smallest id.

        Args:
            pickup (Location): Pick up location

        Returns:
            Optional[Car]: Nearest available car
        """
        nearest_car = None
        nearest_distance = float("inf")
        for car in self.cars:
            if not car.is_booked:
                distance = self.calc_distance(pickup, car.location)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_car = car

                if distance == nearest_distance:
                    nearest_distance = distance

                    if car.car_id < nearest_car.car_id:
                        nearest_car = car

        return nearest_car


class ResetResponse(BaseModel):
    current_time: int
    bookings: List[Book] = []


class TickResponse(BaseModel):
    current_time: int