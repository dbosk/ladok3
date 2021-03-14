#!/usr/bin/python3
#
# Use the data in a Canvas course room to create a spreadsheet of students in the course who are missing an integration ID
#
# Input 
# ./canvas_students_missing_integration_ids.py canvas_course_id
#
# Éxamples:
# ./canvas_students_missing_integration_ids.py 17636
#
# will produce a file: 'users_programs-12162.xlsx
# This file will contain the columns:
# 	canvas_user_id	user	ladok_id				pnr
# 0	xxxx		xxx,yyy	Missing integration ID			fill-in person number
# 1	xxxx		xxx,yyy	Missing integration ID			fill-in person number
# 2	xxxx		xxx,yyy	Missing integration ID			fill-in person number
#...
#
# This program gets the list of users enrolled in a Canvas course and then check for an integration_id. If the integration_id is missing, add the student
# to the spreadsheet.
#
# It requires a config.json file with (1) the Canvas url and access token and (2) the user's username and password (for access to Ladok)
#
# last modified: 2020-07-23
#

import pprint
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

    except:
        print("Unable to open configuration file named {}".format(config_file))
        print("Please create a suitable configuration file, the default name is config.json")
        sys.exit()

    return None


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

#//////////////////////////////////////////////////////////////////////
# utility routines
#//////////////////////////////////////////////////////////////////////
# set up the output write
def write_xlsx(file_name, df, sheet_name):
    writer = pd.ExcelWriter(file_name+'.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name)
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


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

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide course_id\n")
        sys.exit()

    course_id=remainder[0]
    users=users_in_course(course_id)

    user_and_program_list=[]
    # processed_users is a set of user_id that have already been processed
    processed_users=set()
    for u in users:
        d=dict()
        user_id=u['user_id']
        if user_id in processed_users:
            continue

        ladok_id=u['user']['integration_id']
        if not ladok_id:
            if Verbose_Flag:
                print("user without integration_id - user_id={0}, {1}".format(user_id, u['user']['sortable_name']))
            d['canvas_user_id']=user_id
            d['user']=u['user']['sortable_name']
            d['ladok_id']="Missing integration ID"
            d['pnr']="fill-in person number"
            user_and_program_list.append(d)
        processed_users.add(user_id)

    user_and_program_df=pd.json_normalize(user_and_program_list)
    output_file="users_without_integration_ids-{}".format(course_id)
    write_xlsx(output_file, user_and_program_df, 'users_programs')

if __name__ == "__main__": main()

