import argparse
import os
import re
from pathlib import Path


class Dox2Rst:
    REGEX = re.compile(r"(?P<before>[\s\S]*\n)?" +
                       r"(?P<dox>\s*##.*\n(?:\s*#.*)*\n*)" +
                       r"(?P<decorator>(?:\s*@.*\n)*)" +
                       r"(?P<def>\s*(?:def|class).*)\n" +
                       r"(?P<after>[\s\S]*)")

    INDENT_PATTERN = re.compile(r"\s*")
    DOX_CONTINUATION_PREFIX_PATTERN = re.compile(r"( +#) *", re.MULTILINE)

    def convert(self, file_path: str, dry_run: bool = False) -> int:
        print(file_path)
        with open(file_path, "r+") as f:
            contents = f.read()
            change_count = 0

            # Block comments
            changed = True
            while changed:
                contents, changed = self.replace_first_block_comment(contents)
                change_count = change_count + changed  # Increase count by 1 if changed

            # variable / member comments
            changed = True
            while changed:
                contents, changed = self.replace_first_member_comment(contents)
                change_count = change_count + changed  # Increase count by 1 if changed

            if change_count > 0:
                if dry_run:
                    print("======[[ {} ]]======".format(file_path))
                    print(contents)
                else:
                    f.seek(0)
                    f.truncate()
                    f.write(contents)

            return change_count

    def replace_first_block_comment(self, contents: str) -> (str, bool):
        match = self.REGEX.match(contents)
        if match is not None:
            comment_block = match.group("dox")
            comment_block = self.add_indent(comment_block)
            comment_block = self.convert_comment_block(comment_block)
            contents = "{before}{decorator}{definition}\n{rst}\n{after}".format(
                before=match.group("before"),
                decorator=match.group("decorator"),
                definition=match.group("def"),
                rst=comment_block,
                after=match.group("after")
            )
            return contents, True
        else:
            return contents, False

    OPENING_REGEX = re.compile(r"## +")
    PARAM_REGEX = re.compile(r":param \w+")
    RETURN_REGEX = re.compile(r":returns?")
    RST_COMMAND_SUB = "\g<0>:"

    def convert_comment_block(self, dox_block: str):
        """

        :param dox_block:
        """
        indent = self.INDENT_PATTERN.search(dox_block)
        if indent is None:
            indent = ""
        else:
            indent = indent.group()

        # replace opening
        output = re.sub(self.OPENING_REGEX, '"""', dox_block)
        output = re.sub(self.DOX_CONTINUATION_PREFIX_PATTERN, indent, output)
        # replace keyword escapes ie. \return -> :return
        output = output.replace('\\', ":")

        output = output.replace(":code", "")
        output = output.replace(":endcode", "")
        output = re.sub(self.PARAM_REGEX, self.RST_COMMAND_SUB, output)
        output = re.sub(self.RETURN_REGEX, self.RST_COMMAND_SUB, output)
        # Add closing """
        if len(output.splitlines()) > 1:
            output = "{before}{indent}\"\"\"\n".format(before=output, indent=indent)
        else:
            output = output.splitlines()[0]
            output = "{before}\"\"\"\n".format(before=output, indent=indent)

        # ensure separation of subject line and body
        lines = output.splitlines()
        if len(lines) > 1 and re.search(r"\S", lines[1]) is not None:
            lines.insert(1, indent)
            output = "\n".join(lines)

        return output

    MEMBER_COMMENT_REGEX = re.compile(r"(?P<before>[\s\S]*\n)?(?P<dox>\s*##.*\n(?:\s*#.*)*\n*)(?P<var>[\s\w]+=.+\n)(?P<after>[\s\S]*)")

    def replace_first_member_comment(self, contents: str) -> (str, bool):
        match = self.MEMBER_COMMENT_REGEX.match(contents)
        if match is not None:
            comment = match.group("dox")
            comment = self.convert_comment_block(comment)
            contents = "{before}{var}{comment}{after}".format(
                before=match.group("before"),
                var=match.group("var"),
                comment=comment,
                after=match.group("after")
            )
            return contents, True
        else:
            return contents, False

    COMMENT_INDENT_PATTERN = re.compile(r"^\s*#", re.MULTILINE)
    COMMENT_INDENT_SUB = "    \g<0>"

    def add_indent(self, comment_block: str):
        """Add a single level of indent."""

        return re.sub(self.COMMENT_INDENT_PATTERN, self.COMMENT_INDENT_SUB, comment_block)


def main():
    parser = argparse.ArgumentParser("python dox_2_rst.py")
    parser.add_argument("-r", "--recursive", dest="recursive",
                        help="Find python files to convert recursively", default=False, action="store_true")
    parser.add_argument("-d", "--dry", dest="dry_run",
                        help="Print output; do not change files", default=False, action="store_true")
    parser.add_argument("paths", metavar="PATHS", type=str, nargs="+", help="Files or Directories to process")

    args = parser.parse_args()

    glob_func = "rglob" if args.recursive else "glob"

    changed_files_count = 0
    total_changes_count = 0
    python_file_list = []
    for entry in args.paths:
        if not os.path.exists(entry):
            print("WARNING: skipping {}: not found".format(entry))
            continue
        if os.path.isfile(entry):
            python_file_list.append(entry)
        else:
            for path_like in getattr(Path(entry), glob_func)('*.py'):
                python_file_list.append(path_like)

    dox_2_rst = Dox2Rst()
    for file_path in python_file_list:
        comments_changed_count = dox_2_rst.convert(str(file_path), dry_run=args.dry_run)
        if comments_changed_count > 0:
            changed_files_count = changed_files_count + 1
        total_changes_count = total_changes_count + comments_changed_count

    print("Considered {} Python files".format(len(python_file_list)))
    print("Converted {} comments across {} files".format(total_changes_count, changed_files_count))


if __name__ == "__main__":
    main()
