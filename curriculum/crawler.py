# -*- coding: utf-8 -*-
import requests
import re

import sys, os
sys.path.append("..")
os.environ['DJANGO_SETTINGS_MODULE'] = 'szu_api.settings'
from django.conf import settings
import django
django.setup()
from curriculum.models import Course, Student, StudentCourseMap

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

termNum = "20162" # 要爬取的学期号
coursesListBaseUrl = "http://192.168.2.229/newkc/akcjj0.asp"
course = "http://192.168.2.229/newkc/akechengdw.asp" # 开课单位列表url
courseListUrl = "http://192.168.2.229/newkc/kccx.asp?flag=kkdw" # 课程列表url
courseInfoUrl = "http://192.168.2.229/newkc/kcxkrs.asp" # 选修课程的学生列表url

req = requests.Session()

def resolveCollegeList():
  '''
    获取开课单位列表
    返回开课单位名称数组['Mooc']
  '''
  response = req.get(course)
  html = response.content.decode('gb2312')
  reg = ur'<option value=\"(.*)\">'
  return re.findall(reg, html)

def getCourseList(college):
  '''
    获取指定开课单位的课程列表
    将课程信息保存到数据库当中
    调用getStudentInfo获取学生信息
    @param college 开课单位
  '''
  print "匹配课程：{0}".format(college)

  tableReg = "<table border=1 bgColor=white cellSpacing=0 cellPadding=0 align=center background=\"\" borderColorDark=#ffffff borderColorLight=#00ff00 width=\"960\" height=\"42\">([\\w\\W]*?)</table>"
  trReg = "<tr>([\\w\\W]*?)</tr>"

  response = req.post(courseListUrl, data={"bh": college.encode('gb18030')})
  html = response.content.decode('gb18030')
  matchObj = re.search(tableReg, html)
  if matchObj == None:
    print html
    print "匹配table数据失败，开课单位为: {0}".format(college)
    return

  trsHtml = matchObj.group(1)
  trsList = re.findall(trReg, trsHtml)
  trsList = trsList[1:-1] # 跳过表格头和尾信息

  for tr in trsList:
    tr = re.compile("</?(.*?)>").sub("", tr) # 去除 html 标签
    tds = tr.split()
    if len(tds) == 15:
      # {
      #   "course_num": tds[1],
      #   "course_name": tds[2],
      #   "teacher": tds[9],
      #   "class_week": tds[10],
      #   "class_time": tds[11],
      #   "venue": tds[12]
      # }
      # 若课程不存在则添加到数据库中
      courseObj = Course.objects.filter(course_num=tds[1], course_name=tds[2], teacher=tds[9], class_week=tds[10], class_time=tds[11], venue=tds[12])
      if len(courseObj) == 0:
        courseObj = Course(course_num=tds[1], course_name=tds[2], teacher=tds[9], class_week=tds[10], class_time=tds[11], venue=tds[12])
        courseObj.save()
      else:
        courseObj = courseObj[0]

      getStudentInfo(tds[1], courseObj)

def getStudentInfo(courseNum, courseObj):
  '''
    获取指定课程的学生列表
    并把学生信息保存到数据库当中
    @param courseNum 课程号
    @param courseObj 课程的数据库对象
  '''
  print "获取课程编号为{0}的学生列表".format(courseNum)

  tableReg = '<table border=1 bgColor=white cellSpacing=0 cellPadding=0 align=center background="" borderColorDark=#ffffff borderColorLight=#000000 width="660" height="42">([\\w\\W]*?)</table>'
  trReg = "<tr>([\\w\\W]*?)</tr>"

  response = req.get(courseInfoUrl, params={"ykch": courseNum})

  html = response.content.decode('gb18030')

  tables = re.findall(tableReg, html)
  if len(tables) < 2:
    print html
    print "匹配table数据失败，课程号为: {0}".format(courseNum)
    return

  trsHtml = tables[1]
  trsList = re.findall(trReg, trsHtml)
  trsList = trsList[1:-1] # 跳过表格头和尾信息

  for tr in trsList:
    tr = re.compile("</?(.*?)>").sub("", tr) # 去除 html 标签
    tr = re.compile(" |\t").sub("", tr) # 去除空格
    tds = tr.split()
    # {
    #   "stu_num": tds[1],
    #   "name": tds[2],
    #   "sex": tds[3],
    #   "major": tds[4][:-2],
    #   "stu_class": tds[4][-2:]
    # }
    # 根据学号从数据库中查询是否已存在，不存在则添加
    stuObj = Student.objects.filter(stu_num=tds[1])
    if len(stuObj) == 0:
      stuObj = Student(stu_num=tds[1], name=tds[2], sex=tds[3], major=tds[4][:-2], stu_class=int(tds[4][-2:]))
      stuObj.save()
    else:
      stuObj = stuObj[0]

    mapObj = StudentCourseMap.objects.filter(term=termNum, student=stuObj, course=courseObj)
    if len(mapObj) == 0:
      mapObj = StudentCourseMap(term=termNum, student=stuObj, course=courseObj)
      mapObj.save()

def main():
  # 访问coursesListBaseUrl获取cookie
  req.get(coursesListBaseUrl, params={"xqh": termNum})
  collegeList = resolveCollegeList()

  for college in collegeList:
    getCourseList(college.strip())

if __name__ == '__main__':
  main()