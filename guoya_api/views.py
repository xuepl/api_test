import django_filters
from django.db.models import QuerySet
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics
# Create your views here.
from rest_framework.response import Response
from rest_framework import views

from guoya_api.common.automation_case import run_api
from . import serializers
from . import models
from rest_framework import mixins

# APIView
# genericAPIView
# ModelViewSet
class Projects(generics.GenericAPIView):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields=['name']

    def get(self,request,*args,**kwargs):
        """
        获取项目列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        students = self.filter_queryset(self.get_queryset())  # 使用filter_queryset方法对查询集进行过滤
        serializer = self.get_serializer(instance=students, many=True)
        return Response(serializer.data)


    def post(self,request,*args,**kwargs):
        """
        新增项目
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        serializer = serializers.ProjectDeserializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data)



class Project(mixins.DestroyModelMixin,mixins.UpdateModelMixin,generics.GenericAPIView):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectDeserializer

    def get(self,request,*args,**kwargs):
        '''
        查询单个项目的详细信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        project = self.get_object()
        return Response(serializers.ProjectSerializer(instance=project).data)

    def put(self,request,*args,**kwargs):
        '''
        修改单个项目
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        '''
        删除单个项目
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        return self.destroy(request, *args, **kwargs)


class TestCases(views.APIView):
    def post(self, request):
        data = request.data
        headers = data.pop('headDict')
        body_data = data.pop("requestList")
        project_id = data.pop("project_id")
        regular_param = data.pop("RegularParam")
        obj = models.AutomationTestCase.objects.get(id=data.pop("automationTestCase_id"))
        # 把接口详细信息存入automationcaseapi表中
        serializer = serializers.AutomationCaseApiDeserializer(data=data)
        serializer.is_valid(raise_exception=True)
        test_case = serializer.save(automationTestCase=obj)
        for h in headers:
            if h['name'] == "":
                continue
            serializer =serializers.AutomationHeadDeserializer(data=h)
            serializer.is_valid(raise_exception=True)
            serializer.save(automationCaseApi=test_case)
        if data["requestParameterType"] == 'raw':
            raw = {"data":body_data}
            serializer = serializers.AutomationParameterRawDeserializer(data=raw)
            serializer.is_valid(raise_exception=True)
            serializer.save(automationCaseApi=test_case)
        elif(data["requestParameterType"] == 'form-data'):
            for p in body_data:
                serializer = serializers.AutomationParameterDeserializer(data=p)
                serializer.is_valid(raise_exception=True)
                serializer.save(automationCaseApi=test_case)

        return Response("ok")


class ExcuteCase(views.APIView):

    def post(self,request):
        # 获取请求数据
        data = request.data
        # 获取要执行的接口id
        api_id = data["api_id"]
        # 获取使用主机id
        host_id = data["host_id"]
        # 校验 接口数据是否存在，是否有缺失
        run_api(host_id=host_id,api_id=api_id)
        case_api = models.AutomationCaseApi.objects.filter(id = api_id).first()
        res = case_api.test_result.all().last()
        serializer = serializers.AutomationTestResultSerializer(instance=res)
        return Response(serializer.data)







