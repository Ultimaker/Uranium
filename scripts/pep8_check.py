# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import pep8
import re
import os
import sys
import token as token_type

CLASS_NAME_MATCH = re.compile(r'^_*[A-Z][a-zA-Z0-9]*_*$')
FUNCTION_NAME_MATCH = re.compile(r'^(_*|test_)[a-z][a-zA-Z0-9]*_*$')
PUBLIC_MEMBER_NAME_MATCH = re.compile(r'^[A-Z][a-zA-Z0-9]*_*$')
MEMBER_NAME_MATCH = re.compile(r'^[a-z_][a-z0-9_]*$')
VARIABLE_NAME_MATCH = re.compile(r'^[a-z][a-z0-9_]*$')

indent_stack = []

# Check the logical line to see if there is a class or function definition. When there is, check if this definition matches
# The coding style set at Ultimaker.
def checkNames(logical_line, physical_line, tokens, indent_level):
    global indent_stack
    if logical_line != '':
        while indent_stack and indent_stack[-1][0] >= indent_level:
            indent_stack.pop()
        if not indent_stack or indent_stack[-1][0] < indent_level:
            indent_stack.append((indent_level, logical_line))

    # Allow for violations in the coding style in rare cases.
    if "# [CodeStyle: " in physical_line:
        return

    idx = 0
    while tokens[idx].type in [token_type.INDENT, token_type.DEDENT]:
        idx += 1
    if tokens[idx].string == "def":
        idx += 1
        if not FUNCTION_NAME_MATCH.match(tokens[idx].string):
            yield tokens[idx].start, "U101 Function name not properly formatted with lower camel case"
        idx += 1
        if tokens[idx].string != "(":
            yield tokens[idx].start, "U901 Parsing error"
            return
        idx += 1
        if tokens[idx].string != ")":
            while True:
                if tokens[idx].string == "*":
                    idx += 1
                if tokens[idx].string == "**":
                    idx += 1
                if not VARIABLE_NAME_MATCH.match(tokens[idx].string):
                    yield tokens[idx].start, "U201 Function parameter not in lower_case_underscore_format"
                idx += 1
                if tokens[idx].string == "=":
                    while tokens[idx].string not in [",", ")"]:
                        idx += 1
                if tokens[idx].string == ")":
                    break
                if tokens[idx].string != ",":
                    yield tokens[idx].start, "U902 Parsing error: %s: %s" % (tokens[idx].string, logical_line)
                    return
                idx += 1
    elif tokens[idx].string == "class":
        idx += 1
        if not CLASS_NAME_MATCH.match(tokens[idx].string):
            yield tokens[idx].start, "U103 Class name not properly formatted with upper camel case"
    elif len(tokens) > idx + 3 and tokens[idx].string == "self" and tokens[idx + 1].string == "." and tokens[idx + 3].string == "=":
        if not MEMBER_NAME_MATCH.match(tokens[idx + 2].string):
            yield tokens[idx + 2].start, "U202 Member name not in lower_case_underscore_format"
    elif len(tokens) > idx + 2 and tokens[idx + 1].string == "=":
        if len(indent_stack) > 1 and indent_stack[-2][1].startswith('class '):
            # definition is a class member
            if tokens[idx].string.startswith('_'):
                # class member is a private, match the member name style.
                if not MEMBER_NAME_MATCH.match(tokens[idx].string):
                    yield tokens[idx].start, "U202 Member name not in lower_case_underscore_format"
            else:
                # TODO, the conding standard for this is not defined yet. And there are a few variations used in the code.
                # if not PUBLIC_MEMBER_NAME_MATCH.match(tokens[idx].string):
                #     yield tokens[idx].start, "U102 Public member name not in UpperCamelCase format"
                pass
        else:
            # definition is a variable
            if not VARIABLE_NAME_MATCH.match(tokens[idx].string):
                yield tokens[idx].start, "U203 Variable name not in lower_case_underscore_format"


# Check the string definitions in the line. All strings should be double quotes.
def checkStrings(logical_line, tokens):
    for token in tokens:
        if token.type == token_type.STRING:
            if token.string.startswith("'") and not token.string.startswith("'''"): # ''' indicates multiline comment so should be ignored.
                yield token.start, "U110 Strings should use double quotes, not single quotes."

def blankLines(logical_line, blank_lines, indent_level, line_number, blank_before, previous_logical):
    if line_number < 3 and not previous_logical:
        return  # Don't expect blank lines before the first line
    if logical_line.startswith(("def ", "class ", "@")) and not previous_logical.startswith("@"):
        if not indent_level and blank_before < 1:
            yield 0, "U302 expected 2 blank lines, found 0"


def main(paths=["."]):
    pep8.register_check(checkNames)
    pep8.register_check(blankLines)
    pep8.register_check(checkStrings)

    ignore = []
    ignore.append("E501")  # Ignore line length violations.
    ignore.append("E226")  # Ignore too many leading # in comment block.

    critical = []
    critical.append("E301")  # expected 1 blank line, found 0
    critical.append("U302")  # expected 2 blank lines, found 0
    critical.append("E304")  # blank lines found after function decorator
    critical.append("E401")  # multiple imports on one line
    critical.append("E402")  # module level import not at top of file
    critical.append("E713")  # test for membership should be ‘not in’
    critical.append("W191")  # indentation contains tabs
    critical.append("U9")    # Parsing errors (error in this script, or error in code that we're trying to parse)
    critical.append("U")     # All Ultimaker specific stuff.

    pep8style = pep8.StyleGuide(quiet=False, select=critical, ignore=ignore, show_source=True)
    for path in paths:
        if path.endswith(".py") and "_pb2.py" not in path:
            pep8style.paths.append(path)
        for base_path, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(".py") and "_pb2.py" not in filename:
                    pep8style.paths.append(os.path.join(base_path, filename))
    result = pep8style.check_files()
    print("----------------------------------")
    result.print_statistics()
    print("Total: %d" % (result.get_count()))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        main()
