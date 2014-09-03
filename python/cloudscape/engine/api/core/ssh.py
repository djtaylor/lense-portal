import os
from Crypto.PublicKey import RSA
from encrypted_fields import EncryptedTextField

# CloudScape Libraries
from cloudscape.engine.api.app.host.models import DBHostSSHAuth, DBHostDKeys

class SSHKey:
    """
    SSHKey
    
    Class used to handle SSH keys. This includes generating and decrypting SSH keypairs, as
    well as managing the deployment SSH keys used for Windows machines.
    """
    def generate(self):
        """
        Generate a public/private SSH keypair.
        """
        
        # Generate an RSA key pair
        key_obj = RSA.generate(2048, os.urandom)
        
        # Get the public and private keys
        private_key    = key_obj.exportKey('PEM')
        public_key_str = key_obj.publickey().exportKey('OpenSSH')
        public_key     = '%s %s' % (public_key_str, 'cloudscape')
        
        # Convert newlines in private key to a storable format
        private_key    = private_key.replace("\n", "<n>")
        
        # Return the keypair in string format
        return {'public_key': public_key, 'private_key': private_key}
    
    def _get_key_row(self, uuid, dkey):
        """
        Get an SSH keypair row from the database.
        
        @param uuid: The UUID of either the host or deployment key
        @type  uuid: str
        @param dkey: Whether to retrieve a deployment key
        @type  dkey: bool
        """
        if dkey:
            return DBHostDKeys.objects.filter(uuid=uuid).values()[0]
        else:
            return DBHostSSHAuth.objects.filter(host=uuid).values()[0]
    
    def decrypt(self, uuid=None, dkey=False):
        """
        Decrypt an existing SSH keypair.
        
        @param uuid: The UUID of either the host or deployment key
        @type  uuid: str
        @param dkey: Whether to retrieve a deployment key
        @type  dkey: bool
        """
        if not uuid:
            return False
        else:
            
            # Grab the encrypted keypair data
            ssh_key_query  = self._get_key_row(uuid, dkey)
            pub_encrypted  = ssh_key_query['pub_key']
            priv_encrypted = ssh_key_query['priv_key']
            
            # Decrypt the keys
            pub_decrypted  = EncryptedTextField().to_python(pub_encrypted)
            priv_decrypted = EncryptedTextField().to_python(priv_encrypted)
            
            # Restore linebreaks in private key
            priv_formatted = priv_decrypted.replace('<n>', '\n')
            
            # Return the keypair object
            return { 'pub_key':  pub_decrypted,
                     'priv_key': priv_formatted }