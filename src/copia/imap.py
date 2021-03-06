# -*- coding: UTF-8 -*-
#from animail import AnimailMain, mailserver, general
import mailserver
import imaplib, tempfile, socket, os, sys

try: import psyco
except ImportError: pass

from general import colorize, CYAN, RED, GREEN, YELLOW, VIOLET, WHITE, aprint
from gettext import gettext
from thread import exit

_ = gettext

"""
TODO:

FIXME: Test that the expunge did OK looking at the returned message
FIXME: Capture some exceptions
"""

class ConfigError(Exception): pass

class Imap4Server(mailserver.MailServer):
#--------------------------------------------------
    def __init__(self, *args):
        self.objimap = None
        apply(mailserver.MailServer.__init__, (self,) + args)

        try:
            # Psyco increase speed about a 40% here...
            psyco.bind(self.get_message)
        except NameError:
            pass


#--------------------------------------------------
    def takefrom(self, nummsg):
        (typ, data) = self.objimap.fetch(nummsg,
                                '(BODY[HEADER.FIELDS (FROM)])')

        # This returns something in data like:
        # [('1 (BODY[HEADER.FIELDS ("FROM")] {56}', 'From: "Pepito Perez \\[NR\\]"  <polompos@pok.org>\015\012\015\012'), ')']

        # So let put it pretty:
        try:
            if self.config.optv: print 'IMAP4: %s' % typ
            from_ = data[0][1].strip()
            from_ = from_.split(':')[1].strip()
            if from_.find('<') != -1:
                from_ = from_.split('<')[1].strip()
                from_ = from_.replace('>', '')
        except IndexError:
            from_ = "Unknown"

        return from_
#--------------------------------------------------
    def stats(self):
        (typ, data) = self.objimap.search(None, 'ALL')
        self.numbers_list = data[0].split(' ')
        if self.config.optv: print 'IMAP4: %s' % typ

        try:
            self.make_list_real()
        except IndexError: self.lmsg = []
#--------------------------------------------------
    def delmesg(self, msg):
        (buff, data) = self.objimap.store(msg['number'], '+flags', '\Seen \Deleted')
        # We issue an expunge here, FIXME this should be configurable to allow and
        # expunge every n messages instead of an expunge after every message deletion
        self.objimap.expunge()
        self.update_msg_numbers(msg['number'])
        if not self.some_deleted:
            self.some_deleted = True
        if self.config.optv:
            print 'ISAY: STORE %d +flags (\Seen \Deleted)' % msg['number']
            print 'IMAP4: %s' % buff
        #self.lmsg.remove(msg)
#--------------------------------------------------
    def get_header(self, msg, left):
        if self.config.optexpresion:
            aprint(_("Looking header %d (%s)") % (msg['orignumber'], self.alias), VIOLET)

        typ, data = self.objimap.fetch(msg['number'], '(BODY[HEADER])')
        if self.config.optv: print 'IMAP4: %s' % typ
        return data[0][1]
#--------------------------------------------------
    def connect(self):
        self.lmsg = []
        if self.adress == '':
            raise ConfigError, _("Server address not given!!")
        if self.ssl:
            import imapslib
            try:
                self.objimap = imapslib.IMAP4S(self.adress, self.port)
            except socket.sslerror, err:
                aprint(_("SSL error while trying to connect to the server (%s), be sure that you have configured the correct port for IMAP4-SSL(usually 993)")%err,RED)
                exit() #Only exits thead
        else:
            self.objimap = imaplib.IMAP4(self.adress, self.port)
        self.started()
#--------------------------------------------------
    def auth(self):
        if self.config.optv:
            print 'LOGGING IN IMAP SERVER (USER: ',self.name,' PASS: xxxxxx'
        self.objimap.login(self.name, self.passwd)
        self.nummesg = int( self.objimap.select()[1][0] )
#--------------------------------------------------
    def make_list(self):
        pass

#--------------------------------------------------
    def make_list_real(self):
        optmax = self.config.optmax
        max_number = self.config.max_number
        optorder = self.config.optorder
        num = 0

        aprint(_("Getting message list (%s)") % self.alias, CYAN)
        self.lmsg = []
        if self.nummesg <= 0: 
            return

        for msg in range(1, self.nummesg + 1):
            if not (optmax and (num > max_number)):
                    num += 1
                    typ, data = self.objimap.fetch(msg, '(RFC822.SIZE)')
                    if self.config.optv: print 'IMAP4: %s' % typ
                    lst = data[0].split(' ')

                    tmpd = {}
                    tmpd['size'] = int(lst[2][:-1])
                    pok = int(msg)
                    tmpd['number'] = pok
                    tmpd['orignumber'] = pok

                    self.insert_to_list(tmpd, optorder)
                    self.server_bytes_left += tmpd['size']
            else:
                    aprint(_("Message number limit reached"), RED)
                    return
#--------------------------------------------------
    # This method is used to update the message numbers to the 
    # ones that the imap server will have every time we do an expunge
    def update_msg_numbers(self,number):
        for msg in self.lmsg:
            if msg['number'] > number: msg['number'] -= 1
#--------------------------------------------------
    def get_message(self, msg, smtp, header, nmesg):
        #Some alias to optimize the loop
        readline = self.objimap._get_line

        (optv, optquiet, optsmtp, stderr_write, msg_size, server_bytes_left,\
        optsyslog, optnotlog, optcolors) = self.optimize(msg)

        #if optsmtp:
            #smtp_noop = smtp.smtpobj.noop

        total = 0
        msg_list = []
        fromm = self.takefrom(msg['number'])
        if not optsyslog: print colorize(_("From: %s") % fromm, YELLOW)
        strg = '999 FETCH ' + str(msg['number']) + ' BODY[TEXT]\n'

        if self.ssl: self.objimap.ssl.write(strg)
        else: self.objimap.sock.send(strg)

        linea = readline()
        tokens = linea.split('{')
        try:
            msg_size = int(tokens[len(tokens) - 1].split('}')[0])
        except ValueError:
            msg_size = 0
        iter = 0
        first = True

        #This condition is just another kludge, but works and is easier (and more realiable) than
        #the bytes-counting alternative, if you know of some server giving a different fetch
        #completed message please tell me
        lowline = linea.lower()
        while (lowline[0:22] != '999 ok fetch completed') and (lowline[0:16] != '999 ok completed'):
            iter += 1
            #if ((iter % 200) == 0) and optsmtp:
                    #smtp_noop()
            if first:
                    self.server_bytes_left -= len(header)
                    first = False
            #end if first
            linea = readline() + '\n'
            msg_list.append(linea)

            lenb = len(linea) - 1
            total += lenb
            self.totalserv += lenb

            if not optv:
                    self.totalserv += len(linea)
                    # De aquí para abajo podría ir en el padre, pero sería caro en rendimiento
                    # (para cuando macros para Python?)
                    if not optsyslog and not optquiet:
                        stderr_write('\r')
                        if iter % 5 == 0:
                            strtmp = colorize(_("Downloaded: "), YELLOW)
                            strtmp2 = colorize("%3.0f%%" % (total / ( (msg_size + 0.001) * 1.0) * 100.0), WHITE)
                            stderr_write(strtmp + strtmp2)
            lowline = linea.lower()
        #end while
        if not self.config.optexpresion: header = self.get_header(msg, 0)
        else: header = '' #Already given in look_messages
        return ''.join(msg_list[:-2]), fromm, header
#--------------------------------------------------
    def serv_exit(self):
        if self.optdelete and self.some_deleted:
            #aprint(_("Deleting marked messages..."),YELLOW)
            self.objimap.expunge()
        self.objimap.logout()
        self.finished()
        self.num_trans = 0
#--------------------------------------------------
    def cleanup(self):
        pass
        #aprint(_("Deleting already downloaded messages from IMAP4 server..."),YELLOW)
        #self.objimap.expunge()
        #self.objimap.logout()
        #aprint(_("...done"),YELLOW)
        #self.finished()
#-�------------------------------------------------
    def needs_cleanup(self):
        return 0


