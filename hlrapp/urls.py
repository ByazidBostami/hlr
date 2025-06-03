from django.urls import path
from hlrapp.views import hlr_lookup, upload_csv, download_csv, download_txt

urlpatterns = [
    path('', hlr_lookup, name='hlr_lookup'),
    path('upload-csv/', upload_csv, name='upload_csv'),
    path('download-csv/', download_csv, name='download_csv'),  # <-- Make sure this exists
    path('download-txt/', download_txt, name='download_txt'),
    # ... other patterns ...
]
