#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
import ladok3
import os

ladok = ladok3.LadokSession("KTH",
                            vars={"username": os.environ["KTH_LOGIN"],
                                  "password": os.environ["KTH_PASSWD"]},
                            test_environment=True) # for experiments

course_rounds = ladok.search_course_rounds(code="DD1315")

for course_round in course_rounds:
    print(f"{course_round.code} {course_round.start}--{course_round.end}")
print()

course_round = course_rounds[0]
print(f"{course_round.code} {course_round.start}--{course_round.end}")
print(f"round: {course_round.round_id}")
print(f"round code: {course_round.round_code}")
print(f"instance: {course_round.instance_id}")
print(f"education: {course_round.education_id}")
print(f"{course_round.code} components:")
for component in course_round.components():
    print(f"{component.code}: {component.instance_id}")
