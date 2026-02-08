import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
voids = set(["area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"]) 

with open(path, 'r', encoding='utf-8') as f:
    s = f.read()

# remove comments
s_nocomments = re.sub(r'<!--.*?-->', '', s, flags=re.DOTALL)
# find tags
pattern = re.compile(r'<(/?)\s*([a-zA-Z0-9\-]+)([^>]*)>', re.IGNORECASE)
stack = []
errors = []
pos = 0
for m in pattern.finditer(s_nocomments):
    full = m.group(0)
    closing = m.group(1) == '/'
    tag = m.group(2).lower()
    attrs = m.group(3)
    start = m.start()
    # skip doctype
    if tag.startswith('!') or tag == '?xml':
        continue
    # skip self-closing via slash
    self_closing = attrs.strip().endswith('/')
    if closing:
        if not stack:
            errors.append((start, f"Closing tag </{tag}> with no open tag"))
        else:
            top = stack.pop()
            if top != tag:
                errors.append((start, f"Mismatched closing tag </{tag}>; expected </{top}>"))
    else:
        if tag in voids or self_closing:
            continue
        stack.append(tag)

if stack:
    for t in reversed(stack):
        errors.append((len(s_nocomments), f"Unclosed tag <{t}>") )

if errors:
    print('FOUND ERRORS:')
    for pos, msg in errors:
        print(msg)
    sys.exit(1)
else:
    print('No nesting errors found.')
    sys.exit(0)
