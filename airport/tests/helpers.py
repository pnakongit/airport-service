from airport.models import City, Country


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
