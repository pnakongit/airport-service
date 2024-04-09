from django_filters import rest_framework as filters


class FlightFilter(filters.FilterSet):
    start_departure_date = filters.DateTimeFilter(
        field_name="departure_time",
        lookup_expr="date__gte"
    )
    end_departure_date = filters.DateFilter(
        field_name="departure_time",
        lookup_expr="date__lte"
    )
    start_arrival_date = filters.DateFilter(
        field_name="arrival_time",
        lookup_expr="date__gte"
    )
    end_arrival_date = filters.DateFilter(
        field_name="arrival_time",
        lookup_expr="date__lte"
    )
    source = filters.CharFilter(
        field_name="route__source__name"
    )
    destination = filters.CharFilter(
        field_name="route__destination__name"
    )
