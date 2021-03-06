#!/usr/bin/python

import sys
import os
import re
import lxml.etree as etree


def substitute_vars(fix):
    # brittle and troubling code to assign environment vars to XCCDF values
    env_var = re.match("(\s*source\s+\S+)\n+(\s*populate\s+)(\S+)\n(.*)",
                       fix.text, re.DOTALL)
    if not env_var:
        # no need to alter fix.text
        return
    # otherwise, create node to populate environment variable
    varname = env_var.group(3)
    mainscript = env_var.group(4)
    fix.text = varname + "=" + '"'
    # new <sub> element to reference XCCDF variable
    xccdf_sub = etree.SubElement(fix, "sub", idref=varname)
    xccdf_sub.tail = '"' + mainscript
    fix.append(xccdf_sub)


def main():
    if len(sys.argv) < 2:
        print "Provide a directory name, which contains the fixes."
        sys.exit(1)

    fixdir = sys.argv[1]
    output = sys.argv[2]

    fixcontent = etree.Element("fix-content", system="urn:xccdf:fix:script:sh",
                               xmlns="http://checklists.nist.gov/xccdf/1.1")
    fixgroup = etree.SubElement(fixcontent, "fix-group", id="bash",
                                system="urn:xccdf:fix:script:sh",
                                xmlns="http://checklists.nist.gov/xccdf/1.1")

    for filename in os.listdir(fixdir):
        if filename.endswith(".sh"):
            # create and populate new fix element based on shell file
            fixname = os.path.splitext(filename)[0]
            fix = etree.SubElement(fixgroup, "fix", rule=fixname)
            with open(fixdir + "/" + filename, 'r') as fix_file:
                # assignment automatically escapes shell characters for XML
                fix.text = fix_file.read()
                # replace instance of bash function "populate" with XCCDF
                # variable substitution
                substitute_vars(fix)

    if len(sys.argv) == 4:
        shared_fixdir = sys.argv[3]
        for filename in os.listdir(shared_fixdir):
            if filename.endswith(".sh"):
                # create and populate new fix element based on shell file
                fixname = os.path.splitext(filename)[0]
                fix = etree.SubElement(fixgroup, "fix", rule=fixname)
                with open(shared_fixdir + "/" + filename, 'r') as fix_file:
                    # assignment automatically escapes shell characters for XML
                    fix.text = fix_file.read()
                    # replace instance of bash function "populate" with XCCDF
                    # variable substitution
                    substitute_vars(fix)

    tree = etree.ElementTree(fixcontent)
    tree.write(output, pretty_print=True)

    sys.exit(0)

if __name__ == "__main__":
    main()
