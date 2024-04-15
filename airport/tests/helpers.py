from django.urls import reverse

from faker import Faker

from airport.models import City, Country, Airport, Route, Airplane, AirplaneType


def detail_url(view_name: str, obj_id: id) -> str:
    return reverse(view_name, args=[obj_id])


def sample_city(**params) -> City:
    country, _ = Country.objects.get_or_create(
        name="Test Sample Country Name"
    )
    default_city_params = {
        "name": "Test Sample City Name",
        "country": country,
    }
    default_city_params.update(params)
    return City.objects.create(**default_city_params)


def sample_airport(**params) -> Airport:
    country, _ = Country.objects.get_or_create(
        name="Test Sample Country Name"
    )
    city, _ = City.objects.get_or_create(
        name="Test Sample City Name",
        country=country
    )

    default_airport_params = {
        "name": "Test Airport Name",
        "closest_big_city": city,
    }
    default_airport_params.update(params)
    return Airport.objects.create(**default_airport_params)


def sample_route(**params) -> Route:
    fake = Faker()
    source_airport = sample_airport(name=fake.word())
    destination_airport = sample_airport(name=fake.word())

    default_route_params = {
        "source": source_airport,
        "destination": destination_airport,
        "distance": 30
    }
    default_route_params.update(params)
    return Route.objects.create(**default_route_params)


def sample_airplane(**params) -> Airplane:
    airplane_type, _ = AirplaneType.objects.get_or_create(
        name="Test Airplane Type Name"
    )
    default_airplane_params = {
        "name": "Test Airplane Name",
        "rows": 15,
        "seats_in_row": 15,
        "airplane_type": airplane_type,
    }
    default_airplane_params.update(params)
    return Airplane.objects.create(**default_airplane_params)
