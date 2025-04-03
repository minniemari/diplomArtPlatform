import django_filters
from .models import Commission, Birzha

class CommissionFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    type = django_filters.CharFilter(field_name="type__name", lookup_expr="iexact")
    max_deadline = django_filters.NumberFilter(field_name="options__deadline", lookup_expr="lte")

    class Meta:
        model = Commission
        fields = ["min_price", "max_price", "type", "max_deadline"]

class BirzhaFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    type = django_filters.CharFilter(field_name="type__name", lookup_expr="iexact")

    class Meta:
        model = Birzha
        fields = ["min_price", "max_price", "type"]



