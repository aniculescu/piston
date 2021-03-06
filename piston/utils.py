import os
import sys
import frontmatter
import time
from datetime import datetime
import re
import logging
log = logging.getLogger(__name__)


def constructIdentifier(a, p):
    return "@%s/%s" % (a, p)


def sanitizePermlink(permlink):
    permlink = re.sub("_|\s|\.", "-", permlink)
    permlink = re.sub("[^\w-]", "", permlink)
    permlink = permlink.lower()
    return permlink


def derivePermlink(title, parent_permlink=None):
    permlink = ""
    if parent_permlink:
        permlink += "re-"
        permlink += parent_permlink
        permlink += "-" + formatTime(time.time())
    else:
        permlink += title

    return sanitizePermlink(permlink)


def resolveIdentifier(identifier):
    match = re.match("@?([\w\-\.]*)/([\w\-]*)", identifier)
    if not hasattr(match, "group"):
        log.error("Invalid identifier")
        sys.exit(1)
    return match.group(1), match.group(2)


def yaml_parse_file(args, initial_content):
    message = None

    if args.file and args.file != "-":
        if not os.path.isfile(args.file):
            raise Exception("File %s does not exist!" % args.file)
        with open(args.file) as fp:
            message = fp.read()
    elif args.file == "-":
        message = sys.stdin.read()
    else:
        import tempfile
        from subprocess import Popen
        EDITOR = os.environ.get('EDITOR', 'vim')
        # prefix = ""
        # if "permlink" in initial_content.metadata:
        #   prefix = initial_content.metadata["permlink"]
        with tempfile.NamedTemporaryFile(
            suffix=b".md",
            prefix=b"piston-",
            delete=False
        ) as fp:
            # Write initial content
            fp.write(bytes(frontmatter.dumps(initial_content), 'utf-8'))
            fp.flush()
            # Define parameters for command
            args = [EDITOR]
            if re.match("gvim", EDITOR):
                args.append("-f")
            args.append(fp.name)
            # Execute command
            Popen(args).wait()
            # Read content of file
            fp.seek(0)
            message = fp.read().decode('utf-8')

    try :
        meta, body = frontmatter.parse(message)
    except:
        meta = initial_content.metadata
        body = message

    # make sure that at least the metadata keys of initial_content are
    # present!
    for key in initial_content.metadata:
        if key not in meta:
            meta[key] = initial_content.metadata[key]

    return meta, body


def formatTime(t) :
    """ Properly Format Time for permlinks
    """
    return datetime.utcfromtimestamp(t).strftime("%Y%m%dt%H%M%S%Z")
