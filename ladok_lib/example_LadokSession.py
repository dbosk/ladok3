import ladok3

ladok = ladok3.LadokSessionKTH(
        "dbosk", "my not-secret password",
        test_environment=True) # for experiments

gs = ladok.get_grade_scales()
me = ladok.get_student("8506097891")
prgi = ladok.get_course("DD1315")
