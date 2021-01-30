import ladok3
import os

ladok = ladok3.LadokSessionKTH(
        os.environ["KTH_LOGIN"], os.environ["KTH_PASSWD"],
        test_environment=True) # for experiments

me = ladok.get_student("8506097891")
me2 = ladok.get_student("de709f81-a867-11e7-8dbf-78e86dc2470c")

print(f"{me.personnummer} {me.last_name}, {me.first_name}")
print(f"{me2.personnummer} {me2.last_name}, {me2.first_name}")
print(f"{me.ladok_id} == {me2.ladok_id}")
print()

student = ladok.get_student("1234561234")
print(f"{student.personnummer} {student.first_name} {student.last_name}")

for course in student.courses(code="DD1315"):
    print(f"round_id = {course.round_id}")
    print(f"education_id = {course.education_id}")
    print(f"instance_id = {course.instance_id}")
    print(f"code = {course.code}")
    print(f"name = {course.name}")
    print("Results:")
    for result in course.results:
        result.set_grade("P", "2021-01-01")
        s = f"{course.code} {result.component} {result.grade}"
        if result.attested:
            s += f"({result.date})"
        print(s)
        print(f"component_id = {result.component_id}")
        print(f"education_id = {result.education_id}")
        print(f"grade = {result.grade} ({result.date})")
        print(f"attested = {result.attested}")
        print(result.ladok_json.keys())
