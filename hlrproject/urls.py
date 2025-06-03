from django.urls import path, include
from hlrapp.views import hlr_lookup, upload_csv
from hlrapp.api_views import hlr_lookup_api
from rest_framework.authtoken.views import obtain_auth_token
from hlrapp.views import hlr_lookup, upload_csv, download_csv, download_txt

urlpatterns = [
    path('', hlr_lookup, name='hlr_lookup'),
    path('upload-csv/', upload_csv, name='upload_csv'),
    path('api/hlr-lookup/', hlr_lookup_api, name='hlr_lookup_api'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    
    # Add this line for built-in auth views (login/logout)
    path('accounts/', include('django.contrib.auth.urls')),
    path('', hlr_lookup, name='hlr_lookup'),
    path('upload-csv/', upload_csv, name='upload_csv'),
    path('download-csv/', download_csv, name='download_csv'),   # <--- THIS IS REQUIRED
    path('download-txt/', download_txt, name='download_txt'),
    
]
