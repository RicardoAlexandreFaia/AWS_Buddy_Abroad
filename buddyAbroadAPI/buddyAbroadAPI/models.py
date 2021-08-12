# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BuddyInfo(models.Model):
    name = models.CharField(max_length=100)
    earnings = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buddy_info'


class BuddyMatchTourist(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    ordered_trip = models.ForeignKey('Trips', models.DO_NOTHING, blank=True, null=True)
    participants = models.CharField(max_length=100, blank=True, null=True)
    buddy = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buddy_match_tourist'
        unique_together = (('ordered_trip', 'buddy'),)


class Messages(models.Model):
    message = models.CharField(max_length=400, blank=True, null=True)
    sender = models.ForeignKey('Users', models.DO_NOTHING, db_column='sender', blank=True, null=True,related_name='sender')
    recipient = models.ForeignKey('Users', models.DO_NOTHING, db_column='recipient', blank=True, null=True,related_name='recipient')
    date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'messages'
        unique_together = (('sender', 'recipient'),)


class Preferences(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'preferences'


class PreferencesUser(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'preferences_user'


class Roles(models.Model):
    description = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'roles'


class Trips(models.Model):
    id = models.OneToOneField('TripsImages', models.DO_NOTHING, db_column='id', primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    principal_image = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    details = models.CharField(max_length=100, blank=True, null=True)
    turist_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'trips'


class TripsImages(models.Model):
    image = models.CharField(max_length=100)
    trips_id = models.IntegerField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trips_images'


class TuristInfo(models.Model):
    id = models.OneToOneField('Users', models.DO_NOTHING, db_column='id',primary_key=True)
    age = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'turist_info'


class Users(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=100)
    age = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'users'
