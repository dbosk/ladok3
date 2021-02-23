import ladok3
import os

ladok = ladok3.LadokSessionKTH(
        os.environ["KTH_LOGIN"], os.environ["KTH_PASSWD"],
        test_environment=True) # for experiments

prgiX = ladok.get_course_rounds(code="DD1315")

for prgi in prgiX:
    print(f"{prgi.start}--{prgi.end}")
