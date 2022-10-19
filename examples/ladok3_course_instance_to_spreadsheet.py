#!/usr/bin/python3
#
# Input:
#    ./ladok3_course_instance_to_spreadsheet.py course_code course_instance
# or
#    ./ladok3_course_instance_to_spreadsheet.py canvas_course_id
#
# Examples:
#  II2202 P1 in 2019 is course instance 50287
# ./ladok3_course_instance_to_spreadsheet.py II2202 50287
#
# II2202 P1 and P1P2 in 2020
# ./ladok3_course_instance_to_spreadsheet.py II2202 51127
# ./ladok3_course_instance_to_spreadsheet.py II2202 51491
#
# As of Fall 2022
# II2202 P1P2 is Canvas course_id 34870
#    ./ladok3_course_instance_to_spreadsheet.py 34870
# from the sis_course_id the program can fin the course_round information.
#
# will produce a file: users_programs-12162.xlsx
# This file will contain the columns:
# 	canvas_user_id	user	ladok_id				program_code	program_name						track_code	admission
# 0	xxxx		xxx,yyy	xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx	INFKOMTE	Information and Communication Technology		INFKOMTE	KONV-0274B
# 1	xxxx		xxx,yyy	xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx	TEBSM		Master's Programme, Embedded Systems, 120 credits	TEBSM		E0914
# 2	xxxx		xxx,yyy	xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx	TCOMM		Track, Wireless networking				TRN		TRN2020
#...
#
# It requires a config.json file with (1) the Canvas url and access token and (2) the user's username and password (for access to Ladok)
#
# If run with the flag --testing or -t it calls a lot of the routines to test of the functionality of the various calls to get information from Ladok.
#
# If run with the flag -p or --personnumbers - it includes the personnumber of each student.
#
# Add the "-T" flag to run in the Ladok test environment.
#
#
# Adapted to work with the ladok3 python package and also adapted to the change in the shift from integration_id to sis_course_id
# 
# last modified: 2022-0819
#

import ladok3,  pprint
import requests, time
import json
import optparse
import sys
import pandas as pd

import datetime

pp = pprint.PrettyPrinter(indent=4)

global canvas_baseUrl	# the base URL used for access to Canvas
global canvas_header	# the header for all HTML requests
global canvas_payload	# place to store additionally payload when needed for options to HTML requests


def initialize(options):
    global canvas_baseUrl, canvas_header, canvas_payload

    if options.config_filename:
        config_file=options.config_filename
    else:
        config_file='config.json'
    try:
        with open(config_file) as json_data_file:
            configuration = json.load(json_data_file)

            # set up Canvas access
            canvas_access_token=configuration["canvas"]["access_token"]
            if options.containers:
                canvas_baseUrl="http://"+configuration["canvas"]["host"]+"/api/v1"
                print("using HTTP for the container environment")
            else:
                canvas_baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1"

            canvas_header = {'Authorization' : 'Bearer ' + canvas_access_token}
            canvas_payload = {}

            # set up Ladok access
            username=configuration["ladok"]["username"]
            password=configuration["ladok"].get("password", [])
    except:
        print("Unable to open configuration file named {}".format(config_file))
        print("Please create a suitable configuration file, the default name is config.json")
        sys.exit()

    if not password:
        password=getpass.getpass(prompt='Password (for Ladok access): ')
    ls=ladok3.LadokSessionKTH(username, password, options.testenvironment)
    return ls


#//////////////////////////////////////////////////////////////////////
# Canvas related routines
#//////////////////////////////////////////////////////////////////////
def users_in_course(course_id):
    users_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(canvas_baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'type': ['StudentEnrollment']
    }
    r = requests.get(url, params=extra_parameters, headers = canvas_header)
    if Verbose_Flag:
        print("result of getting enrollments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            users_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=canvas_header)
            page_response = r.json()  
            for p_response in page_response:  
                users_found_thus_far.append(p_response)

    return users_found_thus_far

def canvas_user_from_integration_id(integration_id):
    # Use the Canvas API to get the user's informatio
    #GET /api/v1/users/sis_integration_id:xxxxxxx

    url = "{0}/users/sis_integration_id:{1}".format(canvas_baseUrl,integration_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
    }
    r = requests.get(url, params=extra_parameters, headers = canvas_header)
    if Verbose_Flag:
        print("result of getting user: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        return r.json()

    return None

def teachers_in_course(course_id):
    users_found_thus_far=[]
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/courses/:course_id/enrollments

    url = "{0}/courses/{1}/enrollments".format(canvas_baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      'type': ['TeacherEnrollment']
    }
    r = requests.get(url, params=extra_parameters, headers = canvas_header)
    if Verbose_Flag:
        print("result of getting enrollments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            users_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=canvas_header)
            page_response = r.json()  
            for p_response in page_response:  
                users_found_thus_far.append(p_response)

    return users_found_thus_far

def course_info(course_id):
    # Use the Canvas API to get information for the course
    #GET /api/v1/courses/:course_id

    url = "{0}/courses/{1}".format(canvas_baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = canvas_header)
    if Verbose_Flag:
        print("result of getting course: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    return None

def list_dashboard_cards():
    cards_found_thus_far=[]
    # Use the Canvas API to get the list of dashboard cards
    #GET /api/v1/dashboard/dashboard_cards

    url = "{0}/dashboard/dashboard_cards".format(canvas_baseUrl)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = canvas_header)
    if Verbose_Flag:
        print("result of getting dashboard cards: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            cards_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of files
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links.get('next', False):
            r = requests.get(r.links['next']['url'], headers=header)  
            if Verbose_Flag:
                print("result of getting files for a paginated response: {}".format(r.text))
            page_response = r.json()  
            for p_response in page_response:  
                cards_found_thus_far.append(p_response)

    return cards_found_thus_far

#//////////////////////////////////////////////////////////////////////
# Ladok related routines
#//////////////////////////////////////////////////////////////////////
def english_name(names):
    for i in names:
        if i['Sprakkod'] == 'en':
            return i['Text']
        
def swedish_name(names):
    for i in names:
        if i['Sprakkod'] == 'sv':
            return i['Text']


def collect_study_info_from_child(child):
    bi=list()
    if Verbose_Flag:
        print("child={}".format(child))
    if len(child['Barn']) > 0:
        if Verbose_Flag:
            print("length of child is {}".format(len(child['Barn'])))
        for bb in child['Barn']:
            bi.extend(collect_study_info_from_child(bb))
    else:
        bd=dict()
        bd['program_code']=child['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningskod']
        check_for_english_program_name=child['Tillfallesdeltagande']['Utbildningsinformation']['Benamning'].get('en', False)
        if check_for_english_program_name:
            bd['program_name']=child['Tillfallesdeltagande']['Utbildningsinformation']['Benamning']['en']
        else:
            bd['program_name']=child['Tillfallesdeltagande']['Utbildningsinformation']['Benamning']['sv']
            print("*** No English program name for {}".format(bd['program_name']))

        bd['program_study_period']=child['Tillfallesdeltagande']['Utbildningsinformation']['Studieperiod']
        bd['program_session_code']=child['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningstillfalleskod']
        bd['program_type_code']=child['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningstillfallestyp']['Kod']
        bd['program_session_cancelled']=child['Tillfallesdeltagande']['Aterbud']
        bd['program_session_completed']=child['Tillfallesdeltagande']['Avklarad']

        if Verbose_Flag:
            print("bd={}".format(bd))
        bi.append(bd)
    return bi

def specialization_info(ls, student_uid):
    s1=ls.studystructure_student_JSON(student_uid)
    ss1=s1['Studiestrukturer']

    # a student who is not in a program will have s1 == {'Studiestrukturer': [], 'link': []}
    if not ss1:
        return ["Self-contained courses - no program"]


    #print("s1={}".format(s1))
    si=list()
    if len(s1['Studiestrukturer']) > 0:
        if Verbose_Flag:
            print("length of Studiestrukturer is {}".format(len(s1['Studiestrukturer'])))
        for b in s1['Studiestrukturer']: # [0]['Barn']
            si.extend(collect_study_info_from_child(b))
        return si

    return si

# def specialization_info(ls, student_uid):
#     s1=ls.studystructure_student_JSON(student_uid)
#     ss1=s1['Studiestrukturer']

#     # a student who is not in a program will have s1 == {'Studiestrukturer': [], 'link': []}
#     if not ss1:
#         return ["Self-contained courses - no program"]

#     program_code=s1['Studiestrukturer'][0]['Utbildningsinformation']['Utbildningskod']
#     print("program_code={}".format(program_code))
#     if len(s1['Studiestrukturer'][0]['Barn']) > 0:
#         sss1=s1['Studiestrukturer'][0]['Barn'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Benamning']['en']
#         sss2=s1['Studiestrukturer'][0]['Barn'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningskod']
#         sss3=s1['Studiestrukturer'][0]['Barn'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningstillfalleskod']
#         sss4=s1['Studiestrukturer'][0]['Barn'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningstillfallestyp']['Kod']
#         return [program_code, sss1, sss2, sss3, sss4]
#     else:
#         check_for_english_program_name=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Benamning'].get('en', False)
#         if check_for_english_program_name:
#             sss1=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Benamning']['en']
#         else:
#             sss1=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Benamning']['sv']
#             print("*** No English program name for {}".format(sss1))

#         sss2=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningskod']
#         sss3=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningstillfalleskod']
#         sss4=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningstillfallestyp']['Kod']
#         return [program_code, sss1, sss2, sss3, sss4]




# cleanup the session and then exit
def clean_exit(ls):
    status=ls.logout()
    sys.exit()

#//////////////////////////////////////////////////////////////////////
# utility routines
#//////////////////////////////////////////////////////////////////////
# set up the output write
def write_xlsx(file_name, df, sheet_name):
    writer = pd.ExcelWriter(file_name+'.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name)
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

def course_id_from_assetString(card):
    global Verbose_Flag

    course_id=card['assetString']
    if len(course_id) > 7:
        if course_id.startswith('course_'):
            course_id=course_id.replace('course_', "", 1)
            if Verbose_Flag:
                print("course_id_from_assetString:: course_id={}".format(course_id))
            return course_id
    else:
        print("Error missing assetString for card {}".format(card))
        return None

# check if the course_id is all digits, matches course code, or matches a short_name
def process_course_id_from_commandLine(course_id):
    if not course_id.isdigit():
        cards=list_dashboard_cards()
        for c in cards:
            # look to see if the string is a course_code
            if course_id == c['courseCode']:
                course_id=course_id_from_assetString(c)
                break
            # check for matched against shortName
            if course_id == c['shortName']:
                course_id=course_id_from_assetString(c)
                break
            # look for the string at start of the shortName
            if c['shortName'].startswith(course_id) > 0:
                course_id=course_id_from_assetString(c)
                print("picked the course {} based on the starting match".format(c['shortName']))
                break
            # look for the substring in the shortName
            if c['shortName'].find(course_id) > 0:
                course_id=course_id_from_assetString(c)
                print("picked the course {} based on partial match".format(c['shortName']))
                break

            # check for matched against originalName
            if course_id == c['originalName']:
                course_id=course_id_from_assetString(c)
                break
            # look for the string at start of the shortName
            if c['originalName'].startswith(course_id) > 0:
                course_id=course_id_from_assetString(c)
                print("picked the course {} based on the starting match".format(c['shortName']))
                break
            # look for the substring in the shortName
            if c['originalName'].find(course_id) > 0:
                course_id=course_id_from_assetString(c)
                print("picked the course {} based on partial match".format(c['shortName']))
                break

        print("processing course: {0} with course_id={1}".format(c['originalName'], course_id))
    return course_id

def remove_cancelled_programs_from_student_information(si):
    # remove the cancelled programs
    si[:]= [item for item in si if item.get('program_session_cancelled', True) == False]
    today = datetime.date.today()
    
    # remove programs that have ended, i.e., 'Slutdatum' is before today
    if len(si) > 1:             # only do this is there is more than one program, as it might be a student who is late finishing
        si[:]= [item for item in si if datetime.date.fromisoformat(item['program_study_period'].get('Slutdatum', '1900-01-01')) > today]
    
    return si



def main():
    global Verbose_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")

    parser.add_option('-C', '--containers',
                      dest="containers",
                      default=False,
                      action="store_true",
                      help="for the container enviroment in the virtual machine"
    )

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="execute test code"
    )

    parser.add_option('-p', '--personnumbers',
                      dest="pnr",
                      default=False,
                      action="store_true",
                      help="include person numbers"
    )

    parser.add_option('-T', '--testenvironment',
                      dest="testenvironment",
                      default=False,
                      action="store_true",
                      help="execute test code"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    ladok_session=initialize(options)

    course_code=None
    instance_code=None
    
    if (len(remainder) == 2):
        course_code=remainder[0]
        instance_code=remainder[1]
    elif (len(remainder) == 1):
        course_id=process_course_id_from_commandLine(remainder[0])
        if not course_id:
            print("Unable to recognize a course_id, course code, or short name for a course in {}".format(remainder[0]))
            clean_exit(ladok_session)

        # get the "sis_course_id"
        course_information=course_info(course_id)

        course_code=course_information.get('original_name', None)
        if course_code:
            course_code=course_code[:6]

        course_integration_id=course_information.get('sis_course_id', None)
        if not course_integration_id:
            print("Unable to find course_integration information for Canvas course={}".format(course_id))
            clean_exit(ladok_session)

        instance_info=ladok_session.instance_info_uid(course_integration_id)
        if instance_info:
            instance_code=instance_info['TillfallesKod']
            if Verbose_Flag:
                print("instance_code={}".format(instance_code))
        else:
            print("Insuffient arguments - must provide at least a course_code")
            clean_exit(ladok_session)

    else:
        print("Insuffient arguments - must provide course_code course_instance_id (i.e. the KOPPS Tillfällskod)\n")
        clean_exit(ladok_session)

    utbildningstyp=ladok_session.utbildningstyp_JSON()
    types_of_education=dict()
    for i in utbildningstyp['Utbildningstyp']:
        types_of_education[i['Kod']]={
            'en': i['Benamning']['en'],
            'sv': i['Benamning']['sv'],
        }
    if Verbose_Flag:
        pprint.pprint(types_of_education, indent=4)


    user_and_program_list=[]
    #ii=ladok_session.instance_info(course_code, instance_code, 'en')
    # if the enstance code was not found or there is no Uid in the result, there is an error
    if  not instance_info.get('Uid', False):
        print("It seems the instance code is not a Ladok instance ('tillfälleskod'), instance_info:")
        pp.pprint(instance_info)
        clean_exit(ladok_session)
    if Verbose_Flag:
        print("instance_info['Uid']={}".format(instance_info['Uid']))

    if Verbose_Flag:
        print("course_code={}".format(course_code))

    pl=ladok_session.participants_JSON(instance_info['Uid'], participants_types=["not_started",  "ongoing", "registered", "finished", "cancelled"])
    if Verbose_Flag:
        print("pl:")
        pp.pprint(pl)
    if not pl or len(pl) == 0:
        print("It seems there are no participants in this Ladok instance ('tillfälleskod')")
        clean_exit(ladok_session)

    
    for s in pl:
        d=dict()

        ladok_id=s['Student']['Uid']
        si=specialization_info(ladok_session, ladok_id)
        si=remove_cancelled_programs_from_student_information(si)
        canvas_user_info=canvas_user_from_integration_id(ladok_id)
        if canvas_user_info:
            d['canvas_user_id']=canvas_user_info['id']
            d['user']=canvas_user_info['sortable_name']
        else:
            d['canvas_user_id']="not in Canvas"
            d['user']=s['Student']['Efternamn']+','+s['Student']['Fornamn']
            
        d['ladok_id']=ladok_id
        if options.pnr:
            d['pnr']=s['Student']['Personnummer']

        if len(si) > 0:
            si0=si[0]
            d['program_code']=si0['program_code']
            d['program_name']=si0['program_name']
            d['Session_code']=si0['program_session_code']               # utbildningstillfälleskod
            # the type of education is associated with an application code (anmälningskod)
            d['type_ of_education']=types_of_education[si0['program_type_code']]['en']
            d['program_study_period_start']=si0['program_study_period']['Startdatum']

        if len(si) > 1:
            #print("more than one program for student: {0}, {1}".format(d['user'], si))
            for i in range(1, len(si)):
                si0=si[i]
                d['program_code'+'_'+str(i)]=si0['program_code']
                d['program_name'+'_'+str(i)]=si0['program_name']
                d['Session_code'+'_'+str(i)]=si0['program_session_code']               # utbildningstillfälleskod
                # the type of education is associated with an application code (anmälningskod)
                d['type_ of_education'+'_'+str(i)]=types_of_education[si0['program_type_code']]['en']
                d['program_study_period_start'+'_'+str(i)]=si0['program_study_period']['Startdatum']

                
        user_and_program_list.append(d)
        
    user_and_program_df=pd.json_normalize(user_and_program_list)
    output_file="users_programs-instance-{}".format(instance_code)
    write_xlsx(output_file, user_and_program_df, 'users_programs')

    # to logout and close the session
    status=ladok_session.logout()


if __name__ == "__main__": main()

