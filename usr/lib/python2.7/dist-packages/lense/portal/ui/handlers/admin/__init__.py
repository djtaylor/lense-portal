class HandlerNavigation(object):
    attrs = {
        'parent': {
            'name': 'Administration'
        },
        'children': [
            {
                "name": "Users",
                "link": "/admin?view=users",
                "icon": "user"
            },
            {
                "name": "Groups",
                "link": "/admin?view=groups",
                "icon": "user"
            },
            {
                "name": "Handlers",
                "link": "/admin?view=handlers",
                "icon": "wrench"
            }
        ]
    }
