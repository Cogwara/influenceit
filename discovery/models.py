from django.db import models

# Discovery App - Handle influencer search and matching
class InfluencerList(models.Model):
    creator = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    influencers = models.ManyToManyField('users.CustomUser', related_name='lists')
    notes = models.JSONField()

class SearchFilter(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    criteria = models.JSONField()
