from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

def call_hlr_api(msisdn_list):
    url = 'https://api.1s2u.io/hlr'
    numbers = ",".join(msisdn_list)
    params = {
        'username': settings.HLR_USERNAME,
        'password': settings.HLR_PASSWORD,
        'msisdn': numbers,
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 429:
            return None, "Rate limit exceeded, please wait and try again."
        else:
            return None, f"API error: HTTP {response.status_code}"
    except Exception as e:
        logger.error(f"HLR API call failed: {e}")
        return None, f"Request failed: {e}"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hlr_lookup_api(request):
    msisdns = request.data.get('msisdns')
    if not msisdns or not isinstance(msisdns, list):
        return Response({'error': 'msisdns must be a list of phone numbers'}, status=400)
    if len(msisdns) > 30:
        return Response({'error': 'Maximum 30 numbers allowed per request'}, status=400)

    result, error = call_hlr_api(msisdns)
    if error:
        return Response({'error': error}, status=400)
    return Response(result)
