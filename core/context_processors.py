import os

def platform_info(request):
    return {
        'platform_requisites': os.environ.get(
            'PLATFORM_REQUISITES',
            'Dani Systems (ИП в стадии регистрации)'
        )
    }
