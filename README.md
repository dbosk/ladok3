# ladok3: Python wrapper for LADOK3 API

This package provides a wrapper for the LADOK3 API used by 
[start.ladok.se][ladok]. This makes it easy to automate reporting grades, 
compute statistics etc.

To install, run:
```bash
pip install ladok3
```

Then it's just to import the package as usual.
```python
import ladok3

ls = ladok3.LadokSessionKTH("user", "password")

student = ls.get_student("123456-1234")

course_participation = student.courses(code="AB1234")[0]
for result in course_participation.results():
  print(f"{course_participation.code} {result.component}: "
    f"{result.grade} ({result.date})")

component_result = course_participation.results(component="LAB1")[0]
component_result.set_grade("P", "2021-03-15")
```

There are more detailed usage examples in the details documentation that can be 
round with the [releases][releases] and in the `examples` directory.

[ladok]: https://start.ladok.se
[releases]: https://github.com/dbosk/ladok3/releases


## The examples

There are some examples that can be found in the `examples` directory:

  - `example_LadokSession.py` just shows how to establish a session.
  - `example_Course.py` shows course data related examples.
  - `example_Student.py` shows student data related examples.
  - `prgi.py` shows how to transfer grades from KTH Canvas to LADOK.
  - `statsdata.py` shows how to extract data for doing statistics for a course 
    and the students' results.

We also have a few more examples described in the sections below.

### `canvas_ladok3_spreadsheet.py`

Purpose: Use the data in a Canvas course room together with the data from Ladok3 to create a spreadsheet of students in the course
and include their Canvas user_id, name, Ladok3 Uid, program_code, program name, etc.

Note that the course_id can be given as a numeric value or a string which will be matched against the courses in the user's dashboard cards. It will first match against course codes, then short name, then original names.

Input: 
```
canvas_ladok3_spreadsheet.py canvas_course_id
```
Add the "-T" flag to run in the Ladok test environment.

Output: outputs a file ('users_programs-COURSE_ID.xlsx) containing a spreadsheet of the users information

```
canvas_ladok3_spreadsheet.py 12162

canvas_ladok3_spreadsheet.py -t 'II2202 HT20-1'
```


### `ladok3_course_instance_to_spreadsheet.py`

Purpose: Use the data in Ladok3 together with the data from Canvas to create a spreadsheet of students in a course
instance and include their Canvas user_id (or "not in Canvas" if they do not have a Canvas user_id), name, Ladok3 Uid, program_code, program name, etc.

Note that the course_id can be given as a numeric value or a string which will be matched against the courses in the user's dashboard cards. It will first match against course codes, then short name, then original names.

Input: 
```
ladok3_course_instance_to_spreadsheet.py course_code course_instance
```
or
```
ladok3_course_instance_to_spreadsheet.py canvas_course_id
```
or
```
./ladok3_course_instance_to_spreadsheet.py course_code
```

Optionally include their personnumber with the flag -p or --personnumbers 

Add the "-T" flag to run in the Ladok test environment.

Output: outputs a file ('users_programs-instance-COURSE_INSTANCE.xlsx) containing a spreadsheet of the users information

```
# for II2202 the P1 instance in 2019 the course instance is 50287
ladok3_course_instance_to_spreadsheet.py II2202 50287
```
or
```
# Canvas course_id for II2202 in P1 is 20979
ladok3_course_instance_to_spreadsheet.py 20979
```
or
```
# P1P2 is a nickname on a dashboard card for II2202 duing P1 and P2
./ladok3_course_instance_to_spreadsheet.py P1P2
```


### `canvas_students_missing_integration_ids.py`

Purpose: Use the data in a Canvas course room to create a spreadsheet of students in the course who are missing an integration ID.

Input: 
```
canvas_students_missing_integration_ids.py canvas_course_id
```
Output: outputs a file ('users_without_integration_ids-COURSE_ID.xlsx) containing a spreadsheet of the users information


### `cl_user_info.py`

Purpose: Use the data in a Canvas course room together with the data from Ladok3 to find information about a user.

Input: 
```
Input 
cl_user_info.py Canvas_user_id|KTHID|Ladok_id [course_id]
```
The course_id can be a Canvas course_id **or** if you have dashboard cards, you can specific a course code, a nickname, unique part of the short name or original course name.

Add the "-k" or '--kthid' flag to get the KTHID (i.e., the 'sis_user_id) you need to specify a course_id for a course (where this user is a teacher or student) on the command line.

Add the "-T" flag to run in the Ladok test environment.

If you know the Ladok_id, i.e., the integration_id - then you do not need to specify a course_id.

The program can also take an argument in the form https://canvas.kth.se/courses/course_id/users/user_id
- this is the URL when you are on a user's page in a course.

Output:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from Canvas: sortable name, user_id, and integration_id\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if you specified a course_id, you will also get KTHID and login_id\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;from Ladok:  pnr (personnumber) and [program_code, program_name, specialization/track code, admissions info]


