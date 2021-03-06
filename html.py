#!/usr/bin/env python
# Tim Henderson
# tim.tadh@gmail.com

import os, sys, subprocess, re
from getopt import getopt, GetoptError
#import markdown

usage_message = \
'''usage: html.py --css=style.css file.md'''

extended_message = \
'''Options
    -h, help                      print this message
    -t, title=[title]             give the html page a title
    -c, css=[file]                give the location of the CSS to include
    -s, stdin                     read from stdin instead of file
    -H, html                      treat the file as html instead of markdown
                                    (assume it is a partial file with no body
                                    tag).
'''

error_codes = {
    'usage':1,
    'file_not_found':2,
    'option':3,
    'args':4,
}

def log(*msgs):
    for msg in msgs:
        print >>sys.stderr, msg,
    print >>sys.stderr

def usage(code=None):
    '''Prints the usage and exits with an error code specified by code. If code
    is not given it exits with error_codes['usage']'''
    log(usage_message)
    if code is None:
        log(extended_message)
        code = error_codes['usage']
    sys.exit(code)

# def format(text): return markdown.markdown(text)

def which(program):
    which = subprocess.Popen(['which', program], stdout=subprocess.PIPE)
    out, err = which.communicate()
    if which.returncode != 0:
        return False
    return out.strip()

def format(text):
    pandoc_path = which('pandoc')
    if pandoc_path == False:
        return markdown.markdown(text.decode('utf8')).encode('utf8')
    def process(line):
        sline = line.strip()
        regex = r'\\title\{(.*)\}'
        match = re.match(regex, sline)
        log(match, regex, sline)
        if match:
            title = match.groups()[0]
            return "# " + title
        return line
    text = '\n'.join(process(line) for line in text.split('\n'))
    pandoc = subprocess.Popen(
        [pandoc_path, '--mathml', '-f', 'markdown', '-t', 'html', '-5'], 
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = pandoc.communicate(text)
    if pandoc.returncode != 0:
        raise RuntimeError, err
    return out


def css(path):
    if path is None:
        return ''
    f = open(path, 'r')
    s = f.read()
    f.close()
    return s.strip()

def header(title, css_path=None):
    return \
'''
<!doctype html>
<head>
<meta charset="utf-8">
<title>%(title)s</title>
<style>
%(style)s
</style>
</head>
''' % {'title':title, 'style':css(css_path)}

def body(text, mark):
    if mark:
        text = format(text)
    return \
'''
<body>
%(body)s
</body>
</html>
''' % {'body':text}


def main(args):
    try:
        opts, args = getopt(args,
            'hc:t:Hs',
            ['help', 'css=', 'title=', 'html', 'stdin']
        )
    except GetoptError, err:
        log(err)
        usage(error_codes['option'])

    title = 'A Page'
    css = os.path.join(os.path.dirname(__file__), 'default.css')
    assert os.path.exists(css)
    html = False
    stdin = False
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-c', '--css'):
            css = arg
            if not os.path.exists(css):
                log('File "%s" does not exist' % css)
                usage(error_codes['file_not_found'])
        elif opt in ('-t', '--title'):
            title = arg
        elif opt in ('-H', '--html'):
            html = True
        elif opt in ('-s', '--stdin'):
            stdin = True

    if len(args) != 1 and not stdin:
        log('One an only one file is allowed to be built at a time, you gave:')
        log(str(args))
        usage(error_codes['args'])
    elif len(args) == 0 and not stdin:
        log('One an only one file is allowed to be built at a time, you gave:')
        log(str(args))
        usage(error_codes['args'])



    if stdin:
        text = sys.stdin.read()
    else:
        file_path = args[0]
        if not os.path.exists(file_path):
            log('File "%s" does not exist' % file_path)
            usage(error_codes['file_not_found'])
        with open(file_path, 'r') as f:
            text = f.read().strip()
    text = text
    print header(title, css)
    print body(text, mark=(not html))

if __name__ == '__main__':
    main(sys.argv[1:])

