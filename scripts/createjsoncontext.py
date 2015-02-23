#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2014  Burkhard Lück <lueck@hube-lueck.de>

Permission to use, copy, modify, and distribute this software
and its documentation for any purpose and without fee is hereby
granted, provided that the above copyright notice appear in all
copies and that both that the copyright notice and this
permission notice and warranty disclaimer appear in supporting
documentation, and that the name of the author not be used in
advertising or publicity pertaining to distribution of the
software without specific, written prior permission.

The author disclaim all warranties with regard to this
software, including all implied warranties of merchantability
and fitness.  In no event shall the author be liable for any
special, indirect or consequential damages or any damages
whatsoever resulting from loss of use, data or profits, whether
in an action of contract, negligence or other tortious action,
arising out of or in connection with the use or performance of
this software.
"""

import sys, os, json, time, os.path

debugoutput = False #set True to print debug output in scripty's logs

translationfields=['label', 'description'] # = Name + Comment in desktop files
# GenericName translation apparently unused?

basedir = sys.argv[-1]
pottxt = ""

def appendMessage(file, setting, field, value):
    global pottxt
    pottxt += '#: {0}\nmsgctxt "{1} {2}"\nmsgid "{3}"\nmsgstr ""\n\n'.format(file, setting, field, value.replace('\n', '\\n'))

def processSettings(file, settings):
    for name, value in settings.items():
        appendMessage(file, name, 'label', value['label'])
        if 'description' in value:
            appendMessage(file, name, 'description', value['description'])

        if 'children' in value:
            processSettings(file, value['children'])

def potheader():
    headertxt =  "#, fuzzy\n"
    headertxt += "msgid \"\"\n"
    headertxt += "msgstr \"\"\n"
    headertxt += "\"Project-Id-Version: json files\\n\"\n"
    headertxt += "\"Report-Msgid-Bugs-To: http://bugs.kde.org\\n\"\n"
    headertxt += "\"POT-Creation-Date: %s+0000\\n\"\n" %time.strftime("%Y-%m-%d %H:%M")
    headertxt += "\"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n\"\n"
    headertxt += "\"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n\"\n"
    headertxt += "\"Language-Team: LANGUAGE <kde-i18n-doc@kde.org>\\n\"\n"
    headertxt += "\"MIME-Version: 1.0\\n\"\n"
    headertxt += "\"Content-Type: text/plain; charset=UTF-8\\n\"\n"
    headertxt += "\"Content-Transfer-Encoding: 8bit\\n\"\n"
    headertxt += "\n"
    return headertxt

if len(sys.argv) < 3:
    print('wrong number of args: %s' %sys.argv)
    print('\nUsage: python %s jsonfilenamelist basedir' %os.path.basename(sys.argv[0]))
else:
    jsonfilenamelist = sys.argv[1:-1]

    for jsonfilename in jsonfilenamelist:
        with open(jsonfilename, 'r') as data_file:
            error = False
            try:
                jsondatadict = json.load(data_file)
                if not 'categories' in jsondatadict:
                    continue

                for name, value in jsondatadict['categories'].items():
                    appendMessage(jsonfilename.replace(basedir,''), name, 'label', value['label'])
                    if 'description' in value:
                        appendMessage(jsonfilename.replace(basedir,''), name, 'description', value['description'])

                    if 'settings' in value:
                        processSettings(jsonfilename.replace(basedir,''), value['settings'])
            except Exception as e:
                print(e)

    if pottxt!="":
        print(potheader() + pottxt)
