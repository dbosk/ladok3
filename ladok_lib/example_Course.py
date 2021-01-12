import ladok3
import os

ladok = ladok3.LadokSessionKTH(
        os.environ["KTH_LOGIN", os.environ["KTH_PASSWD"],
        test_environment=True) # for experiments

#prgi = ladok.get_course("DD1315")

instance = ladok3.CourseInstance(
        ladok=ladok,
        **ladok.course_instances_JSON("DD1315")["Resultat"][0])
print(instance.ladok_json["Utbildningsinstans"]["Uid"])
print(instance.ladok_json["Utbildningsinstans"]["UtbildningUID"])
print(instance.ladok_json["Utbildningsinstans"]["Utbildningskod"])
print(instance.instance_code)
print(instance.ladok_json["Utbildningsinstans"].keys())
