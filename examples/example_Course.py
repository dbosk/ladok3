#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
import ladok3
import os

ladok = ladok3.LadokSessionKTH(
        os.environ["KTH_LOGIN"], os.environ["KTH_PASSWD"],
        test_environment=True) # for experiments

prgiX = ladok.search_course_rounds(code="DD1315")

for prgi in prgiX:
    print(f"{prgi.code} {prgi.start}--{prgi.end}")
print()

prgi = prgiX[0]
print(f"{prgi.code} {prgi.start}--{prgi.end}")
print(f"round: {prgi.round_id}")
print(f"round code: {prgi.round_code}")
print(f"instance: {prgi.instance_id}")
print(f"education: {prgi.education_id}")
print(f"{prgi.code} components:")
for component in prgi.components():
    print(f"{component.code}: {component.instance_id}")
