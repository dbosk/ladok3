#!/usr/bin/python3
#
# Use the data in a spreadsheet to compute some statistics about the number of students in eahc program, track, and addmission group
#
# Input 
# ./add_stats_to_spreadsheet.py spreadsheet_filae.xls sheet_name
#
# Éxamples:
#
# last modified: 2020-07-25
#

import pprint
import time
import json
import optparse
import sys

import pandas as pd
pp = pprint.PrettyPrinter(indent=4)

def add_program_code_to_program_codes(prg_code):
    global program_codes
    current_entry=program_codes.get(prg_code, 0)
    program_codes[prg_code]=current_entry+1

def add_program_code_and_other_data(prgm_code, prgm_name, track_code, admission):
    global program_stats
    
    current_prgm_entry=program_stats.get(prgm_code, dict())
    program_stats[prgm_code]=current_prgm_entry
    
    current_prgm_name_entry=current_prgm_entry.get(prgm_name, dict())
    program_stats[prgm_code][prgm_name]=current_prgm_name_entry

    current_track_entry=current_prgm_name_entry.get(track_code, dict())
    program_stats[prgm_code][prgm_name][track_code]=current_track_entry

    current_admissions_entry=current_track_entry.get(admission, 0)
    program_stats[prgm_code][prgm_name][track_code][admission]=current_admissions_entry+1

def main():
    global Verbose_Flag
    global program_codes
    global program_stats

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))

    if (len(remainder) < 2):
        print("Insuffient arguments - must provide filename for an XLSX spreadsheet and sheet name")
        sys.exit()

    input_filename=remainder[0]
    sheetname=remainder[1]

    spreadsheet_df = pd.read_excel(open(input_filename, 'rb'), sheet_name=sheetname)

    program_codes=dict()
    program_stats=dict()
    
    for index, row in  spreadsheet_df.iterrows():
        if Verbose_Flag:
            print("index: {0}, row: {1}".format(index, row))
        add_program_code_to_program_codes(row['program_code'])
        add_program_code_and_other_data(row['program_code'], row['program_name'], row['track_code'], row['admission'])

    print("program_codes={}".format(program_codes))
    print("program_stats={}".format(program_stats))
    pp.pprint(program_stats)

    # stats_df
    # write_xlsx(output_file, stats_df, 'stats')



if __name__ == "__main__": main()

