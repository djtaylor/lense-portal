def register():
    """
    Register the administration handler.
    """
    LENSE.PORTAL.INTERFACE.register('admin')
    LENSE.PORTAL.INTERFACE.admin.include('js', [
        {
            'id': 'acl',
        }
    ])