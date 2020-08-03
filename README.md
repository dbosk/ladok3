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
    # testenvironment_flag  - set to True to run in the Ladok test environment, by default it is False
   
    def __init__(self, username, password, testenvironment_flag = False):
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

### get_student_data_JSON
```python
    #####################################################################
    #
    # get_student_data_JSON
    #
    # person_nr           - personnummer, flera format accepteras enligt regex:
    #                       (\d\d)?(\d\d)(\d\d\d\d)[+\-]?(\w\w\w\w)
    #
    # RETURNERAR JSON of the request for studentinformation/student
    def get_student_data_JSON(self, person_nr_raw, lang = 'sv'):
```
### logout
```python
    #####################################################################
    #
    # logout
    #                        Terminate the Ladok session
    #
    # RETURNERAR response to the request
    #
    # Example:     status=ladok_session.logout()
    def logout(self):
```

### all_grading_scale
```python
    #####################################################################
    #
    # all_grading_scale
    #
    #
    # RETURNERAR en dictionary of the grading scales
    def all_grading_scale(self):
```
### grading_rights
```python
    #####################################################################
    #
    # grading_rights
    #
    #
    # RETURNERAR en dictionary of the grading rights (of the logged in user)
    def grading_rights(self):
```
### change_local
```python
    #####################################################################
    #
    # change_locale
    #
    # lang               - language code 'en' or 'sv', defaults to 'sv'
    #
    # RETURNERAR reponse to the request
    #
    # Example:     status=ladok_session.change_locale('en')
    def change_locale(self, lang = 'sv'):
```
### course_instances_JSON

```python
    #####################################################################
    #
    # course_instances_JSON
    #
    # course_code        - course code, such as "II2202"
    #
    # lang               - language code 'en' or 'sv', defaults to 'sv'
    #
    # RETURNERAR JSON of resultat/kurstillfalle
    #
    # Example: ladok_session.course_instances_JSON('II2202', 'en')
    def course_instances_JSON(self, course_code, lang = 'sv'):
```
### organization_info_JSON
```python
    #####################################################################
    #
    # organization_info_JSON
    #
    # RETURNERAR JSON of resultat/organisation/utanlankar for the entire institution of the logged in user
    def organization_info_JSON(self):
```

### period_info_JSON
```python
    #####################################################################
    #
    # period_info_JSON
    #
    # RETURNERAR JSON of /resultat/grunddata/period
    def period_info_JSON(self):
```
### instance_info
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
    #
    # Example: info=ladok_session.instance_info('II2202', instance_code, 'en')
    def instance_info(self, course_code, instance_code, lang = 'sv'):
```
### course_instance_JSON
```python
    #####################################################################
    #
    # course_instance_JSON
    #
    # uid                -  uid of c course instance
    #
    # RETURNERAR JSON of resultat/utbildningsinstans/kursinstans
    #
    # Example: kurs=ladok_session.course_instance_JSON(ii['Utbildningsinstans']['Uid']
    def course_instance_JSON(self, uid):
```
### participants_JSON
```python
    #####################################################################
    #
    # participants
    #
    # uid                -  uid of c course instance
    #
    # RETURNERAR JSON of participants in a given course instance
    # 
    # Example:         instance_code='50287'
    #                  ii=ladok_session.instance_info('II2202', instance_code, 'en')
    #                  pl=ladok_session.participants(ii['Uid'])
    def participants_JSON(self, uid):
```
### studystructure_student_JSON
```python
    #####################################################################
    #
    # studystructure_student_JSON
    #
    # uid                -  uid of a student
    #
    # RETURNERAR en dictionary of student information
    def studystructure_student_JSON(self, uid):
```
### undervisningssprak_JSON
```python
    #####################################################################
    #
    # undervisningssprak
    #
    # RETURNERAR en dictionary of languages used for instruction
    def undervisningssprak_JSON(self):
```
### i18n_translation_JSON
```python
    #####################################################################
    #
    # i18n_translation_JSON
    #
    # lang               - language code 'en' or 'sv', defaults to 'sv'
    # RETURNERAR JSON of i18n translations used in Ladok3
    def i18n_translation_JSON(self, lang = 'sv'):
```
Example use is:
```python
    translation_table_English=dict()
    for i in translations_English['Oversattningar']:
        translation_table_English[i['I18nNyckel']]=i['Text']

    translation_table_Swedish=dict()
    for i in translations_Swedish['Oversattningar']:
        translation_table_Swedish[i['I18nNyckel']]=i['Text']

    translations_table=[]
    for i in translations_English['Oversattningar']:
        translations_table.append({'key': i['I18nNyckel'],
                                  'en': translation_table_English[i['I18nNyckel']],
                                  'sv': translation_table_Swedish[i['I18nNyckel']]})

    translations_df=pd.json_normalize(translations_table)

    output_file="ladoki18n-translations"
    write_xlsx(output_file, translations_df, 'i18n')
```
### svenskort_JSON
```python
    #####################################################################
    #
    # svenskort_JSON
    #
    # RETURNERAR JSON of places in Sweden with their KommunID
    def svenskort_JSON(self):
```

### kommuner_JSON
```python
    #####################################################################
    #
    # kommuner_JSON
    #
    # RETURNERAR JSON of Kommun in Sweden
    def kommuner_JSON(self):
```

### lander_JSON
```python
    #####################################################################
    #
    # lander_JSON
    #
    # RETURNERAR JSON of countries
    def lander_JSON(self):
```
### undervisningstid_JSON
```python
    #####################################################################
    #
    # undervisningstid_JSON
    #
    # RETURNERAR JSON of teaching times
    def undervisningstid_JSON(self):
```

### successivfordjupning_JSON
```python
    #####################################################################
    #
    # successivfordjupning_JSON
    #
    # RETURNERAR JSON of Successive Specializations
    def successivfordjupning_JSON(self):
```

### undervisningsform_JSON
```python
    #####################################################################
    #
    # undervisningsform_JSON
    #
    # RETURNERAR JSON of forms of education
    def undervisningsform_JSON(self):
```

### LokalaPerioder_JSON
```python
    #####################################################################
    #
    # LokalaPerioder_JSON
    #
    # RETURNERAR JSON of local periods
    def LokalaPerioder_JSON(self):
```

### nivainomstudieordning_JSON
```python
    #####################################################################
    #
    # nivainomstudieordning_JSON
    #
    # RETURNERAR JSON of education levels
    def nivainomstudieordning_JSON(self):
```

### amnesgrupp_JSON
```python
    #####################################################################
    #
    # amnesgrupp_JSON
    #
    # RETURNERAR JSON of subject area groups
    def amnesgrupp_JSON(self):
```
### studietakt_JSON
```python
    #####################################################################
    #
    # studietakt_JSON
    #
    # RETURNERAR JSON of study tempos
    def studietakt_JSON(self):
```
### finansieringsform_JSON
```python
    #####################################################################
    #
    # finansieringsform_JSON
    #
    # RETURNERAR JSON forms of financing
    def finansieringsform_JSON(self):
```
### utbildningsomrade_JSON
```python
    #####################################################################
    #
    # utbildningsomrade_JSON
    #
    # RETURNERAR JSON of subjects
    def utbildningsomrade_JSON(self):
```
### kravpatidigarestudier_JSON
```python
    #####################################################################
    #
    # kravpatidigarestudier_JSON
    #
    # RETURNERAR JSON of krequirements for earlier studies
    def kravpatidigarestudier_JSON(self):
```
### studieordning_JSON
```python
    #####################################################################
    #
    # studieordning_JSON
    #
    # RETURNERAR JSON of study regulation
    def studieordning_JSON(self):
```
### organisation_by_uid_JSON
```python
    #####################################################################
    #
    # organisation_by_uid_JSON
    #
    # organisationUid           -- organization's UID
    #
    # RETURNERAR JSON of selected organization
    def organisation_by_uid_JSON(self, organisationUid):
```
### utbildningstyp_JSON
```python
    #####################################################################
    #
    # utbildningstyp_JSON
    #
    # RETURNERAR JSON of types of education
    def utbildningstyp_JSON(self):
```

### aktivitetstillfallestyp_JSON
```python
    #####################################################################
    #
    # aktivitetstillfallestyp_JSON
    #
    # RETURNERAR JSON of activities
    def aktivitetstillfallestyp_JSON(self):
```
### catalog_service_index__JSON
```python
    #####################################################################
    #
    # catalog_service_index__JSON
    #
    # RETURNERAR JSON of admission round
    def catalog_service_index__JSON(self):
```
### omradesbehorighet_JSON
```python
    #####################################################################
    #
    # omradesbehorighet_JSON
    #
    # RETURNERAR JSON of "omradesbehorighet"
    def omradesbehorighet_JSON(self):
```


### canvas_ladok3_spreadsheet.py

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
### ladok3_course_instance_to_spreadsheet.py

Purpose: Use the data in Ladok3 together with the data from Canvas to create a spreadsheet of students in a course
instance and include their Canvas user_id (or "not in Canvas" if they do not have a Canvas user_id), name, Ladok3 Uid, program_code, program name, etc.

Input: 
```
ladok3_course_instance_to_spreadsheet.py course_code course_instance
```
Optionally include their personnumber with the flag -p or --personnumbers 

Add the "-T" flag to run in the Ladok test environment.

Output: outputs a file ('users_programs-instance-COURSE_INSTANCE.xlsx) containing a spreadsheet of the users information

```
# for the P1 instance in 2019 the course instance is 50287
ladok3_course_instance_to_spreadsheet.py II2202 50287
```

### canvas_students_missing_integration_ids.py

Purpose: Use the data in a Canvas course room to create a spreadsheet of students in the course who are missing an integration ID.

Input: 
```
canvas_students_missing_integration_ids.py canvas_course_id
```

Output: outputs a file ('users_without_integration_ids-COURSE_ID.xlsx) containing a spreadsheet of the users information


### cl_user_info.py

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


