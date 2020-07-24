#!/usr/bin/python3
#
# Use the data in a Canvas course room together with the data from Ladok3 to find information about a user.
#
# Input 
# ./cl_user_info.py Canvas_user_id|KTHID|Ladok_id [course_id]
#
# Éxamples:
# ./cl_user_info.py 29
# ./cl_user_info.py u1d13i2c 
# ./cl_user_info.py 'maguire@kth.se'
#
# If you know the student's Ladok ID, i.e., sis_integration_id you can say
# ./cl_user_info.py 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
#
#
# ./cl_user_info.py dddd         course_id
# ./cl_user_info.py u1xxxxx      course_id
# ./cl_user_info.py 'x@kth.se'   course_id
#
# The course ID can be a Canvas course_id or
# if you have dashboard cards, you can specific a course code, a nickname, unique part of the short name or original course name
#
# This program gets the list of users enrolled in a Canvas course and then uses their integration-id to ask Ladok for the information about the student.
#
# It requires a config.json file with (1) the Canvas url and access token and (2) the user's username and password (for access to Ladok)
#
# last modified: 2020-07-24
#

import ladok3,  pprint
import requests, time
import json
import optparse
import sys
import pandas as pd
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
    ls=ladok3.LadokSession(username, password)
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


def users_in_accounts(account_id, user_id):
    users_found_thus_far=[]
    # Use the Canvas API to get the list of users in this account
    #GET /api/v1/accounts/:account_id/users

    url = "{0}/accounts/{1}/users".format(canvas_baseUrl, account_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    extra_parameters={'per_page': '100',
                      #'type': ['StudentEnrollment']
    }
    r = requests.get(url, params=extra_parameters, headers = canvas_header)
    if Verbose_Flag:
        print("result of getting users in account: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            users_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # while r.links.get('next', False):
        #     r = requests.get(r.links['next']['url'], headers=canvas_header)
        #     page_response = r.json()  
        #     for p_response in page_response:  
        #         users_found_thus_far.append(p_response)

    return users_found_thus_far



def user_info(user_id):
    # Use the Canvas API to get the list of users enrolled in this course
    #GET /api/v1/users/:id

    url = "{0}/users/{1}".format(canvas_baseUrl, user_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = canvas_header)
    if Verbose_Flag:
        print("result of getting user: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        return r.json()
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

def specialization_info(ls, student_uid):
    s1=ls.studystructure_student_JSON(student_uid)
    ss1=s1['Studiestrukturer']

    # a student who is not in a program will have s1 == {'Studiestrukturer': [], 'link': []}
    if not ss1:
        return ["Self-contained courses - no program"]

    program_code=s1['Studiestrukturer'][0]['Utbildningsinformation']['Utbildningskod']
    if len(s1['Studiestrukturer'][0]['Barn']) > 0:
        sss1=s1['Studiestrukturer'][0]['Barn'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Benamning']['en']
        sss2=s1['Studiestrukturer'][0]['Barn'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningskod']
        sss3=s1['Studiestrukturer'][0]['Barn'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningstillfalleskod']
        return [program_code, sss1, sss2, sss3]
    else:
        check_for_english_program_name=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Benamning'].get('en', False)
        if check_for_english_program_name:
            sss1=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Benamning']['en']
        else:
            sss1=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Benamning']['sv']
            print("*** No English program name for {}".format(sss1))

        sss2=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningskod']
        sss3=s1['Studiestrukturer'][0]['Tillfallesdeltagande']['Utbildningsinformation']['Utbildningstillfalleskod']
        return [program_code, sss1, sss2, sss3]

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

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    ladok_session=initialize(options)

    integration_id=None

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide Canvas_user_id|KTHID|Ladok_id [course_id]\n")
        sys.exit()

    person_id=remainder[0]
    # users=users_in_accounts('self', person_id)
    # print("users={}".format(users))

    # check for numeric string, in which case this a Canvas user_id
    if person_id.isdigit():
        info=user_info(person_id)
    elif person_id.count('-') == 4:     # Ladok ID, i.e., a sis_integration_id
        info=user_info('sis_integration_id:'+person_id)
        integration_id=person_id        # since we have the Ladok ID, save it for later
    elif person_id.find('@') > 1:       # if an e-mail address
        info=user_info('sis_login_id:'+person_id)
    else:
        # assume it is a KTHID
        info=user_info('sis_user_id:'+person_id)

    # extract Canvas user-id from the user's info:
    user_id=info['id']
    print("sortable name={}".format(info['sortable_name']))
    print("Canvas user_id={}".format(user_id))

    if integration_id:
        student_info=ladok_session.get_student_data_by_uid_JSON(integration_id)
        if Verbose_Flag:
            pp.pprint("student_info={}".format(student_info))
        pnr=student_info['Personnummer']
        if pnr:
            print("pnr={}".format(pnr))
            si=specialization_info(ladok_session, integration_id)
            print("integration_id={0};program: {1}".format(integration_id, si))
            return

    if (len(remainder) == 1) and not integration_id:
        print("To get the personnumber, specify a course_id|course code|short name in which the users in enrolled as 2nd argument to the program")
        return


    # if we don't have the integration_id, then we need a course number to look it up
    if (len(remainder) == 2):
        course_id=remainder[1]
        course_id=process_course_id_from_commandLine(course_id)
        if not course_id:
            print("Unable to recognize a course_id, course code, or short name for a course in {}".format(remainder[0]))
            return

        # look for user - then check for integration_id
        users=users_in_course(course_id)
        if Verbose_Flag:
            print("users={}".format(users))

        for u in users:
            if u['user']['id'] == user_id:
                integration_id=u['user'].get('integration_id', None)
                if not integration_id:
                    print("user without integration_id - user_id={0}, {1}".format(user_id, u['user']['sortable_name']))
                else:
                    if Verbose_Flag:
                        print("integration_id={}".format(integration_id))
                    student_info=ladok_session.get_student_data_by_uid_JSON(integration_id)
                    if Verbose_Flag:
                        pp.pprint("student_info={}".format(student_info))
                    pnr=student_info['Personnummer']
                    if pnr:
                        print("pnr={}".format(pnr))
                    si=specialization_info(ladok_session, integration_id)
                    print("integration_id={}".format(integration_id))
                    print("program: {}".format(si))

                    # as a user will be in the list of users for each enrollment
                    # (which means for each section they are in), once found return
                    return

    # to logout and close the session
    status=ladok_session.logout()


if __name__ == "__main__": main()

