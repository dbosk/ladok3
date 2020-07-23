# ladok3

## class LadokSession

Det här är ett gränssnitt för att läsa och skriva resultat
 till ladok 3. Det består av:

* \_\_init__         konstruktor som loggar in och hämtar grunddata
* get_results      returnerar en dictionary med momentnamn och resultat
* save_result      sparar resultat för en student som utkast
* get_student_name

### \_\_init__

```python
    #####################################################################
    #
    # init
    #
    # Konstruktorn loggar in på ladok3 över https genom att härma en
    # webbläsare. 
    #
    # username            - ditt loginid t.ex. alba
    # password            - lösenord

    def __init__(self, username, password):
```

### get_results

```python
    #####################################################################
    #
    # get_results
    #
    # person_nr           - personnummer, flera format accepteras
    #                       t.ex. 19461212-1212
    # course_code         - kurskod t.ex. DD1321
    #
    # RETURNERAR en dictionary från ladok med momentnamn, resultat
    #
    # {'LABP': {'date': '2019-01-14', 'grade': 'P', 'status': 'attested'},
    #  'LABD': {'date': '2019-03-23', 'grade': 'E', 'status': 'pending(1)'},
    #  'TEN1': {'date': '2019-03-13', 'grade': 'F', 'status': 'pending(2)'}}
    #
    #  status:  kan ha följande värden vilket gissningsvis betyder: 
    #           attested   - attesterad
    #           pending(1) - utkast
    #           pending(2) - klarmarkerad
    #

    def get_results(self, person_nr_raw, course_code):
```

### save_result

```python
    #####################################################################
    #
    # save_result
    #
    # person_nr           - personnummer, flera format accepteras enligt regex:
    #                       (\d\d)?(\d\d)(\d\d\d\d)[+\-]?(\w\w\w\w)
    # course_code         - kurskod t.ex. DD1321
    # course_moment       - ladokmoment/kursbetyg t.ex. TEN1, LAB1, DD1321 (!)
    #                       om labmomententet är samma som course_code så sätts kursbetyg!
    # result_date         - betygsdatum, flera format accepteras enligt regex
    #                       (\d\d)?(\d\d)-?(\d\d)-?(\d\d)
    # grade_code          - det betyg som ska sättas
    # grade_scale         - betygsskala t.ex. AF eller PF. Möjliga betygsskalor
    #                       listas i self.__grade_scales. 
    #
    # RETURNERAR True om det gått bra, kastar (förhoppningsvis) undantag
    #            om det går dåligt. 
    
    def save_result(self, person_nr_raw, course_code, course_moment, result_date_raw, grade_raw, grade_scale):
```

### get_student_name

```python
    #####################################################################
    #
    # get_student_name
    #
    # person_nr           - personnummer, flera format accepteras enligt regex:
    #                       (\d\d)?(\d\d)(\d\d\d\d)[+\-]?(\w\w\w\w)
    #
    # RETURNERAR en dictionary med för- och efternamn
    #
    # {"first_name" : 'Anna', "last_name : 'Andersson'}
    #
    
    def get_student_name(self, person_nr_raw):
```

```python
    #####################################################################
    #
    # get_student_data_complete
    #
    # person_nr           - personnummer, flera format accepteras enligt regex:
    #                       (\d\d)?(\d\d)(\d\d\d\d)[+\-]?(\w\w\w\w)
    #
    # RETURNERAR JSON of the request for studentinformation/student
```

```python
    #####################################################################
    #
    # get_student_data_complete
    #
    # person_nr          - personnummer, flera format accepteras enligt regex:
    #                      (\d\d)?(\d\d)(\d\d\d\d)[+\-]?(\w\w\w\w)
    #
    # lang               - language code 'en' or 'sv', defaults to 'sv'
    #
    # RETURNERAR en dictionary med för- och efternamn and more
    #
    # {"first_name" : 'Anna', "last_name : 'Andersson'}
```

```python
    #####################################################################
    #
    # logout
    #                        Terminate the Ladok session
    #
    # RETURNERAR en dictionary of the request
```

```python
    #####################################################################
    #
    # all_grading_scale
    #
    #
    # RETURNERAR en dictionary of the grading scales
```

```python
    #####################################################################
    #
    # change_local
    #
    # lang               - language code 'en' or 'sv', defaults to 'sv'
    #
    # RETURNERAR en dictionary of request
```

```python
    #####################################################################
    #
    # course_instances
    #
    # course_code        - course code, such as "II2202"
    #
    # lang               - language code 'en' or 'sv', defaults to 'sv'
    #
    # RETURNERAR en dictionary of course instances
```

```python
    #####################################################################
    #
    # organization_info
    #
    # RETURNERAR en dictionary of organization information
```

```python
    #####################################################################
    #
    # period_info
    #
    # RETURNERAR en dictionary of period information
```

```python
    #####################################################################
    #
    # instance_info
    #
    # course_code        - course code, such as "II2202"
    #
    # instance_code      - instance of the course ('TillfallesKod')
    # 
    # lang               - language code 'en' or 'sv', defaults to 'sv'
    #
    # RETURNERAR en dictionary of course instance information
```
```python
    #####################################################################
    #
    # course_instance
    #
    # uid                -  uid of c course instance
    #
    # RETURNERAR en dictionary of course instance information
```
```python
    #####################################################################
    #
    # participants
    #
    # uid                -  uid of c course instance
    #
    # RETURNERAR en dictionary of participants in a given course instance
```
```python
    #####################################################################
    #
    # studystructure_student
    #
    # uid                -  uid of a student
    #
    # RETURNERAR en dictionary of student information
```

### canvas_ladok3_spreadsheet.py

Purpose: Use the data in a Canvas course room together with the data from Ladok3 to create a spreadsheet of students in the course
and include their Canvas user_id, name, Ladok3 Uid, program_code, program name, etc.


Input: 
```
canvas_ladok3_spreadsheet.py canvas_course_id
```

Output: outputs a file ('users_programs-COURSE_ID.xlsx) containing a spreadsheet of the users information

```
canvas_ladok3_spreadsheet.py 12162
```
### ladok3_course_instance_to_spreadsheet.py

Purpose: Use the data in Ladok3 together with the data from Canvas to create a spreadsheet of students in a course
instance and include their Canvas user_id (or "not in Canvas" if they do not have a Canvas user_id), name, Ladok3 Uid, program_code, program name, etc.

Optionally include their personnumber with the flag -p or --personnumbers 


Input: 
```
ladok3_course_instance_to_spreadsheet.py course_code course_instance
```

Output: outputs a file ('users_programs-COURSE_ID.xlsx) containing a spreadsheet of the users information

```
# for the P1 instance in 2019 the course instance is 50287
ladok3_course_instance_to_spreadsheet.py II2202 50287
```

