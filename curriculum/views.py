# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
import simplejson

from curriculum.models import Student, Course, StudentCourseMap

def index(request):
  if request.method == "GET":
    data = query(request.GET.get("stuNum", None), request.GET.get("term", None))
  else:
    return HttpResponseNotFound('<h1>Page not found</h1>')

  #ensure_ascii=False用于处理中文
  return HttpResponse(simplejson.dumps(data, ensure_ascii=False))

def queryStudent(request):
  if request.method == "GET":
    student = getStudentInfo(request.GET.get("stuNum", None))
    if student == None:
      return HttpResponseNotFound('<h1>Page not found</h1>')
    data = {
      "code": 10000,
      "error": None,
      "data": student
    }
    return HttpResponse(simplejson.dumps(data, ensure_ascii=False))
  else:
    return HttpResponseNotFound('<h1>Page not found</h1>')

def getStudentInfo(stuNum):
  '''
    通过学号获取学生信息
    查询不到返回None
  '''
  if stuNum == None:
    return None
  student = Student.objects.filter(stu_num=stuNum)
  if len(student) == 0:
    return None
  student = student[0]
  return {
    "stuNum": student.stu_num,
    "name": student.name,
    "sex": student.sex,
    "major": student.major,
    "class": student.stu_class
  }

def query(stuNum, term):
  if stuNum == None:
    return {
      "code": 10404,
      "error": "参数错误"
    }

  if term == None:
    result = StudentCourseMap.objects.filter(student__stu_num=stuNum)
  else:
    result = StudentCourseMap.objects.filter(term=term).filter(student__stu_num=stuNum)

  data = {}
  for studentCourseMap in result:
    course = studentCourseMap.course
    if data.get(studentCourseMap.term) == None:
      data[studentCourseMap.term] = []

    data[studentCourseMap.term].append({
      "courseNum": course.course_num,
      "courseName": course.course_name,
      "teacher": course.teacher,
      "classWeek": course.class_week,
      "classTime": course.class_time,
      "venue": course.venue
    })
  return {
    "code": 10000,
    "error": None,
    "data": data
  }


