'''
Author: Matt Brooks, @cmatthewbrooks

DESCRIPTION:

The sessionstarter.py script is helpful when starting a new
r2 session against a suspected malware target. It will handle
auto-analysis as well as naming specific types of functions.

ARGS:

Use the optional -i flag to point to a directory of sig hash files
generated by sigs.py

NOTES:

- When using zsigs from a signature file, only the "bytes" sigs
  are considered. The "refs" and "graphs" sigs are too loose for
  my taste and in the instances where they match correctly, a
  "bytes" signature exists for the same function. If you determine
  a case where the "refs" or "graphs" signatures were useful without
  an existing "bytes" signature, please file a Github issue.

TODO:


'''

import os,sys
import argparse
import json

import r2pipe 
import r2utils as R2utils

from sigs import Renamer

class SessionStarter:

    def __init__(self):

        r2 = r2pipe.open()
        
        func_count = r2.cmd('aflc')

        if int(func_count) == 0:
            # If there are no functions, analyze the file
            r2.cmd("aa; aar; aac")

        r2.quit()

    # The start_session method is the only method meant to be
    # called outside the class.

    def start_session(self, infile=None):

        if not infile:
            infile = ''

        lib_renamer = Renamer()
        lib_renamer.rename_recognized_code(infile)

        self.rename_common_funcs()


    def rename_common_funcs(self):

        r2 = r2pipe.open() 
        r2utils = R2utils.r2utils()

        funcj_list = r2utils.get_funcj_list()

        for funcj in funcj_list:

            if r2utils.check_is_import_jmp_func(funcj):

                r2.cmd('s ' + str(funcj['addr']))
                r2.cmd('afn jmp_' + 
                    r2utils.get_import_from_import_jmp_func(funcj)
                )

            elif r2utils.check_is_wrapper_func(funcj):

                r2.cmd('s ' + str(funcj['addr']))
                r2.cmd('afn wrapper_' + 
                    (r2utils.get_call_from_wrapper(funcj)).replace(' ','_')
                )

            elif r2utils.check_is_global_assignment_func(funcj):

                r2.cmd('s ' + str(funcj['addr']))
                r2.cmd('afn globalassign_' + funcj['name'].replace('.',''))


        r2.quit()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--infile', 
        help = 'Input for matching. Can be a file or directory.')
    args = parser.parse_args()

    if args.infile and not os.path.exists(args.infile):

        print args.infile + ' is not a valid input for signature matching.'
        sys.exit(1)
    
    elif args.infile and os.path.exists(args.infile):
    
        ss = SessionStarter()
        ss.start_session(args.infile)
    
    elif not args.infile:
    
        ss = SessionStarter()
        ss.start_session()
