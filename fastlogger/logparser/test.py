test_strs = [
"""
text
text
text
""",
"""
{single line comment}
""",
"""
{ single line comment with space }
""",
"""
{two line comment...
it continues}
""",
"""
{ two line comment...
it continues }
""",
"""
{multiline comment
in continues
we can put more info here}
""",
"""
{ multiline comment
in continues
we can put more info here }
""",
"""
{multiline comment
in continues
in continues
in continues
we can put more info here}
""",
"""
{ multiline comment
in continues
in continues
in continues
we can put more info here }
""",
"""
some text goes here {but wait! here's a comment}
""",
"""
some text goes here { but wait! here's a comment }
""",
"""
some text goes here {but wait! here's a comment
but wait! there's more! it's multiple lines!}
""",
"""
some text goes here { but wait! here's a comment
but wait! there's more! it's multiple lines! }
""",
"""
text {comment
comment
more comment}
""",
"""
text { comment
comment
more comment }
""",
"""
text {comment
more comment} more text
""",
"""
text { comment
more comment } more text
""",
"""
text {comment
comment
more comment} text
""",
"""
text { comment
comment
more comment } text
""",
"""
text {comment} text
""",
"""
text { comment } text
""",
"""
text {comment} text {comment}
""",
"""
text { comment } text { comment }
""",
]

for test in test_strs:
    comment = False
    clean_str = ""
    for ln in test.split("\n"):
        #print(ln)
        clean_ln = ""
        for char in ln:
            if not comment:
                if char == "{":
                    comment = True
                else:
                    clean_ln += char
            # if comment
            else:
                if char == "}":
                    comment = False
                else:
                    continue
        clean_str += clean_ln + "\n"
    print(test)
    print(clean_str)