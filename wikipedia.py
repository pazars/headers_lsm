# This Python file uses the following encoding: utf-8
"""
Created on Jan 30, 2021
@author: lukelindemann

Wikipedia metadata:
https://en.wikipedia.org/wiki/Help:Cheatsheet


"""

import re
import utils

# from bz2 import BZ2File as bzopen
from os import listdir
from bz2file import BZ2File as bzopen  # For Multistream

# from Carbon.Aliases import false


def open_bz2(filename, line_limit=100000):
    # reading a bz2 archive
    with bzopen(filename, "r") as bzfin:
        lines = []
        for i, line in enumerate(bzfin):
            if i == line_limit:
                break
            # Decode the binary line into text using UTF-8 encoding
            line_text = line.decode("utf-8")
            lines.append(line_text)
    # bzfin.close()
    return lines


def del_wiki_tab(page):
    lev = 0
    clean_page = ""

    for i in range(0, len(page)):
        # Current char
        char = page[i]

        # Previous char
        if i >= 1:
            pchar = page[i - 1]
        else:
            pchar = ""

        # Previous previous char
        if i >= 2:
            ppchar = page[i - 2]
        else:
            pchar = ""

        # Next char
        if i < len(page) - 1:
            nchar = page[i + 1]
        else:
            nchar = ""

        # Going in a level: {|
        if (char == "{") and (nchar == "|"):
            # print 'Going in'
            # print page[i:i+50]
            lev += 1

        # Going out a level: |}
        if (pchar == "}") and (ppchar == "|"):
            # print 'Coming out'
            # print page[i-2:i+50]
            lev -= 1

        # Failsafe for unbalanced tags: if there's a double linebreak assume the table is closed
        # if (lev != 0) and (char == '\n') and (nchar == '\n'):
        #    lev = 0

        # Write if outside a table
        if lev == 0:
            clean_page += char

    return clean_page


def del_wiki_temp(page):
    # Must be run after del_wiki_table!!!!!

    # Deletes everything between nested {{tags}}, including templates,
    # citation tags, math formulas, infoboxes

    lev = 0
    clean_page = ""
    collection = ""
    onCollect = False

    page = re.sub("{{", "{>", page)
    page = re.sub("}}", "<}", page)

    for i in range(0, len(page)):
        # Current char
        char = page[i]

        # Previous char
        if i >= 1:
            pchar = page[i - 1]
        else:
            pchar = ""

        # Previous previous char
        if i >= 2:
            ppchar = page[i - 2]
        else:
            ppchar = ""

        # Next char
        if i < len(page) - 1:
            nchar = page[i + 1]
        else:
            nchar = ""

        # Going in a level: {{
        if (char == "{") and (nchar == ">"):
            if lev == 0:
                onCollect = True

            lev += 1

        # Going out a level: }}
        if (pchar == "}") and (ppchar == "<"):
            lev -= 1

            if lev == 0:
                # print collection
                # print '\n\n\n'
                onCollect = False
                collection = ""

        # Write if outside a table
        if lev == 0:
            clean_page += char

        if onCollect:
            collection += char

    return clean_page


def wiki_clean(page):
    page_clean = page

    # Delete Tables and Templates
    page_clean = del_wiki_temp(page_clean)
    page_clean = del_wiki_tab(page_clean)

    # p1_clean = re.sub('<!--.*?-->', '', p1_clean, flags=re.DOTALL)
    # p1_clean = re.sub('<(.*?)>', '', p1_clean, flags=re.DOTALL)
    # p1_clean = re.sub('\n[\{\[=\*].*', '', p1_clean)
    # p1_clean = re.sub('^[\{\[=\*].*', '', p1_clean)

    # p1_clean = re.sub("'''", "", p1_clean)
    # p1_clean = re.sub('\n.*[_=|&].*', '', p1_clean)
    # p1_clean = re.sub('^.*[_=|&].*', '', p1_clean)

    # p1_clean = re.sub('[\[\]]', '', p1_clean)

    # Delete any line that contains <tag carrots>:
    # Note: These are XML tags, not wysinwyg Wiki Markup tags
    page_clean = re.sub(r"[\t ]*<text.*>", "", page_clean)
    page_clean = re.sub(r"</text>", "", page_clean)
    page_clean = re.sub(
        r"^.*[<>].*$", r"", page_clean, flags=re.MULTILINE
    )  # Any line with <carrots>

    # Delete ''Italic'' and '''Bold''' formatting
    page_clean = re.sub(r"'{2,}", r"", page_clean)

    # Links:
    # Delete doubly embedded links (links within file captions) e.g. [[File:Wiki.png|thumb| [[Caption1]] and [[Caption 2]] ]]
    page_clean = re.sub(
        r"\[\[[^\[\]]*(\[\[[^\[\]]*\]\][^\[\]]*)+[^\[\]]*\]\]", r"", page_clean
    )
    # Delete if it has a colon -> [[Category:Category Name]] [[File:Wiki.png|thumb|Caption]]
    page_clean = re.sub(r"\[\[[^\]]*:[^\]]*\]\]", r"", page_clean)
    # If piped, take the second element -> [[FileName|FileAlias]]
    page_clean = re.sub(
        r"\[\[[^\]]+\|([^\]]+)\]\]", r"\1", page_clean
    )  # Links of the type: [[ LinkName | LinkAlias ]] -> LinkAlias
    # Otherwise, just remove double brackets
    page_clean = re.sub(r"(\[\[)|(\]\])", r"", page_clean)
    # Delete website link and description of form [http://www.link.com description]
    page_clean = re.sub(r"\[(\w+):\/\/(.*?)(( (.*?))|())\]", r"", page_clean)
    # Delete bare website links
    page_clean = re.sub(r"(\w+):\/\/(.*?)( |$)", r"", page_clean, flags=re.MULTILINE)

    # References: Delete everything between <ref../ref> OR <ref .../> tags
    page_clean = re.sub(
        r"&lt;ref.*?((/ref&gt;)|(/&gt;))", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags

    # Delete everything between tags: <math../math> OR <math.. /math> tags
    # Math, imagemap, gallery...
    page_clean = re.sub(
        r"&lt;math.*?((/math&gt;)|(/&gt;))", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags
    page_clean = re.sub(
        r"&lt;imagemap.*?((/imagemap&gt;)|(/&gt;))", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags
    page_clean = re.sub(
        r"&lt;mapframe.*?((/mapframe&gt;)|(/&gt;))", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags
    page_clean = re.sub(
        r"&lt;gallery.*?((/gallery&gt;)|(/&gt;))", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags
    page_clean = re.sub(
        r"&lt;inputbox.*?((/inputbox&gt;)|(/&gt;))", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags
    page_clean = re.sub(
        r"&lt;timeline.*?((/timeline&gt;)|(/&gt;))", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags
    page_clean = re.sub(
        r"&lt;center.*?((/center&gt;)|(/&gt;))", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags
    page_clean = re.sub(
        r"&lt;table.*?/table&gt;", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags
    page_clean = re.sub(
        r"&lt;td.*?/td&gt;", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags
    page_clean = re.sub(
        r"&lt;tr.*?/tr&gt;", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags

    # Comments, Other Wiki <markup>: Delete within tags:
    page_clean = re.sub(
        r"&lt;.*?&gt;", "", page_clean, flags=re.DOTALL
    )  # Delete anything between Wiki's &lt; and &gt; tags

    # Delete full lines that start with Headings (==Heading==), Lists (*X, ;X, #X), #REDIRECT, &  and parts of tables (!,|,})
    page_clean = re.sub(
        r"^[\*#&\-=;!Â¹Â²Â³Â°â€ :\|\}].*$", r"", page_clean, flags=re.MULTILINE
    )  # Line starts with =,*,#,&,-,:(indent),Â¹Â²Â³Â°â€ (footnotes)

    # Delete Table of Content Metadata:
    page_clean = re.sub(
        r"(__FORCETOC__)|(__TOC__)|(__NOTOC__)|(__NOEDITSECTION__)", r"", page_clean
    )

    # Turn non-breaking spaces into spaces:
    page_clean = re.sub(r"&?nbsp;", r" ", page_clean)

    # Delete special character codes like &atilde;:
    page_clean = re.sub(r"&\w+;", r"", page_clean)

    # Delete lines that start with a numeral (almost always lists or timelines)
    page_clean = re.sub(r"^\d.*$", r"", page_clean, flags=re.MULTILINE)

    # Delete words separated by two or more dots or dashes on a single line: A - B - C
    page_clean = re.sub(
        r"^([\w\s]+ [-Â·â€¢â€”|]+ ){2,}.*$", r"", page_clean, flags=re.MULTILINE
    )

    # Delete a line consisting of a single word:
    page_clean = re.sub(r"^\w+[ :-]?$", r"", page_clean, flags=re.MULTILINE)

    # Delete multiple line breaks
    page_clean = re.sub(r"\n{3,}", r"\n\n", page_clean)

    return page_clean


### Wikipedia scraper: takes a bz2 dump file and writes to a given file


def make_wiki(
    file_to_read,
    file_to_write,
    allowed_namespaces=["0"],
    max_line_read=float("inf"),
    min_article_len=0,
    max_article_count=float("inf"),
    max_word_count=float("inf"),
):
    full = open_bz2(file_to_read, line_limit=max_line_read)

    # Start and end indices of every page
    init_ind = [i for i, item in enumerate(full) if re.search("<page", item)]
    end_ind = [i for i, item in enumerate(full) if re.search("</page", item)]

    # Process each page

    article_count = 0
    word_count = 0
    for i in range(len(end_ind)):
        if i % 10000 == 0:
            print(str(round(i / float((len(end_ind))), 3) * 100) + "%")

        p_lines = full[init_ind[i] : end_ind[i] + 1]

        p = "".join(p_lines)

        title = re.search("<title>(.*)</title>", p).group(1)
        namespace = re.search("<ns>(.*)</ns>", p).group(1)

        if namespace in allowed_namespaces:
            # print title
            # print p

            p = wiki_clean(p)

            article_len = len(p.split())

            if article_len >= min_article_len:
                if article_count + 1 <= max_article_count:
                    if word_count <= max_word_count:
                        word_count += article_len
                        article_count += 1

                        f = open(file_to_write, "a", encoding="utf-8")

                        f.write(
                            "#Article "
                            + str(article_count)
                            + ": "
                            + title
                            + " ("
                            + str(article_len)
                            + " words)\n"
                        )
                        f.write(p)
                        f.write("\n\n\n")
                        f.close()

        if article_count == max_article_count:
            break
        if word_count > max_word_count:
            word_count -= article_len
            article_count -= 1
            break

    f = open(file_to_write, "a")

    f.write("#Total Article count: " + str(article_count) + "\n")
    f.write("#Total Word count: " + str(word_count))

    f.close()


####  MAIN CODE ###
cfg = utils.load_config()
in_dir = cfg["wiki-dump-dir"]

# Place the filepath to a folder containing Wikipedia Dump Files here
# in_dir = ''


# For Make_wiki below:

# Allowed Namespaces: which Wikipedia article types ('0' for articles)
# Maximum Lines to Read: for big bz2 files, restrict to a certain number of lines to go quicker
# Minimum Article Length: Exclude articles that contain than a certain number of words
# Maximum Article Count: Include only the first X number of articles
# Maximum Word Count: Stop running before reaching a certain maximum number of words


for f in listdir(in_dir):
    if str(f).endswith("bz2"):
        print(f)

        a = in_dir + "/" + f
        b = in_dir + "/" + re.sub(r"\-.*$", "", f) + ".txt"

        make_wiki(
            a,
            b,
            allowed_namespaces=["0"],
            max_line_read=20000000,
            min_article_len=10,
            max_article_count=float("inf"),
            max_word_count=20000000000,
        )
