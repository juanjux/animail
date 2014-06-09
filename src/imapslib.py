# -*- coding: UTF-8 -*-
import re, socket, string, random, sys, imaplib

#       Globals

CRLF = '\r\n'
Debug = 0
IMAP4_PORT = 993
AllowedVersions = ('IMAP4REV1', 'IMAP4')        # Most recent first

#       Commands

Commands = {
        # name            valid states
        'APPEND':       ('AUTH', 'SELECTED'),
        'AUTHENTICATE': ('NONAUTH',),
        'CAPABILITY':   ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'),
        'CHECK':        ('SELECTED',),
        'CLOSE':        ('SELECTED',),
        'COPY':         ('SELECTED',),
        'CREATE':       ('AUTH', 'SELECTED'),
        'DELETE':       ('AUTH', 'SELECTED'),
        'EXAMINE':      ('AUTH', 'SELECTED'),
        'EXPUNGE':      ('SELECTED',),
        'FETCH':        ('SELECTED',),
        'LIST':         ('AUTH', 'SELECTED'),
        'LOGIN':        ('NONAUTH',),
        'LOGOUT':       ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'),
        'LSUB':         ('AUTH', 'SELECTED'),
        'NOOP':         ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'),
        'PARTIAL':      ('SELECTED',),
        'RENAME':       ('AUTH', 'SELECTED'),
        'SEARCH':       ('SELECTED',),
        'SELECT':       ('AUTH', 'SELECTED'),
        'STATUS':       ('AUTH', 'SELECTED'),
        'STORE':        ('SELECTED',),
        'SUBSCRIBE':    ('AUTH', 'SELECTED'),
        'UID':          ('SELECTED',),
        'UNSUBSCRIBE':  ('AUTH', 'SELECTED'),
        }

#       Patterns to match server responses

Continuation = re.compile(r'\+( (?P<data>.*))?')
Flags = re.compile(r'.*FLAGS \((?P<flags>[^\)]*)\)')
InternalDate = re.compile(r'.*INTERNALDATE "'
        r'(?P<day>[ 123][0-9])-(?P<mon>[A-Z][a-z][a-z])-(?P<year>[0-9][0-9][0-9][0-9])'
        r' (?P<hour>[0-9][0-9]):(?P<min>[0-9][0-9]):(?P<sec>[0-9][0-9])'
        r' (?P<zonen>[-+])(?P<zoneh>[0-9][0-9])(?P<zonem>[0-9][0-9])'
        r'"')
Literal = re.compile(r'.*{(?P<size>\d+)}$')
Response_code = re.compile(r'\[(?P<type>[A-Z-]+)( (?P<data>[^\]]*))?\]')
Untagged_response = re.compile(r'\* (?P<type>[A-Z-]+)( (?P<data>.*))?')
Untagged_status = re.compile(r'\* (?P<data>\d+) (?P<type>[A-Z-]+)( (?P<data2>.*))?')



class IMAP4S(imaplib.IMAP4):


        def open(self, host, port):
                """Setup 'self.sock' and 'self.file'."""
                self.port = IMAP4_PORT
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((host, self.port))
                self.ssl = socket.ssl(self.sock._sock,None,None)
                self.file = self.makefile('r')

        def makefile(self, mode='r', bufsize=-1):
                return _fileobject(self.sock, self.ssl, mode, bufsize)


        def logout(self):
                """Shutdown connection to server.

                (typ, [data]) = <instance>.logout()

                Returns server 'BYE' response.
                """
                self.state = 'LOGOUT'
                try: typ, dat = self._simple_command('LOGOUT')
                except: typ, dat = 'NO', ['%s: %s' % sys.exc_info()[:2]]
                self.file.close()
                self.sock.close()
                del self.ssl
                if self.untagged_responses.has_key('BYE'):
                        return 'BYE', self.untagged_responses['BYE']
                return typ, dat


        def _command(self, name, *args):

                if self.state not in Commands[name]:
                        self.literal = None
                        raise self.error(
                        'command %s illegal in state %s' % (name, self.state))

                for typ in ('OK', 'NO', 'BAD'):
                        if self.untagged_responses.has_key(typ):
                                del self.untagged_responses[typ]

                if self.untagged_responses.has_key('READ-ONLY') \
                and not self.is_readonly:
                        raise self.readonly('mailbox status changed to READ-ONLY')

                tag = self._new_tag()
                data = '%s %s' % (tag, name)
                for arg in args:
                        if arg is None: continue
                        data = '%s %s' % (data, self._checkquote(arg))

                literal = self.literal
                if literal is not None:
                        self.literal = None
                        if type(literal) is type(self._command):
                                literator = literal
                        else:
                                literator = None
                                data = '%s {%s}' % (data, len(literal))

                try:
                        buf = '%s%s' % (data, CRLF)
                        self.ssl.write(buf)
                except socket.error, val:
                        raise self.abort('socket error: %s' % val)

                if literal is None:
                        return tag

                while 1:
                        # Wait for continuation response

                        while self._get_response():
                                if self.tagged_commands[tag]:   # BAD/NO?
                                    return tag

                        # Send literal

                        if literator:
                                literal = literator(self.continuation_response)

                        try:
                                self.ssl.send(literal)
                                self.ssl.send(CRLF)
                        except socket.error, val:
                                raise self.abort('socket error: %s' % val)

                        if not literator:
                                break

                return tag


class _fileobject:

        def __init__ (self, sock, ssl, mode, bufsize):
                self._sock = sock
                self._ssl = ssl
                self._mode = mode
                if bufsize < 0:
                        bufsize = 512
                self._rbufsize = max(1,bufsize)
                self._wbufsize = bufsize
                self._wbuf = self._rbuf = ""

        def close (self):
                try:
                        if self._sock:
                                self.flush()
                finally:
                        self._sock = None

        def __del__ (self):
                self.close()

        def flush (self):
                if self._wbuf:
                        self._sock.write(self._wbuf,len(self._wbuf))
                self._wbuf = ""

        def fileno (self):
                return self._sock.fileno()

        def write (self, data):
                self._wbuf += data
                if self._wbufsize == 1:
                        if '\n' in data:
                                self.flush()
                else:
                        if len(self._wbuf) >= self._wbufsize:
                                self.flush()

        def writelines (self, lst):
                filter(self._sock.send,lst)
                self.flush()

        def read (self, n=-1):
                if n >= 0:
                        while len(self._rbuf) < n:
                                new = self._ssl.read(self._rbufsize)
                                if not new: break
                                self._rbuf += new
                        data,self._rbuf = self._rbuf[:n],self._rbuf[n:]
                        return data
                while 1:
                        new = self._ssl.read(self._rbufsize)
                        if not new: break
                        self._rbuf += new
                data,self._rbuf = self._rbuf,""
                return data

        def readline (self):
                data = ""
                i = string.find(self._rbuf,'\n')
                while i < 0:
                        new = self._ssl.read(self._rbufsize)
                        if not new: break
                        i = string.find(new,'\n')
                        if i >= 0:
                            i += len(self._rbuf)
                        self._rbuf += new
                if i < 0:
                    i = len(self._rbuf)
                else:
                    i += 1
                data,self._rbuf = self._rbuf[:i],self._rbuf[i:]
                return data

        def readlines (self):
                l = []
                while 1:
                        line = self.readline()
                        if not line: break
                        l.append(line)
                return l


if __name__ == '__main__':

    import getopt, getpass

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'd:')
    except getopt.error, val:
        pass

    for opt,val in optlist:
        if opt == '-d':
            Debug = int(val)

    if not args: args = ('',)

    host = args[0]

    USER = getpass.getuser()
    PASSWD = getpass.getpass("IMAP password for %s on %s: " % (USER, host or "localhost"))

    test_mesg = 'From: %(user)s@localhost%(lf)sSubject: IMAP4 test%(lf)s%(lf)sdata...%(lf)s' % {'user':USER, 'lf':CRLF}
    test_seq1 = (
    ('login', (USER, PASSWD)),
    ('create', ('/tmp/xxx 1',)),
    ('rename', ('/tmp/xxx 1', '/tmp/yyy')),
    ('CREATE', ('/tmp/yyz 2',)),
    ('append', ('/tmp/yyz 2', None, None, test_mesg)),
    ('list', ('/tmp', 'yy*')),
    ('select', ('/tmp/yyz 2',)),
    ('search', (None, 'SUBJECT', 'test')),
    ('partial', ('1', 'RFC822', 1, 1024)),
    ('store', ('1', 'FLAGS', '(\Deleted)')),
    ('namespace', ()),
    ('expunge', ()),
    ('recent', ()),
    ('close', ()),
    )

    test_seq2 = (
    ('select', ()),
    ('response',('UIDVALIDITY',)),
    ('uid', ('SEARCH', 'ALL')),
    ('response', ('EXISTS',)),
    ('append', (None, None, None, test_mesg)),
    ('recent', ()),
    ('logout', ()),
    )

    def run(cmd, args):
        _mesg('%s %s' % (cmd, args))
        typ, dat = apply(getattr(M, cmd), args)
        _mesg('%s => %s %s' % (cmd, typ, dat))
        return dat

    try:
        M = IMAP4S(host)
        _mesg('PROTOCOL_VERSION = %s' % M.PROTOCOL_VERSION)
        _mesg('CAPABILITIES = %s' % `M.capabilities`)

        for cmd,args in test_seq1:
            run(cmd, args)

        for ml in run('list', ('/tmp/', 'yy%')):
            mo = re.match(r'.*"([^"]+)"$', ml)
            if mo: path = mo.group(1)
            else: path = ml.split()[-1]
            run('delete', (path,))
        for cmd,args in test_seq1:
            run(cmd, args)

        for ml in run('list', ('/tmp/', 'yy%')):
            mo = re.match(r'.*"([^"]+)"$', ml)
            if mo: path = mo.group(1)
            else: path = ml.split()[-1]
            run('delete', (path,))

        for cmd,args in test_seq2:
            dat = run(cmd, args)

            if (cmd,args) != ('uid', ('SEARCH', 'ALL')):
                continue

            uid = dat[-1].split()
            if not uid: continue
            run('uid', ('FETCH', '%s' % uid[-1],
                    '(FLAGS INTERNALDATE RFC822.SIZE RFC822.HEADER RFC822.TEXT)'))

        print '\nAll tests OK.'

    except:
        print '\nTests failed.'

        if not Debug:
            print '''
If you would like to see debugging output,
try: %s -d5
''' % sys.argv[0]

        raise

