from django.db import models
from django.utils import timezone
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# CloudScape Libraries
from cloudscape.common.vars import G_ADMIN, G_USER, G_DEFAULT
from cloudscape.engine.api.app.group.models import DBGroupMembers, DBGroupDetails

class DBUserAPIKeys(models.Model):
    """
    Main database model for storing user API keys.
    """
    
    # User API key table columns
    user    = models.ForeignKey('user.DBUser', to_field='uuid', db_column='user')
    api_key = models.CharField(max_length=64, unique=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'auth_user_api_keys'
        
class DBUserAPITokens(models.Model):
    """
    Main database model for storing user API tokens.
    """
    
    # User API token table columns
    user    = models.ForeignKey('user.DBUser', to_field='uuid', db_column='user')
    token   = models.CharField(max_length=255, unique=True)
    expires = models.DateTimeField()
    
    # Custom model metadata
    class Meta:
        db_table = 'auth_user_api_tokens'

class DBUserQuerySet(models.query.QuerySet):
    """
    Custom query set for the user model.
    """
    
    # Timestamp format / timefield keys
    timestamp  = '%Y-%m-%d %H:%M:%S'
    timefields = ['date_joined', 'last_login']
    
    def __init__(self, *args, **kwargs):
        super(DBUserQuerySet, self).__init__(*args, **kwargs)

    def _is_admin(self, user):
        """
        Check if the user is a member of the administrator group.
        """
        groups = self._get_groups(user)
        for group in groups:
            if group['uuid'] == G_ADMIN:
                return True
        return False

    def _get_groups(self, user):
        """
        Retrieve a list of group membership.
        """
        membership = []
        for g in DBGroupMembers.objects.filter(member=user).values():
            gd = DBGroupDetails.objects.filter(uuid=g['group_id']).values()[0]
            membership.append({
                'uuid': gd['uuid'],
                'name': gd['name'],
                'desc': gd['desc']
            })
        return membership

    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Store the initial results
        _u = super(DBUserQuerySet, self).values(*fields)
        
        # Process each user object definition
        for user in _u:
            
            # Parse any time fields
            for timefield in self.timefields:
                if timefield in user:
                    user[timefield] = user[timefield].strftime(self.timestamp)
            
            # Get user groups and administrator status
            user.update({
                'groups': self._get_groups(user['uuid']),
                'is_admin': self._is_admin(user['uuid'])
            })
        
        # Return the constructed user results
        return _u

class DBUserManager(BaseUserManager):
    """
    Custom user manager for the custom user model.
    """
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return DBUserQuerySet(model=self.model)
        
    def get_or_create(self, **kwargs):
        """
        Get or create a new user object.
        """
        
        
    def create_user(self, uuid, username, email, password, group, **kwargs):
        """
        Create a new user account.
        """
        
        # Import the API keys module
        from cloudscape.engine.api.auth.key import APIKey
        
        # Get the current timestamp
        now = timezone.now()
        
        # Create a new user object
        user = self.model(
            uuid         = uuid,
            username     = username,
            email        = self.normalize_email(email),
            is_active    = True,
            last_login   = now,
            date_joined  = now,
            **kwargs
        )
        
        # Set the password and and save
        user.set_password(password)
        user.save(using=self._db)
        
        # Get the group object
        group = DBGroupDetails.objects.get(uuid=group)
        
        # Add the user to the group
        group.members_set(user)
        
        # Generate an API key for the user
        key_str = APIKey().create()
        api_key = DBUserAPIKeys(
            user    = user,
            api_key = key_str
        )
        api_key.save()
        
        # Return the user object
        return user

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
    objects = DBUserManager()

    # Username field and required fields
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    # Model metadata
    class Meta:
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')