from django.db import models

# Create your models here.

# Messaging App - Handle in-platform communication
class Conversation(models.Model):
    participants = models.ManyToManyField('users.CustomUser')
    campaign = models.ForeignKey('campaigns.Campaign', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField('users.CustomUser', related_name='read_messages')
