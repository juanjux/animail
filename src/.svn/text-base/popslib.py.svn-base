# -*- coding: UTF-8 -*-
"""A POP3 client class.

Based on the J. Myers POP3 draft, Jan. 96
"""

# Author: David Ascher <david_ascher@brown.edu>
#                [heavily stealing from nntplib.py]
# Updated: Piers Lauder <piers@cs.su.oz.au> [Jul '97]

# Example (see the test function at the end of this file)

TESTSERVER = "localhost"
TESTACCOUNT = "test"
TESTPASSWORD = "password"

# Imports

import socket, string, poplib

# Exception raised when an error or invalid response is received:

class error_proto(Exception): pass

# Standard Port
POP3_PORT = 995

# Line terminators (we always output CRLF, but accept any of CRLF, LFCR, LF)
CR = '\r'
LF = '\n'
CRLF = CR+LF


class POP3S(poplib.POP3):

    def __init__(self, host, port = POP3_PORT):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.ssl = socket.ssl(self.sock._sock, None, None)
        self.file = self.makefile('rb')
        self._debugging = 0
        self.welcome = self._getresp()

    def makefile(self, mode='r', bufsize=-1):
        return _fileobject(self.sock, self.ssl, mode, bufsize)

    def _putline(self, line):
        #if self._debugging > 1: print '*put*', `line`
        buf = '%s%s' % (line, CRLF)
        self.ssl.write(buf)

    def quit(self):
        """Signoff: commit changes on server, unlock mailbox, close connection."""
        try:
                resp = self._shortcmd('QUIT')
        except error_proto, val:
                resp = val
        self.file.close()
        self.sock.close()
        del self.file, self.sock, self.ssl
        return resp


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

        
if __name__ == "__main__":
    a = POP3S(TESTSERVER)
    print a.getwelcome()
    a.user(TESTACCOUNT)
    a.pass_(TESTPASSWORD)
    a.list()
    (numMsgs, totalSize) = a.stat()
    for i in range(1, numMsgs + 1):
        (header, msg, octets) = a.retr(i)
        print "Message ", `i`, ':'
        for line in msg:
                print '   ' + line
        print '-----------------------'
    a.quit()

