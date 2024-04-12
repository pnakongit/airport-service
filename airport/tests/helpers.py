from django.urls import reverse

from airport.models import City, Country, Airport


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
    country , _ = Country.objects.get_or_create(
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
