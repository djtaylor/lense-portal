from django.db import models
from django.contrib.auth.models import User

# CloudScape Libraries
from cloudscape.common.vars import G_ADMIN
from cloudscape.engine.api.app.group.models import DBGroupMembers, DBGroupDetails

class DBUserDetails(User):
    """
    Main database model for extending the Django user model.
    """

    # Check for administrator group membership
    def is_admin_member(self):
        groups = self.get_groups()
        for group in groups:
            if group['uuid'] == G_ADMIN:
                return True
        return False

    # Get user groups
    def get_groups(self):
        membership = []
        for g in DBGroupMembers.objects.filter(member=self.username).values():
            gd = DBGroupDetails.objects.filter(uuid=g['group_id']).values()[0]
            membership.append({
                'uuid': gd['uuid'],
                'name': gd['name'],
                'desc': gd['desc']
            })
        return membership

    # Proxy metaclass
    class Meta:
        proxy = True

class DBUserAPIKeys(models.Model):
    """
    Main database model for storing user API keys.
    """
    
    # User API key table columns
    user    = models.ForeignKey(User, to_field='username', db_column='user')
    api_key = models.CharField(max_length=64, unique=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'auth_user_api_keys'
        
class DBUserAPITokens(models.Model):
    """
    Main database model for storing user API tokens.
    """
    
    # User API token table columns
    user    = models.ForeignKey(User, to_field='username', db_column='user')
    token   = models.CharField(max_length=255, unique=True)
    expires = models.DateTimeField()
    
    # Custom model metadata
    class Meta:
        db_table = 'auth_user_api_tokens'