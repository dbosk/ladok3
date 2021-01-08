import ladok3

ladok = ladok3.LadokSessionKTH(
        "dbosk", "my not-secret password",
        test_environment=True) # for experiments

prgi = ladok.get_course("DD1315")
