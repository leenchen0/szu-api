# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Course(models.Model):
  course_num = models.CharField(max_length=100)
  course_name = models.CharField(max_length=100)
  teacher = models.CharField(max_length=100)
  class_week = models.CharField(max_length=20)
  class_time = models.CharField(max_length=100)
  venue = models.CharField(max_length=100)

  def __unicode__(self):
    return self.course_name

class Student(models.Model):
  stu_num = models.CharField(max_length=20)
  name = models.CharField(max_length=50)
  sex = models.CharField(max_length=10)
  major = models.CharField(max_length=100)
  stu_class = models.IntegerField()

  def __unicode__(self):
    return self.name

class StudentCourseMap(models.Model):
  term = models.CharField(max_length=15)
  student = models.ForeignKey(Student)
  course = models.ForeignKey(Course)