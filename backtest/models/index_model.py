from django.db import models


class Index(models.Model):
    time = models.DateTimeField(primary_key=True)
    symbol = models.CharField(max_length=50, primary_key=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()
    exchange = models.CharField(max_length=50)

    class Meta:
        db_table = 'index'
        app_label = 'price_feed_app'
        managed = False