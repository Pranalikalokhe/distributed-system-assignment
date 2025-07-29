from django.db import models

# Create your models here.

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'users'

class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.FloatField()

    class Meta:
        managed = False
        db_table = 'products'

class Order(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'orders'
