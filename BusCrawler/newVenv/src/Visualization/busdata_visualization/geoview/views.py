from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.core.serializers import serialize
from django.shortcuts import render
from .models import Line
from shapely.geometry import shape
from shapely import wkt
import json
# import pdb; pdb.set_trace()

def geoview(request):
  lines = Line.objects.all()
  data = serialize('geojson', lines, geometry_field='geometry', fields=('line', 'auslastung_montag'))
  # print(data)
  context = {
    'lines': data,
  }
  return render(request, 'index.html', context)

def get_bus_data(request):
  lines = Line.objects.all()
  data = serialize('geojson', lines, geometry_field='geometry', fields=('line', 'auslastung_montag'))
  return JsonResponse(json.loads(data), safe=False)