# -*- coding: utf-8 -*-
import re, html, datetime, urllib.parse, json

try:
    import requests
except ImportError as e:
    print("""
Python-paketet requests behöver installeras för att nå ladok
> pip3 install requests
""")
    print(e)
    sys.exit()

base_url = 'https://www.start.ladok.se/gui/proxy'

##############################################################
#
# LadokSession
#
# Det här är ett gränssnitt för att läsa och skriva resultat
# till ladok 3. Det består av:
#
# __init__         konstruktor som loggar in och hämtar grunddata
# get_results      returnerar en dictionary med momentnamn och resultat
# save_result      sparar resultat för en student som utkast
#
# The original LadokSession code is from Alexander Baltatzis <alba@kth.se> on 2020-07-20
# I (Gerald Q. Maguire Jr.) have extended on 2020-07-21 and later with the code as noted below.
class LadokSession():

    #####################################################################
    #
    # init
    #
    # username          - ditt loginid t.ex. alba
    # password          - lösenord
    
    def __init__(self, username, password):
        self.signed_in = False
        self.__session = None
        self.__headers = { 'Accept' : 'application/vnd.ladok-resultat+json, application/vnd.ladok-kataloginformation+json, application/vnd.ladok-studentinformation+json, application/vnd.ladok-studiedeltagande+json, application/vnd.ladok-utbildningsinformation+json, application/vnd.ladok-examen+json, application/vnd.ladok-extintegration+json, application/vnd.ladok-uppfoljning+json, application/vnd.ladok-extra+json, application/json, text/plain' }
        self.__grade_scales = []
        self.__grade_by_id = {}
        s = requests.session()
        
        r = s.get(url = 'https://www.start.ladok.se/gui/loggain')
        r = s.get(url = 'https://www.start.ladok.se/gui/shiblogin')
        
        shibstate = re.search('return=(.*?)(&|$)', r.url).group(1)
        url = urllib.parse.unquote(shibstate)
        
        r = s.get(url = url + '&entityID=https://saml.sys.kth.se/idp/shibboleth')
        
        post_data = {
            'shib_idp_ls_exception.shib_idp_session_ss': '',
            'shib_idp_ls_success.shib_idp_session_ss': 'true',
            'shib_idp_ls_value.shib_idp_session_ss': '',
            'shib_idp_ls_exception.shib_idp_persistent_ss': '',
            'shib_idp_ls_success.shib_idp_persistent_ss': 'true',
            'shib_idp_ls_value.shib_idp_persistent_ss': '',
            'shib_idp_ls_supported': 'true',
            '_eventId_proceed': ''
        }
        
        r = s.post(url = 'https://saml-5.sys.kth.se/idp/profile/SAML2/Redirect/SSO?execution=e1s1', data = post_data)
        
        action = re.search('<form id="fm1" action="(.*?)" method="post">', r.text).group(1)
        lt = re.search('<input type="hidden" name="lt" value="(.*?)" />', r.text).group(1)
        execution = re.search('<input type="hidden" name="execution" value="(.*?)" />', r.text).group(1)
        
        post_data = {
            'username': username,
            'password': password,
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit',
            'subimt': 'Logga in'
        }
        
        r = s.post(url = 'https://login.kth.se' + action, data = post_data)
        
        action = re.search('<form action="(.*?)" method="post">', r.text)
        if action is None: raise Exception('Invalid username or password.')
        action = html.unescape(action.group(1))
        
        relay_state = re.search('<input type="hidden" name="RelayState" value="([^"]+)"\/>', r.text)
        relay_state = html.unescape(relay_state.group(1))
        
        saml_response = re.search('<input type="hidden" name="SAMLResponse" value="(.*?)"/>', r.text)
        saml_response = html.unescape(saml_response.group(1))
        
        post_data = {
            'RelayState': relay_state,
            'SAMLResponse': saml_response
        }
        
        r = s.post(url = action, data = post_data)
        
        if 'Din användare finns inte i Ladok' in r.text: raise Exception('Signed in successfully, but not as a teacher.')

        r = s.get(url = base_url + '/resultat/grunddata/betygsskala', headers = self.__headers)
        
        for grade_scale in r.json()['Betygsskala']:
            self.__grade_scales.append({
                'id': int(grade_scale['ID']),
                'code': grade_scale['Kod'],
                'name': grade_scale['Benamning']['sv'],
                'grades': [{
                    'id': int(grade['ID']),
                    'code': grade['Kod'],
                    'accepted': grade['GiltigSomSlutbetyg']
                } for grade in grade_scale['Betygsgrad']]
            })
        
        for grade_scale in self.__grade_scales:
            for grade in grade_scale['grades']:
                self.__grade_by_id[grade['id']] = {
                    'grade_scale': grade_scale,
                    'grade': grade
                }
        
        self.signed_in = True
        self.__session = s
        

    #####################################################################
    #
    # get_results
    #
    # person_nr          - personnummer, siffror i strängformat
    #            t.ex. 19461212-1212
    # course_code          - kurskod t.ex. DD1321
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
        if not self.signed_in: raise Exception('Not signed in.')

        person_nr_raw = str(person_nr_raw)
        person_nr =  self.__validate_person_nr(person_nr_raw)
        if not person_nr: raise Exception('Invalid person nr ' + person_nr_raw)
        
        student_data = self.__get_student_data(person_nr)

        student_course = next(x for x in self.__get_student_courses(student_data['id']) if x['code'] == course_code)

        # get attested results
        r = self.__session.get(url = base_url + '/resultat/studentresultat/attesterade/student/' + student_data['id'], headers = self.__headers).json()
        
        results_attested_current_course = None
        results = {}  # return value
        
        for course in r['StudentresultatPerKurs']:
            if course['KursUID'] == student_course['education_id']:
                results_attested_current_course = course['Studentresultat']
                break


        if results_attested_current_course:
            for result in results_attested_current_course:
                try:
                    d = { 'grade' : result['Betygsgradskod'],
                          'status': 'attested',
                          'date'  : result['Examinationsdatum'] }
                    results[ result['Utbildningskod'] ] = d
                except:
                    pass  # tillgodoräknanden har inga betyg och då är result['Utbildningskod'] == None

        # get pending results
        r = self.__session.get(url = base_url + '/resultat/resultat/resultat/student/' + student_data['id'] + '/kurs/' + student_course['education_id'] + '?resultatstatus=UTKAST&resultatstatus=KLARMARKERAT', headers = self.__headers).json()
        
        for result in r['Resultat']:
            r = self.__session.get(url = base_url + '/resultat/utbildningsinstans/' + result['UtbildningsinstansUID'], headers = self.__headers).json()
            d_grade     = result['Betygsgradsobjekt']['Kod']
            d_status = "pending(" + str(result['ProcessStatus']) + ")"
            # utkast har inte datum tydligen ...
            d_date     = "0" if 'Examinationsdatum' not in result else result['Examinationsdatum'] 
            d = { 'grade' : d_grade ,
                  'status': d_status,
                  'date'  : d_date      } 
            results[ r['Utbildningskod'] ] = d
        return results

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
        if not self.signed_in: raise Exception('Not signed in.')
        
        if grade_raw in ["AF", "PF"]:
            raise Exception('Invalid grade: ' + grade_raw + ' looks like a grade_scale') 

        if (grade_raw == 'P' and grade_scale == "AF") or (grade_raw in "ABCDE" and grade_scale == "PF"):
            raise Exception('Invalid grade: ' + grade_raw + ' does not match grade_scale ' + grade_scale) 
        
        person_nr =  self.__validate_person_nr(person_nr_raw)
        if not person_nr: raise Exception('Invalid person nr ' + person_nr_raw)
        
        result_date = self.__validate_date(result_date_raw)
        if not result_date : raise Exception('Invalid grade date: ' + result_date_raw + ' pnr: ' +  person_nr_raw + ' moment: ' + course_moment)
        
        student_data = self.__get_student_data(person_nr)
        student_course = next(x for x in self.__get_student_courses(student_data['id']) if x['code'] == course_code)
        
        # momentkod = kurskod => vi hanterar kursbetyg
        if course_moment == student_course['code']:
            course_moment_id = student_course['instance_id']
        else:
            #course_moment_id = next(x['course_moment_id'] for x in self.__get_student_course_moments(student_course['round_id'], student_data['id']) if x['code'] == course_moment)
            for x in self.__get_student_course_moments(student_course['round_id'], student_data['id']):
                if x['code'] == course_moment:
                    course_moment_id = x['course_moment_id']
            
        student_course_results = self.__get_student_course_results(student_course['round_id'], student_data['id'])
        
        grade_scale = self.__get_grade_scale_by_code(grade_scale)
        grade = next(grade for grade in grade_scale['grades'] if grade['code'] == grade_raw)
                    
        headers = self.__headers.copy()
        headers['Content-Type'] = 'application/vnd.ladok-resultat+json'
        headers['X-XSRF-TOKEN'] = self.__get_xsrf_token()
        headers['Referer'] = 'https://www.start.ladok.se/gui/'
        
        previous_result = None
        
        for result in student_course_results['results']:
            if result['pending'] is not None:
                if result['pending']['moment_id'] == course_moment_id:
                    previous_result = result['pending']
                    break
        
        # uppdatera befintligt utkast
        if previous_result:
            put_data = {
                'Resultat': [{
                    'ResultatUID': previous_result['id'],
                    'Betygsgrad': grade['id'],
                    'Noteringar': [],
                    'BetygsskalaID': grade_scale['id'],
                    'Examinationsdatum': result_date,
                    'SenasteResultatandring': previous_result['last_modified']
                }]
            }
            
            r = self.__session.put(url = base_url + '/resultat/studieresultat/uppdatera', json = put_data, headers = headers)
        
        # lägg in nytt betygsutkast
        else:
            post_data = {
                'Resultat': [{
                    'StudieresultatUID': student_course_results['id'],
                    'UtbildningsinstansUID': course_moment_id,
                    'Betygsgrad': grade['id'],
                    'Noteringar': [],
                    'BetygsskalaID': grade_scale['id'],
                    'Examinationsdatum': result_date
                }]
            }
            r = self.__session.post(url = base_url + '/resultat/studieresultat/skapa', json = post_data, headers = headers)
        
        if not 'Resultat' in r.json(): raise Exception("Kunde inte mata in " + person_nr_raw + " " + course_moment + " : " + grade_raw + " " + result_date_raw + "\n" + r.text)
        
        return True


    #####################################################################
    #
    # get_student_data
    #
    # person_nr           - personnummer, flera format accepteras enligt regex:
    #                       (\d\d)?(\d\d)(\d\d\d\d)[+\-]?(\w\w\w\w)
    #
    # RETURNERAR {'id': 'xxxx', 'first_name': 'x', 'last_name': 'y', 'person_nr': 'xxx', 'alive': True}

    def get_student_data(self, person_nr_raw):
        if not self.signed_in: raise Exception('Not signed in.')
        person_nr =  self.__validate_person_nr(person_nr_raw)
        
        if not person_nr: raise Exception('Invalid person nr ' + person_nr_raw)
        
        student_data = self.__get_student_data(person_nr)
        return student_data

    #####################################################################
    #
    # get_student_name
    #
    # person_nr          - personnummer, flera format accepteras enligt regex:
    #                      (\d\d)?(\d\d)(\d\d\d\d)[+\-]?(\w\w\w\w)
    #
    # RETURNERAR en dictionary med för- och efternamn
    #
    # {"first_name" : 'Anna', "last_name : 'Andersson'}
    #
    def get_student_name(self, person_nr_raw):
        if not self.signed_in: raise Exception('Not signed in.')
        person_nr =  self.__validate_person_nr(person_nr_raw)
        
        if not person_nr: raise Exception('Invalid person nr ' + person_nr_raw)
        
        student_data = self.__get_student_data(person_nr)
        return { "first_name": student_data["first_name"], "last_name" : student_data["last_name"] }


    # added by GQMJr
    #####################################################################
    #
    # get_student_data_JSON
    #
    # person_nr          - personnummer, flera format accepteras enligt regex:
    #                      (\d\d)?(\d\d)(\d\d\d\d)[+\-]?(\w\w\w\w)
    #
    # lang               - language code 'en' or 'sv', defaults to 'sv'
    #
    # RETURNERAR en dictionary med för- och efternamn and more
    def get_student_data_JSON(self, person_nr_raw, lang = 'sv'):
        if not self.signed: raise Exception('Not signed in.')
        person_nr =  self.__validate_person_nr(person_nr_raw)
        
        if not person_nr: raise Exception('Invalid person nr ' + person_nr_raw)

        r = self.__session.get(url = base_url + '/studentinformation/student/filtrera?limit=2&orderby=EFTERNAMN_ASC&orderby=FORNAMN_ASC&orderby=PERSONNUMMER_ASC&page=1&personnummer=' + person_nr + '&skipCount=false&sprakkod='+lang, headers = self.__headers).json()
        
        return r

    # added by GQMJr
    #####################################################################
    #
    # logout
    #                        Terminate the Ladok session
    #
    # RETURNERAR response to the request
    #
    # Example:     status=ladok_session.logout()
    def logout(self):
        if not self.signed_in: raise Exception('Not signed in.')
        r = self.__session.get(url = base_url + '/logout', headers = self.__headers)

        if r.status_code == 200:
            # successfully logged out
            self.__session.close()
            self.signed_in = False
            self.__session = None
        return r


    # added by GQMJr
    #####################################################################
    #
    # all_grading_scale
    #
    #
    # RETURNERAR en dictionary of the grading scales
    def all_grading_scale(self):
        # for grade_scale in self.__grade_scales:
        #     print("grade_scale={}".format(grade_scale))
        return self.__grade_scales


    # added by GQMJr
    #####################################################################
    #
    # grading_rights
    #
    #
    # RETURNERAR en dictionary of the grading rights (of the logged in user)
    def grading_rights(self):
        if not self.signed_in: raise Exception('Not signed in.')
        r = self.__session.get(url = base_url + '/resultat/resultatrattighet/listaforinloggadanvandare', headers = self.__headers).json()
        return r['Resultatrattighet']
        

    # added by GQMJr
    #####################################################################
    #
    # change_locale
    #
    # lang               - language code 'en' or 'sv', defaults to 'sv'
    #
    # RETURNERAR reponse to the request
    def change_locale(self, lang = 'sv'):
        if not self.signed_in: raise Exception('Not signed in.')
        r = self.__session.get(url = 'https://www.start.ladok.se/gui/services/i18n/changeLocale?lang='+lang, headers = self.__headers).json()
        return r

    # added by GQMJr
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
    # Example: ladok_session.course_instances('II2202', 'en')
    def course_instances(self, course_code, lang = 'sv'):
        if not self.signed_in: raise Exception('Not signed in.')
        # note that there seems to be a limit of 403 for the number of pages
        r = self.__session.get(url = base_url + '/resultat/kurstillfalle/filtrera?kurskod='+course_code+'&page=1&limit=100&skipCount=false&sprakkod='+lang, headers = self.__headers).json()
        return r

    # added by GQMJr
    #####################################################################
    #
    # organization_info_JSON
    #
    # RETURNERAR en dictionary of organization information for the entire institution of the logged in user
    def organization_info(self):
        if not self.signed_in: raise Exception('Not signed in.')
        r = self.__session.get(url = base_url + '/resultat/organisation/utanlankar', headers = self.__headers).json()
        return r

    # added by GQMJr
    #####################################################################
    #
    # period_info_JSON
    #
    # RETURNERAR JSON of /resultat/grunddata/period
    def period_info(self):
        if not self.signed_in: raise Exception('Not signed in.')
        r = self.__session.get(url = base_url + '/resultat/grunddata/period', headers = self.__headers).json()
        return r

    # added by GQMJr
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
    # Example: ii=ladok_session.instance_info('II2202', instance_code, 'en')
    def instance_info(self, course_code, instance_code, lang = 'sv'):
        if not self.signed_in: raise Exception('Not signed in.')
        r = self.__session.get(url = base_url + '/resultat/kurstillfalle/filtrera?kurskod='+course_code+'&page=1&limit=25&skipCount=false&sprakkod='+lang, headers = self.__headers).json()
        for course in r['Resultat']:
            if course['TillfallesKod'] == instance_code:
                return course
        return r


    # added by GQMJr
    #####################################################################
    #
    # course_instance_JSON
    #
    # uid                -  uid of c course instance
    #
    # RETURNERAR JSON of resultat/utbildningsinstans/kursinstans
    #
    # Example: kurs=ladok_session.course_instance_JSON(ii['Utbildningsinstans']['Uid'])
    def course_instance(self, uid):
        if not self.signed_in: raise Exception('Not signed in.')
        r = self.__session.get(url = base_url + '/resultat/utbildningsinstans/kursinstans/'+uid, headers = self.__headers).json()
        return r

    # added by GQMJr
    #####################################################################
    #
    # participants_JSON
    #
    # uid                -  uid of c course instance
    #
    # RETURNERAR JSON of participants in a given course instance
    #
    # Example:         instance_code='50287'
    #                  ii=ladok_session.instance_info('II2202', instance_code, 'en')
    #                  pl=ladok_session.participants(ii['Uid'])
    def participants_JSON(self, uid):
        if not self.signed_in: raise Exception('Not signed in.')
        headers = self.__headers.copy()
        headers['Content-Type'] = 'application/vnd.ladok-studiedeltagande+json'
        headers['X-XSRF-TOKEN'] = self.__get_xsrf_token()
        headers['Origin'] = 'https://www.start.ladok.se'

        put_data = {'page': 1,
                    'limit': 400,
                    'orderby': ['EFTERNAMN_ASC',
                                'FORNAMN_ASC',
                                'PERSONNUMMER_ASC',
                                'KONTROLLERAD_KURS_ASC'],
                    'deltagaretillstand': ['EJ_PABORJAD', # include students how have not yet started the course
                                           'REGISTRERAD', # include registered students
                                           'AVKLARAD'], # include students who have completed the course
                    'utbildningstillfalleUID': [uid]
        }
            
        # the constants above come from schemas.ladok.se-studiedeltagande.xsd
        #
        # <xs:simpleType name="DeltagareKurstillfalleOrderByEnum">
        #   <xs:restriction base="xs:string">
        #     <xs:enumeration value="EFTERNAMN_DESC"/>
        #     <xs:enumeration value="PERSONNUMMER_DESC"/>
        #     <xs:enumeration value="PERSONNUMMER_ASC"/>
        #     <xs:enumeration value="EFTERNAMN_ASC"/>
        #     <xs:enumeration value="FORNAMN_DESC"/>
        #     <xs:enumeration value="FORNAMN_ASC"/>
        #   </xs:restriction>
        # </xs:simpleType>
        #
        # or perhaps it comes from:
        #
        # <xs:simpleType name="DeltagareKurspaketeringstillfalleOrderByEnum">
        #   <xs:restriction base="xs:string">
        #     <xs:enumeration value="EFTERNAMN_ASC"/>
        #     <xs:enumeration value="EFTERNAMN_DESC"/>
        #     <xs:enumeration value="PERIOD_I_ORDNING_DESC"/>
        #     <xs:enumeration value="KONTROLLERAD_KURS_DESC"/>
        #     <xs:enumeration value="SUMMERAD_GODKAND_OMFATTNING_DESC"/>
        #     <xs:enumeration value="PERSONNUMMER_ASC"/>
        #     <xs:enumeration value="FORNAMN_ASC"/>
        #     <xs:enumeration value="KONTROLLERAD_KURS_ASC"/>
        #     <xs:enumeration value="SUMMERAD_GODKAND_OMFATTNING_ASC"/>
        #     <xs:enumeration value="FORNAMN_DESC"/>
        #     <xs:enumeration value="PERIOD_I_ORDNING_ASC"/>
        #     <xs:enumeration value="PERSONNUMMER_DESC"/>
        #   </xs:restriction>
        # </xs:simpleType>

        # <xs:simpleType name="DeltagaretillstandEnum">
        #   <xs:restriction base="xs:string">
        #     <xs:enumeration value="EJ_PAGAENDE_TILLFALLESBYTE"/>
        #     <xs:enumeration value="EJ_PABORJAD"/>
        #     <xs:enumeration value="AVKLARAD"/>
        #     <xs:enumeration value="ATERBUD"/>
        #     <xs:enumeration value="AVBROTT"/>
        #     <xs:enumeration value="PAGAENDE_MED_SPARR"/>
        #     <xs:enumeration value="PAGAENDE"/>
        #     <xs:enumeration value="PABORJAD"/>
        #     <xs:enumeration value="FORVANTAD_DELTAGARE"/>
        #     <xs:enumeration value="REGISTRERAD"/>
        #     <xs:enumeration value="UPPEHALL"/>
        #   </xs:restriction>
        # </xs:simpleType>


        txt=json.dumps(put_data)
        #print("txt={}".format(txt))
        # note that I could not use json = put_data, as this changed the 'Content-Type' and broke the functionality
        # For thie reason, I manually do the conversion of the JSON to a string and manually set the 'Content-Type'.
        r = self.__session.put(url = base_url + '/studiedeltagande/deltagare/kurstillfalle', data = txt, headers = headers)
        if r.status_code == 200:
            participant_info=json.loads(r.text)
            return participant_info
        return r


    # added by GQMJr
    #####################################################################
    #
    # studystructure_student_JSON
    #
    # uid                -  uid of a student
    #
    # RETURNERAR en dictionary of student information
    def studystructure_student_JSON(self, uid):
        if not self.signed_in: raise Exception('Not signed in.')
        r = self.__session.get(url = base_url + '/studiedeltagande/studiestruktur/student/'+uid, headers = self.__headers).json()
        return r

#################################################################
##
## private methods
##
    
    
    def __get_xsrf_token(self):
        cookies = self.__session.cookies.get_dict()
        return next(cookies[cookie] for cookie in cookies if cookie == 'XSRF-TOKEN')
    
    # returns None or a LADOK-formated person nr 
    def __validate_person_nr(self, person_nr_raw):
        pnrregex = re.compile("(\d\d)?(\d\d)(\d\d\d\d)[+\-]?(\w\w\w\w)")
        pnr = pnrregex.match(person_nr_raw)
        if pnr:
            now = datetime.datetime.now()
            if pnr.group(1) == None: # first digits 19 or 20 missing
                if now.year - 2000 >= int(pnr.group(2)) + 5: # must be > 5 years old
                    return "20" + pnr.group(2) + pnr.group(3) + pnr.group(4)
                else:
                    return "19" + pnr.group(2) + pnr.group(3) + pnr.group(4)
            else:
                return pnr.group(1) + pnr.group(2) + pnr.group(3) + pnr.group(4)
        else:
            return None
    
    # returns None or a LADOK-formated date
    def __validate_date(self, date_raw):
        datregex = re.compile("(\d\d)?(\d\d)-?(\d\d)-?(\d\d)")
        dat = datregex.match(date_raw)
        if dat:
            if dat.group(1) == None: # add 20, ladok3 won't survive till 2100
                return "20" + dat.group(2) + "-" + dat.group(3) + "-" + dat.group(4) 
            else:
                return dat.group(1) + dat.group(2) + "-" + dat.group(3) + "-" + dat.group(4) 
        else:
            return None
    
    def __get_grade_scale_by_id(self, grade_scale_id):
        return next(grade_scale for grade_scale in self.__grade_scales if grade_scale['id'] == grade_scale_id)
    
    
    def __get_grade_scale_by_code(self, grade_scale_code):
        return next(grade_scale for grade_scale in self.__grade_scales if grade_scale['code'] == grade_scale_code)
    
    
    def __get_grade_by_id(self, grade_id):
        for grade_scale in self.__grade_scales:
            for grade in grade_scale['grades']:
                if grade['id'] == grade_id: return grade
        
        return None
    
    
    def __get_student_data(self, person_nr):
        r = self.__session.get(url = base_url + '/studentinformation/student/filtrera?limit=2&orderby=EFTERNAMN_ASC&orderby=FORNAMN_ASC&orderby=PERSONNUMMER_ASC&page=1&personnummer=' + person_nr + '&skipCount=false&sprakkod=sv', headers = self.__headers).json()['Resultat']
        
        if len(r) != 1: return None
        
        r = r[0]
        # from schemas/schemas.ladok.se-studentinformation.xsd
        #   <xs:complexType name="Student">
        #   <xs:complexContent>
        #     <xs:extension base="base:BaseEntitet">
        #       <xs:sequence>
        #         <xs:element name="Avliden" type="xs:boolean"/>
        #         <xs:element minOccurs="0" name="Efternamn" type="xs:string"/>
        #         <xs:element minOccurs="0" name="ExterntUID" type="xs:string"/>
        #         <xs:element name="FelVidEtableringExternt" type="xs:boolean"/>
        #         <xs:element minOccurs="0" name="Fodelsedata" type="xs:string"/>
        #         <xs:element minOccurs="0" name="Fornamn" type="xs:string"/>
        #         <xs:element minOccurs="0" name="KonID" type="xs:int"/>
        #         <xs:element minOccurs="0" name="Personnummer" type="xs:string"/>
        #         <xs:element minOccurs="0" name="Skyddsstatus" type="xs:string"/>
        #         <xs:element minOccurs="0" ref="si:UnikaIdentifierare"/>
        #       </xs:sequence>
        #     </xs:extension>
        #   </xs:complexContent>
        # </xs:complexType>

        return {
            'id': r['Uid'], # Ladok-ID
            'first_name': r['Fornamn'],
            'last_name':  r['Efternamn'],
            'person_nr':  r['Personnummer'], # tolv siffror, utan bindestreck eller plustecken
            'alive':  not r['Avliden']
        }
    
    # detta är egentligen kurstillfällen, inte kurser (ID-numret är alltså ett ID-nummer för ett kurstillfälle)
    def __get_student_courses(self, student_id):
        r = self.__session.get(url = base_url + '/studiedeltagande/tillfallesdeltagande/kurstillfallesdeltagande/student/' + student_id, headers = self.__headers).json()
        
        results = []
        
        for course in r['Tillfallesdeltaganden']:
            if not course['Nuvarande'] or 'Utbildningskod' not in course['Utbildningsinformation']: continue
            
            results.append({
                'id': course['Uid'],
                'round_id': course['Utbildningsinformation']['UtbildningstillfalleUID'], # ett Ladok-ID för kursomgången
                'education_id': course['Utbildningsinformation']['UtbildningUID'], # ett Ladok-ID för något annat som rör kursen
                'instance_id': course['Utbildningsinformation']['UtbildningsinstansUID'], # ett Ladok-ID för att rapportera in kursresultat
                'code': course['Utbildningsinformation']['Utbildningskod'], # kurskod KOPPS
                'name': course['Utbildningsinformation']['Benamning']['sv']
            })
        
        return results
    
    
    def __get_student_course_moments(self, course_round_id, student_id):
        r = self.__session.get(url = base_url + '/resultat/kurstillfalle/' + str(course_round_id) + '/student/' + str(student_id) + '/moment', headers = self.__headers).json()
        
        return [{
            'course_moment_id': moment['UtbildningsinstansUID'],
            'code': moment['Utbildningskod'],
            'education_id': moment['UtbildningUID'],
            'name': moment['Benamning']['sv']
        } for moment in r['IngaendeMoment']]
    
    
    def __get_student_course_results(self, course_round_id, student_id):
        r = self.__session.get(url = base_url + '/resultat/studieresultat/student/' + student_id + '/utbildningstillfalle/' + course_round_id, headers = self.__headers).json()
        
        return {
            'id': r['Uid'],
            'results': [{
                    'education_id': result['UtbildningUID'],
                    'pending': {
                        'id': result['Arbetsunderlag']['Uid'],
                        'moment_id': result['Arbetsunderlag']['UtbildningsinstansUID'],
                        'grade': self.__get_grade_by_id(result['Arbetsunderlag']['Betygsgrad']),
                        'date': result['Arbetsunderlag']['Examinationsdatum'],
                        'grade_scale': self.__get_grade_scale_by_id(result['Arbetsunderlag']['BetygsskalaID']),
                        # behövs vid uppdatering av betygsutkast
                        'last_modified': result['Arbetsunderlag']['SenasteResultatandring']
                    } if 'Arbetsunderlag' in result else None,
                    'attested': {
                        'id': result['SenastAttesteradeResultat']['Uid'],
                        'moment_id': result['SenastAttesteradeResultat']['UtbildningsinstansUID'],
                        'grade': self.__get_grade_by_id(result['SenastAttesteradeResultat']['Betygsgrad']),
                        'date': result['SenastAttesteradeResultat']['Examinationsdatum'],
                        'grade_scale': self.__get_grade_scale_by_id(result['SenastAttesteradeResultat']['BetygsskalaID'])
                    } if 'SenastAttesteradeResultat' in result else None
                } for result in r['ResultatPaUtbildningar']
            ]
        }
