from paramiko.py3compat import byte_chr

""" SSH2 Response Codes

Pulled directly from the source code for the SFTP server in OpenSSH.
"""
SSH2_FXP_STATUS=101
SSH2_FX_OK=0
SSH2_FX_EOF=1
SSH2_FX_NO_SUCH_FILE=2
SSH2_FX_PERMISSION_DENIED=3
SSH2_FX_FAILURE=4
SSH2_FX_BAD_MESSAGE=5
SSH2_FX_BAD_MESSAGE=6
SSH2_FX_CONNECTION_LOST=7
SSH2_FX_OP_UNSUPPORTED=8

""" SSH Response Message Constants

Used mainly for debugging.
"""
SCP_STATUS = {
    0: 'Success',
    1: 'End of file',
    2: 'No such file',
    3: 'Permission denied',
    4: 'Failure',
    5: 'Bad message',
    6: 'No connection',
    7: 'Connection lost',
    8: 'Operation unsupported'  
}