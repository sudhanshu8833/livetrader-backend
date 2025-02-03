from backtest.models import Index, Options
from rest_framework import serializers

class IndexCandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Index
        fields = '__all__'

class OptionsCandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = '__all__'