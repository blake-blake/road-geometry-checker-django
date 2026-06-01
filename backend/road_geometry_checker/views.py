from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from .parsers.parse_12d_html import parse_12d_html
from .checks.horizontal import check_horizontal_alignment

VALID_SPEEDS = {30, 40, 50, 60, 70, 80, 90, 100}
VALID_EMAX = { 6, 7, 10}

@api_view(['POST'])
@parser_classes([MultiPartParser])
def check_road_geometry(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']

    # Read and decode the file content
    try:
        raw = file.read()
        try:
            html_content = raw.decode('utf-8')
        except UnicodeDecodeError:
            html_content = raw.decode('utf-16')
    except Exception as e:
        return Response({'error': f'Error reading file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    # Check input parameters
    try:
        speed = int(request.data.get('design_speed', 100))
        emax = int(request.data.get('emax', 6))

        if speed not in VALID_SPEEDS:
            return Response({'error': f'Invalid speed limit: {speed}'}, status=status.HTTP_400_BAD_REQUEST)

        if emax not in VALID_EMAX:
            return Response({'error': f'Invalid Emax value: {emax}'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as e:
        return Response({'error': f'Invalid input parameters: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)



    try:
        alignment_data = parse_12d_html(html_content)
    except Exception as e:
        return Response({'error': f'Error parsing file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        horizontal_results = check_horizontal_alignment(alignment_data, speed, emax)
    except Exception as e:
        return Respone({'error': f'Check failed: {str(e)}'}, status = 500)

    return Response({
        'alignment': {
            'name': alignment_data['name'],
            'design_speed': speed,
            'emax': emax,
            'start_chainage': alignment_data['start_chainage'],
            'end_chainage': alignment_data['end_chainage'],
            'warnings': alignment_data['warnings'],
        },
        'results': horizontal_results,
        'summary': {
            'total_checks': len(horizontal_results),
            'pass':    sum(1 for r in horizontal_results if r['status'] == 'pass'),
            'fail':    sum(1 for r in horizontal_results if r['status'] == 'fail'),
            'warning': sum(1 for r in horizontal_results if r['status'] == 'warning'),
        }
    })