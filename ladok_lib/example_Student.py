import ladok3

ladok = ladok3.LadokSessionKTH(
        "dbosk", "my not-secret password",
        test_environment=True) # for experiments

me = ladok.get_student("8506097891")

print(f"{me.personnummer} {me.last_name}, {me.first_name}")

for course in me.courses:
    print(course)
