from django.db import models
from django.utils import timezone
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, UserManager

# CloudScape Libraries
from cloudscape.common.vars import G_ADMIN
from cloudscape.engine.api.app.group.models import DBGroupMembers, DBGroupDetails

class DBUser(AbstractBaseUser):
    """
    Main database model for user accounts.
    """
    uuid       = models.CharField(max_length=36, unique=True)
    username   = models.CharField(_('username'), 
        max_length = 30, 
        unique     = True,
        help_text  = _('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators = [
            validators.RegexValidator(r'^[\w.@+-]+$',
            _('Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.'), 
            'invalid'),
        ],
        error_messages = {
            'unique': _("A user with that username already exists."),
        })
    
    # First / last name / email
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name  = models.CharField(_('last name'), max_length=30, blank=True)
    email      = models.EmailField(_('email address'), blank=True)
    
    # Is the user staff or not
    is_staff   = models.BooleanField(_('staff status'), 
        default   = False,
        help_text = _('Designates whether the user can log into this admin '
                    'site.')
    )
    
    # Is the account active
    is_active = models.BooleanField(_('active'), 
        default   = True,
        help_text = _('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    )
    
    # Date joined
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    # Is the user authenticated from LDAP
    from_ldap = models.BooleanField(_('LDAP User'), editable=False, default=False)

    # User objects manager
    objects = UserManager()

    # Username field and required fields
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def is_admin(self):
        """
        Check if the user is a member of the administrator group.
        """
        groups = self.get_groups()
        for group in groups:
            if group['uuid'] == G_ADMIN:
                return True
        return False

    def get_groups(self):
        """
        Retrieve a list of group membership.
        """
        membership = []
        for g in DBGroupMembers.objects.filter(member=self.uuid).values():
            gd = DBGroupDetails.objects.filter(uuid=g['group_id']).values()[0]
            membership.append({
                'uuid': gd['uuid'],
                'name': gd['name'],
                'desc': gd['desc']
            })
        return membership

    # Model metadata
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

class DBUserAPIKeys(models.Model):
    """
    Main database model for storing user API keys.
    """
    
    # User API key table columns
    user    = models.ForeignKey(User, to_field='uuid', db_column='user')
    api_key = models.CharField(max_length=64, unique=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'auth_user_api_keys'
        
class DBUserAPITokens(models.Model):
    """
    Main database model for storing user API tokens.
    """
    
    # User API token table columns
    user    = models.ForeignKey(User, to_field='uuid', db_column='user')
    token   = models.CharField(max_length=255, unique=True)
    expires = models.DateTimeField()
    
    # Custom model metadata
    class Meta:
        db_table = 'auth_user_api_tokens'