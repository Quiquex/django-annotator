import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponse,
                         HttpResponseForbidden,
                         HttpResponseBadRequest)
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

import annotator
from annotator import models, serializers


@csrf_exempt
def index_create(request):
    if request.method == "GET":
        annotations = models.Annotation.objects.all()
        serializer = serializers.AnnotationSerializer(annotations, many=True)
        return JsonResponse(serializer.data)
    elif request.method == "POST":
        data = json.loads(request.body)
        serializer = serializers.AnnotationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response = HttpResponse(status=303)
            response["Location"] = reverse("read_update_delete",
                                           kwargs={"pk": serializer.data["id"]})
            return response
        else:
            return HttpResponseBadRequest(content=str(serializer.errors))
    else:
        return HttpResponseForbidden()


@csrf_exempt
def read_update_delete(request, pk):
    if request.method == "GET":
        annotation = get_object_or_404(models.Annotation, pk=pk)
        serializer = serializers.AnnotationSerializer(annotation)
        return JsonResponse(serializer.data, status=200)
    elif request.method == "PUT":
        annotation = get_object_or_404(models.Annotation, pk=pk)
        data = json.loads(request.body)
        serializer = serializers.AnnotationSerializer(annotation, data=data)
        if serializer.is_valid():
            serializer.save()
            response = HttpResponse(status=303)
            response["Location"] = reverse("read_update_delete",
                                           kwargs={"pk": serializer.data["id"]})
            return response
        else:
            return HttpResponseBadRequest(content=str(serializer.errors))
    elif request.method == "DELETE":
        annotation = get_object_or_404(models.Annotation, pk=pk)
        annotation.delete()
        return HttpResponse(status=204)
    else:
        return HttpResponseForbidden()


def search(request):
    if request.method == "GET":
        query = {k: v for k, v in request.GET.items()}
        annotations = models.Annotation.objects.filter(**query)
        serializer = serializers.AnnotationSerializer(annotations, many=True)
        return JsonResponse({"total": len(serializer.data), "rows": serializer.data})
    else:
        return HttpResponseForbidden()


class DemoView(TemplateView):
    template_name = "annotator/demo.html"
