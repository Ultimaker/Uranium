import pep8
import re

CLASS_NAME_MATCH = re.compile(r'^_*[A-Z][a-zA-Z0-9]*_*$')
FUNCTION_NAME_MATCH = re.compile(r'^_*[a-z][a-zA-Z0-9]*_*$')


# Check the logical line to see if there is a class or function definition. When there is, check if this definition matches
# The coding style set at Ultimaker.
def checkNames(logical_line, tokens):
    idx = 0
    while tokens[idx].type in [5]:
        idx += 1
    if tokens[idx].string == 'def':
        idx += 1
        if not FUNCTION_NAME_MATCH.match(tokens[idx].string):
            print(logical_line)
            yield tokens[idx].start[1], "U101 Function name not properly formatted with lower camel case"
    if tokens[idx].string == 'class':
        idx += 1
        if not CLASS_NAME_MATCH.match(tokens[idx].string):
            print(logical_line)
            yield tokens[idx].start[1], "U102 Class name not properly formatted with upper camel case"


def blankLines(logical_line, blank_lines, indent_level, line_number, blank_before, previous_logical):
    if line_number < 3 and not previous_logical:
        return  # Don't expect blank lines before the first line
    if logical_line.startswith(('def ', 'class ', '@')):
        if not indent_level and blank_before < 1:
            yield 0, "U302 expected 2 blank lines, found 0"


def main():
    pep8.register_check(checkNames)
    pep8.register_check(blankLines)

    ignore = []
    ignore.append('E501')  # Ignore line length violations.
    ignore.append('E226')  # Ignore too many leading # in comment block.

    critical = []
    critical.append('U101')  # Function name does not match the coding standard.
    critical.append('U102')  # Class name does not match the coding style.
    critical.append('E301')  # expected 1 blank line, found 0
    critical.append('U302')  # expected 2 blank lines, found 0
    critical.append('E304')  # blank lines found after function decorator
    critical.append('E401')  # multiple imports on one line
    critical.append('E402')  # module level import not at top of file
    critical.append('E713')  # test for membership should be ‘not in’
    critical.append('W191')  # indentation contains tabs

    pep8style = pep8.StyleGuide(quiet=False, select=critical, ignore=ignore)
    result = pep8style.check_files(['.'])
    print('----------------------------------')
    result.print_statistics()

if __name__ == "__main__":
    main()
