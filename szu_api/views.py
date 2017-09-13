# -*- coding: utf-8 -*-

from django.http import HttpResponse

def queryTermNum(req):
    return HttpResponse(getTermNum())

def getTermNum():
    '''
    获取当前学期号
    '''
    return "20171"