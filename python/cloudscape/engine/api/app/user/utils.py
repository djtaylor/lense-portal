import re
import string
import random
from uuid import uuid4

# Django Libraries
from django.core.mail import send_mail

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.auth.key import APIKey
from cloudscape.common.vars import G_ADMIN, U_ADMIN
from cloudscape.engine.api.app.user.models import DBUser, DBUserAPIKeys
from cloudscape.engine.api.app.group.models import DBGroupDetails

def gen_password(length=12):
    """
    Helper method used to generate a random password.
    """
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(length)])

class UserDelete:
    """
    API class used to handle deleting a user account.
    """
    def __init__(self, parent):
        self.api  = parent
        
        # Target user
        self.user = self.api.acl.target_object()
        
    def launch(self):
        """
        Worker method for deleting a user account.
        """
        
        # Construct a list of authorized users
        auth_users = self.api.acl.authorized_objects('user', 'user/get')
        
        # If the user does not exist or access is denied
        if not self.user in auth_users.ids:
            return invalid('Cannot delete user <%s>, not found or access denied' % self.user)
        self.api.log.info('Deleting user account <%s>' % self.user)
        
        # Cannot delete default administrator
        if self.user == U_ADMIN:
            return invalid('Cannot delete the default administrator account')

        # Delete the user account
        DBUser.objects.filter(username=self.user).delete()

        # Return the response
        return valid('Successfully deleted user account', {
            'username': self.user
        })

class UserEnable:
    """
    API class used to handle enabling a user account.
    """
    def __init__(self, parent):
        self.api = parent

        # Target user
        self.user = self.api.acl.target_object()
        
    def launch(self):
        """
        Worker method used to handle enabling a user account.
        """
        
        # Construct a list of authorized users
        auth_users = self.api.acl.authorized_objects('user', 'user/get')
        
        # If the user does not exist or access is denied
        if not self.user in auth_users.ids:
            return invalid('Cannot enable user <%s>, not found or access denied' % self.user)
        self.api.log.info('Enabling user account <%s>' % self.user)

        # Cannot enable/disable default administrator
        if self.user == U_ADMIN:
            return invalid('Cannot enable/disable the default administrator account')

        # Get the user object and disable the account
        user_obj = DBUser.objects.get(username=self.user)
        user_obj.is_active = True
        user_obj.save()
        
        # Return the response
        return valid('Successfully enabled user account', {
            'username': self.user
        })

class UserDisable:
    """
    API class used to handle disabling a user account.
    """
    def __init__(self, parent):
        self.api = parent

        # Target user
        self.user = self.api.acl.target_object()
        
    def launch(self):
        """
        Worker method used to handle disabling a user account.
        """
        
        # Construct a list of authorized users
        auth_users = self.api.acl.authorized_objects('user', 'user/get')
        
        # If the user does not exist or access is denied
        if not self.user in auth_users.ids:
            return invalid('Cannot disable user <%s>, not found or access denied' % self.user)
        self.api.log.info('Disabling user account <%s>' % self.user)

        # Cannot enable/disable default administrator
        if self.user == U_ADMIN:
            return invalid('Cannot enable/disable the default administrator account')

        # Get the user object and disable the account
        user_obj = DBUser.objects.get(username=self.user)
        user_obj.is_active = False
        user_obj.save()
        
        # Return the response
        return valid('Successfully disabled user account', {
            'username': self.user
        })

class UserResetPassword:
    """
    API class used to handle resetting a user's password.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Targer user
        self.user = self.api.acl.target_object()
        
    def launch(self):
        """
        Worker method to handle resetting a user's password.
        """
        
        # Construct a list of authorized users
        auth_users = self.api.acl.authorized_objects('user', 'user/get')
        
        # If the user does not exist or access is denied
        if not self.user in auth_users.ids:
            return invalid('Cannot reset password for user <%s>, not found or access denied' % self.user)
        self.api.log.info('Resetting password for user <%s>' % self.user)
        
        # Generate a new random password
        new_pw = gen_password()

        # Get the user object and set the new password
        try:
            user_obj = DBUser.objects.get(username=self.user)
            user_obj.set_password(new_pw)
            user_obj.save()
            self.api.log.info('Successfully reset password for user <%s>' % self.user)
            
        # Critical error when resetting user password
        except Exception as e:
            return invalid('Failed to reset password for user <%s>: %s' % (self.user, str(e)))
        
        # Send the email
        try:
            
            # Email properties
            email_sub  = 'CloudScape Password Reset: %s' % self.user
            email_txt  = 'Your password has been reset. You may login with your new password "%s".' % new_pw
            email_from = 'noreply@vpls.net'
            email_to   = [user_obj.email]
            
            # Send the email
            send_mail(email_sub, email_txt, from_email=email_from, recipient_list=email_to, fail_silently=False)
            self.api.log.info('Sent email confirmation for password reset to user <%s>' % self.user)
            
            # Return the response
            return valid('Successfully reset user password')
        
        # Critical error when sending password reset notification
        except Exception as e:
            return invalid(self.api.log.error('Failed to send password reset confirmation: %s' % str(e)))

class UserCreate:
    """
    API class designed to create a new user account.
    """
    def __init__(self, parent):
        """
        Construct the UserCreate utility
        
        :param parent: The APIBase
        :type parent: APIBase
        """
        self.api  = parent

        # New user UUID
        self.uuid = str(uuid4())

    def _validate(self):
        """
        Make sure the user request is valid.
        """

        # Make sure the user doesn't exist
        if DBUser.objects.filter(username=self.api.data['username']).count():
            return invalid(self.api.log.error('The user account <%s> already exists' % self.api.data['username']))

        # Password RegEx Tester:
        # - At least 8 characters
        # - At least 1 lower case letter
        # - At least 1 upper case letter
        # - At least 1 number
        # - At least 1 special character
        pw_regex = re.compile(r'^\S*(?=\S{8,})(?=\S*[a-z])(?=\S*[A-Z])(?=\S*[\d])(?=\S*[\W])\S*$')
        if not pw_regex.match(self.api.data['password']):
            return invalid(self.api.log.error('Password is too weak. Must be at least <8> characters and contain - upper/lower case letters, numbers, and special characters'))
        return valid()

    def launch(self):
        """
        Worker method used to handle creation of a new user account.
        """
        
        # Validate the user creation request
        req_status = self._validate()
        if not req_status['valid']:
            return req_status
        
        # Try to create the new user account
        try:
            
            # If manually supplying a password
            password = gen_password()
            if ('password' in self.api.data):
                if not ('password_confirm' in self.api.data):
                    return invalid('Missing <password_confirm> request parameter')
                if not (self.api.data['password'] == self.api.data['password_confirm']):
                    return invalid('Request parameters <password> and <password_confirm> do not match')
                password = self.api.data['password']
                
            # Create the user account
            new_user = DBUser.objects.create_user(
                uuid         = self.uuid,
                username     = self.api.data['username'],
                email        = self.api.data['email'],
                password     = self.api.data['password']
            )
                
            # Save the user account details
            new_user.save()
            self.api.log.info('Created user account <%s>' % (self.api.data['username']))
            
            # Get the group object
            group = DBGroupDetails.objects.get(uuid=self.api.data['group'])
            
            # Add the user to the group
            group.members_set(new_user)
            
            # Generate an API key for the user
            key_str = APIKey().create()
            api_key = DBUserAPIKeys(
                user    = new_user,
                api_key = key_str
            )
            api_key.save()
            self.api.log.info('Generated API key <%s> for user <%s>' % (key_str, self.api.data['username']))
            
            # Send the account creation email
            try:
                
                # Email properties
                email_sub  = 'CloudScape New Account: %s' % new_user.username
                email_txt  = 'Your account has been created. You may login with your password "%s".' % password
                email_from = 'noreply@vpls.net'
                email_to   = [new_user.email]
                
                # Send the email
                send_mail(email_sub, email_txt, from_email=email_from, recipient_list=email_to, fail_silently=False)
                self.api.log.info('Sent email confirmation for new account <%s> to <%s>' % (new_user.username, new_user.email))
                
                # Return valid
                return valid('Successfully sent account creation confirmation')
            except Exception as e:
                return invalid(self.api.log.error('Failed to send account creation confirmation: %s' % str(e)))
            
        # Something failed during creation
        except Exception as e:
            return invalid(self.api.log.exception('Failed to create user account <%s>: %s' % (self.api.data['username'], str(e))))
        
        # Return the response
        return valid('Successfully created user account', {
            'username': self.api.data['username'],
            'email':    self.api.data['email'],
            'super':    False if (not 'is_superuser' in self.api.data) else self.api.data['is_superuser'],
        })

class UserGet:
    """
    API class designed to retrieve the details of a single user, or a list of all user
    details.
    """
    def __init__(self, parent):
        """
        Construct the UserGet utility
        
        :param parent: The APIBase
        :type parent: APIBase
        """
        self.api  = parent
        
        # Target user
        self.user = self.api.acl.target_object()
        
    def _get_user(self, id):
        user_obj = DBUser.objects.get(username=id)
         
        # Map the user details
        return {
            'uuid':         user_obj.uuid,
            'username':     user_obj.get_username(),
            'first_name':   user_obj.first_name,
            'last_name':    user_obj.last_name,
            'is_active':    user_obj.is_active,
            'is_staff':     user_obj.is_staff,
            'is_superuser': user_obj.is_superuser,
            'email':        user_obj.email,
            'groups':       user_obj.get_groups()
        }
            
    def launch(self):
        """
        Worker method that does the work of retrieving user details.
        
        :rtype: valid|invalid
        """
        
        # Construct a list of authorized user objects
        auth_users = self.api.acl.authorized_objects('user')
        
        # If retrieving a specific user
        if self.user:
            
            # If the user does not exist or access is denied
            if not self.user in auth_users.ids:
                return invalid('User <%s> does not exist or access denied' % self.user)
            
            # Return the user details
            return valid(self._get_user(self.user))
            
        # If retrieving all users
        else:
        
            # Construct a detailed users object
            users_obj = []
            for user in auth_users.details:
                users_obj.append(self._get_user(user['username']))
        
            # Return the constructed users object
            return valid(users_obj)