import ladok3.kth
import os

ladok = ladok3.kth.LadokSession(
        os.environ["KTH_LOGIN"], os.environ["KTH_PASSWD"],
        test_environment=True) # for experiments

me = ladok.get_student("8506097891")
me2 = ladok.get_student("de709f81-a867-11e7-8dbf-78e86dc2470c")

print(f"{me.personnummer} {me.last_name}, {me.first_name}")
print(f"{me2.personnummer} {me2.last_name}, {me2.first_name}")
print(f"{me.ladok_id} == {me2.ladok_id}")
print()

for course in me.courses():
    print(f"{course.code} {course.name}")

course = me.courses(code="DD2395")[0]

print(f"{course.code} results:")
for result in course.results():
    s = f"{course.code}"
    if result.component:
        s += f" {result.component}"
    s += f" {result.grade}"
    if result.attested:
        s += f" ({result.date})"
    print(s)
print()

student = ladok.get_student("1234561234")
datintro = student.courses(code="DD1301")[0]

print(f"{student.personnummer} {student.first_name} {student.last_name}")

for result in datintro.results():
    print(f"{result.component} {result.grade} ({result.date})", end="")
    if not result.attested:
        print("*")
    else:
        print()

print("Changing grades")

try:
    lab1 = datintro.results(component="LAB1")[0]
    lab1.set_grade("P", "2022-11-18")
    lab1.finalize()
except Exception as err:
    print(f"Couldn't change LAB1: {err}")

for result in datintro.results():
    print(f"{result.component} {result.grade} ({result.date})", end="")
    if not result.attested:
        print("*")
    else:
        print()

