import pep8
import re
import os
import sys

CLASS_NAME_MATCH = re.compile(r'^_*[A-Z][a-zA-Z0-9]*_*$')
FUNCTION_NAME_MATCH = re.compile(r'^(_*|test_)[a-z][a-zA-Z0-9]*_*$')
MEMBER_NAME_MATCH = re.compile(r'^[a-z_][a-z0-9_]*$')
VARIABLE_NAME_MATCH = re.compile(r'^[a-z][a-z0-9_]*$')


# Check the logical line to see if there is a class or function definition. When there is, check if this definition matches
# The coding style set at Ultimaker.
def checkNames(logical_line, tokens):
    idx = 0
    while tokens[idx].type in [5, 6]:
        idx += 1
    if tokens[idx].string == "def":
        idx += 1
        if not FUNCTION_NAME_MATCH.match(tokens[idx].string):
            yield tokens[idx].start[1], "U101 Function name not properly formatted with lower camel case"
        idx += 1
        if tokens[idx].string != "(":
            yield tokens[idx].start[1], "U901 Parsing error"
            return
        idx += 1
        if tokens[idx].string != ")":
            while True:
                if tokens[idx].string == "*":
                    idx += 1
                if tokens[idx].string == "**":
                    idx += 1
                if not VARIABLE_NAME_MATCH.match(tokens[idx].string):
                    yield tokens[idx].start[1], "U201 Function parameter not in lower_case_underscore_format"
                idx += 1
                if tokens[idx].string == "=":
                    while tokens[idx].string not in [",", ")"]:
                        idx += 1
                if tokens[idx].string == ")":
                    break
                if tokens[idx].string != ",":
                    yield tokens[idx].start[1], "U902 Parsing error: %s: %s" % (tokens[idx].string, logical_line)
                    return
                idx += 1
    elif tokens[idx].string == "class":
        idx += 1
        if not CLASS_NAME_MATCH.match(tokens[idx].string) and tokens[idx].string != "i18nCatalog":
            yield tokens[idx].start[1], "U103 Class name not properly formatted with upper camel case"
    elif len(tokens) > idx + 3 and tokens[idx].string == "self" and tokens[idx + 1].string == "." and tokens[idx + 3].string == "=":
        if not MEMBER_NAME_MATCH.match(tokens[idx + 2].string):
            yield tokens[idx + 2].start[1], "U202 Member name not in lower_case_underscore_format"
    # elif len(tokens) > idx + 2 and tokens[idx + 1].string == "=":
    #     if not VARIABLE_NAME_MATCH.match(tokens[idx].string):
    #         yield tokens[idx].start[1], "U203 Variable name not in lower_case_underscore_format"


# Check the string definitions in the line. All strings should be double quotes.
def checkStrings(logical_line, tokens):
    for token in tokens:
        if token.type == 3:
            if token.string.startswith("'"):
                yield token.start, "U110 Strings should use double quotes, not single quotes."

def blankLines(logical_line, blank_lines, indent_level, line_number, blank_before, previous_logical):
    if line_number < 3 and not previous_logical:
        return  # Don't expect blank lines before the first line
    if logical_line.startswith(("def ", "class ", "@")):
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

    pep8style = pep8.StyleGuide(quiet=False, select=critical, ignore=ignore)
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
