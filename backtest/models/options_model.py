from django.db import models


class Options(models.Model):
    time = models.DateTimeField(primary_key=True)
    symbol = models.CharField(max_length=50, primary_key=True)
    expiration_date = models.DateField(primary_key=True)
    strike_price = models.FloatField(primary_key=True)
    option_type = models.CharField(max_length=2, choices=[('CE', 'CE'), ('PE', 'PE')], primary_key=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()
    exchange = models.CharField(max_length=50)

    class Meta:
        db_table = 'options'
        app_label = 'price_feed_app'
        managed = False