class HandlerNavigation(object):
    attrs = {
        'parent': {
            'name': 'Administration'
        },
        'children': [
            {
                "name": "Users",
                "link": "/admin?view=users"
            },
            {
                "name": "Groups",
                "link": "/admin?view=groups"
            },
            {
                "name": "Handlers",
                "link": "/admin?view=handlers"
            },
            {
                "name": "ACL",
                "link": "/admin?view=acls"
            }
        ]
    }
    