from django.shortcuts import render
from dataclasses import dataclass


import json

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from .parsers.parse_12d_html import parse_12d_html
from .checks.horizontal import check_horizontal_alignment
from .checks.vertical import check_vertical_alignment

VALID_SPEEDS = {30, 40, 50, 60, 70, 80, 90, 100}
VALID_EMAX = { 6, 7, 10}
VALID_SURFACE = {'sealed', 'unsealed'}
VALID_OBJECT_HEIGHT = {0, 0.2}
VALID_VEHICLES = ['LME', 'Trucks', 'RAV-4S', 'HME']


# IMPORT AND USE A DATACLASS TO STORE CONFIGURATION SETTINGS
@dataclass
class CheckSettings:
    speed: int
    emax: int
    road_surface: str
    object_height: float
    vehicles: list[str]


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
        road_surface = str(request.data.get('road_surface', 'unsealed'))
        object_height = float(request.data.get('object_height', 0))
        vehicles_raw = request.data.get('vehicles', [])

        #Parse JSON into a list
        try:
            vehicles = json.loads(vehicles_raw)
            if not isinstance(vehicles, list):
                return Response({'error': 'Vehicles parameter must be an array'}, status=status.HTTP_400_BAD_REQUEST)
        except (json.JSONDecodeError, TypeError):
            return Response({'error': 'Malformed JSON string provided for vehicles'}, status=status.HTTP_400_BAD_REQUEST)
        

        if speed not in VALID_SPEEDS:
            return Response({'error': f'Invalid speed limit: {speed}'}, status=status.HTTP_400_BAD_REQUEST)
        if emax not in VALID_EMAX:
            return Response({'error': f'Invalid Emax value: {emax}'}, status=status.HTTP_400_BAD_REQUEST)
        if road_surface not in VALID_SURFACE:
            return Response({'error': f'Invalid Surface type: {road_surface}'}, status=status.HTTP_400_BAD_REQUEST)
        if object_height not in VALID_OBJECT_HEIGHT:
            return Response({'error': f'Invalud Object Height: {object_height}'}, status=status.HTTP_400_BAD_REQUEST)
        if not set(vehicles).issubset(VALID_VEHICLES):
            return Response({'error': f'Invalid vehicles provided: {vehicles}'}, status=status.HTTP_400_BAD_REQUEST)

    except ValueError as e:
        return Response({'error': f'Invalid input parameters: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)



    try:
        alignment_data = parse_12d_html(html_content)
    except Exception as e:
        return Response({'error': f'Error parsing file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        settings = CheckSettings(speed=speed, emax = emax, road_surface=road_surface, object_height=object_height, vehicles=vehicles)
        horizontal_results = check_horizontal_alignment(alignment_data, settings)
        vertical_results = check_vertical_alignment(alignment_data, settings)
    except Exception as e:
        return Response({'error': f'Check failed: {str(e)}'}, status = 500)

    all_results = horizontal_results + vertical_results

    return Response({
        'alignment': {
            'name': alignment_data['name'],
            'design_speed': speed,
            'emax': emax,
            'start_chainage': alignment_data['start_chainage'],
            'end_chainage': alignment_data['end_chainage'],
            'warnings': alignment_data['warnings'],
        },
        'results': all_results,
        'summary': {
            'total_checks': len(all_results),
            'pass':    sum(1 for r in all_results if r['status'] == 'pass'),
            'fail':    sum(1 for r in all_results if r['status'] == 'fail'),
            'warning': sum(1 for r in all_results if r['status'] == 'warning'),
        }
    })