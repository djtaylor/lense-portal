Database Encryption Keys
=========
The CloudScape API engine encrypts information for a number of database fields, including SSH keys and other sensitive data. CloudScape is based on the [Django] framework, and uses [django-encrypted-fields] to manage encrypting and decrypting the data as needed.

This directory must contain an encryption key and metadata generated using keyczar:

Generating Keys
----------------

```sh
keyczart create --location=/home/cloudscape/dbkey --purpose=crypt
keyczart addkey --location=/home/cloudscape/dbkey --status=primary --size=256
```

[Django]:https://www.djangoproject.com/
[django-encrypted-fields]:https://github.com/defrex/django-encrypted-fields