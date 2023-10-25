import re

class Wiki:
    '''
    Parse wiki markup and return html.
    
    Syntax:
        [h1 Title 1]
        Url is [1] (or [2 Link text]). This is [img 3] or [img 4 Hello World!] images.
        [code python]
          ...
        [/code]
        ----
        [1] http://link
        [2] http://link2
        [3] http://link3
        [4] http://link4 class="one two"
        [h1] name="title1"
    
    Using:
      Wiki().parse(raw_data)
    '''
    rules = (
            # link: http://site.com/path/to/page.html
            ("((https?|ftp|nntp|news|mailto)://([\w._-]+\.\w{2,4})([^ ]*))",
             "<a href='\\1'>\\3</a>"),
            # email
            ("([\w._-]+\@([\w._-]+\w{2,4}))",
             "<a href='mailto:\\1'>\\1</a>"),
            # TODO: generate TOC (table of contents)
            ("^\[TOC\ h([1-6])-h([2-6])]$",
             "TOC - table of contents"),
            )

    def __init__(self):
        self.in_p = False
        self.in_pre = False
        self.in_code = False
        self.result = []
        # compile regular expressions
        self.rules = [(re.compile(k, flags=re.UNICODE), v) for k, v in Wiki.rules]

    def parse(self, text):
        '''Parce wiki text and return html'''
        lines = text.splitlines()
        self.result = []
        # transform wiki text to html
        for line in lines:
            # delete white spaces
            line = line.strip()
            # processing lines
            line = self.parse_line(line)
            # processing blocks
            line = self.parse_block(line)
        # post processing (close tags)
        if self.in_p:
            last = self.result.pop()
            self.result.append("</p>")
            self.result.append(last)
        return "".join(self.result)

    def parse_block(self, line):
        # separator
        if re.match(r"^-{3,}$", line, flags=re.UNICODE):
            line = "<hr>"
        # header
        elif line.startswith("="):
            depth = line.count("=", 0, 6)
            line = "<h%s>%s</h%s>" % (depth, line.lstrip("= "), depth)
        # paragraph
        elif not self.in_p and line:
            self.in_p = True
            self.result.append("<p>")
        elif self.in_p and line == "":
            self.in_p = False
            self.result.pop()
            self.result.append("</p>")
        elif self.in_p:
            last = self.result.pop()
            self.result.append("<br/>")
            self.result.append(last)
        elif line == "":
            self.result.pop()
        # set value and new line
        self.result.append(line)
        self.result.append("\n")

    def parse_line(self, line):
        # replace rules
        for key, value in self.rules:
            line = re.sub(key, value, line)
        # return changed line
        return line
