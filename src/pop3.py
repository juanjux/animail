# -*- coding: UTF-8 -*-
#from animail import general, mailserver
import socket, re, os, tempfile, poplib, sys, rfc822, StringIO

try: import psyco
except ImportError: pass

import general, mailserver
from gettext import gettext
_ = gettext
aprint = general.aprint

class ConfigError(Exception): pass



class Pop3Server(mailserver.MailServer):
#--------------------------------------------------
    def __init__(self, *args):
        #test
        self.objpop = None
        self.deleted_msgs = []
        apply(mailserver.MailServer.__init__, (self,) + args)

        try:
            # Psyco increase speed about a 40% here...
            import psyco
            psyco.bind(self.get_message)
        except ImportError:
            pass

    # end def __init__
#--------------------------------------------------
    def stats(self):
        (self.nummesg, self.server_bytes_left) = self.objpop.stat()
#--------------------------------------------------
    def delmesg(self, msg):
        buffer = self.objpop.dele(msg['number'])
        if self.config.optv:
            print 'ISAY: DELE %d\nPOP3: %s'%(msg['number'],buffer)
        self.lmsg.remove(msg)
        self.deleted_msgs.append(msg)
    # end def delmesg
#--------------------------------------------------
    def delmesg2(self, msg): # Don't remove from list
        buffer = self.objpop.dele(msg['number'])
        if self.config.optv: print 'ISAY: DELE %d\nPOP3: %s' % (msg['number'],buffer)
        self.deleted_msgs.append(msg)
#--------------------------------------------------
    def get_header(self, msg, left):
        aprint(_("Looking header %d (%s)") % (msg['orignumber'], self.alias), general.VIOLET)
        header = self.objpop.top(int(msg['number']), 0)
        return header
    # end def get_header
#--------------------------------------------------
    def connect(self):
        self.lmsg = []
        if self.adress == '':
            raise ConfigError, _("Server address not given!!")

        if self.ssl:
            import popslib
            try:
                self.objpop = popslib.POP3S(self.adress, self.port)
            except socket.sslerror, err:
                aprint(_("SSL error while trying to connect to the server (%s), be sure that you have configured the correct port for POP3-SSL(usually 995)")%err,general.RED)
                exit() #Only exits thead
        else:
            self.objpop = poplib.POP3(self.adress, self.port)
        welcome = self.objpop.getwelcome()
        self.started()
        if self.protocol == 'APOP':
            lwelcome = welcome.split()
            lwelcome.reverse()
            self.timestamp = lwelcome[0]
        return welcome
        # end if
    # end def connect
#--------------------------------------------------
    def serv_exit(self):
        strg = self.objpop.quit()
        self.finished()
        if self.config.optv:
            print 'ISAY: QUIT'
        del self.lmsg
    # end def serv_exit
#--------------------------------------------------
    def auth(self):
        if self.protocol == 'POP3':
            buffer = self.objpop.user(self.name)
            if self.config.optv:
                print 'ISAY: USER %s\nPOP3: %s' % (self.name, buffer)
            buffer = self.objpop.pass_(self.passwd)
            if self.config.optv:
                print 'ISAY: PASS *\nPOP3: %s' % buffer
        elif self.protocol == 'APOP':
            import md5
            md5obj = md5.md5(''.join( (self.timestamp, self.passwd)) )
            digest = md5obj.digest()

            # digest to hexadecimal string conversion
            # in obfuscated and fast form:
            str_digest = "%02x"*len(digest) % tuple(map(ord, digest))

            buffer = self.objpop.apop(self.name, str_digest)
            if self.config.optv:
                print 'ISAY: APOP %s *\nPOP3: %s' % (self.name, buffer)
        # end if
    # end def auth
#--------------------------------------------------
    def make_list(self):

        optmax = self.config.optmax
        max_number = self.config.max_number
        optorder = self.config.optorder
        num = 0

        aprint(_("Getting message list (%s)") % self.alias, general.CYAN)
        self.lmsg = []
        if self.nummesg <= 0: return
        # FIXME: Until here this could go in an inherited parent class method

        listaresp = self.objpop.list()

        for msg in listaresp[1]:
            if not (optmax and (num > max_number)):
                num += 1
                (strtmp, sizetmp) = msg.split()
                tmpd = {}
                pok = int(strtmp)
                tmpd['number'] = pok
                tmpd['orignumber'] = pok
                tmpd['size'] = int(sizetmp)

                self.insert_to_list(tmpd, optorder)
            else:
                aprint(_("Message number limit reached"), general.RED)
                return
#-------------------------------------------------------------
    def getuidl(self, number):
        strg = self.objpop.uidl(number)
        (nada, nada, str_uidl) = strg.split()
        return str_uidl
#-------------------------------------------------------------
    def cleanup(self):
        aprint(_("Deleting already downloaded messages from POP3 server..."),general.YELLOW)
        for msg in self.deleted_msgs[:]:
            aprint(_("Deleting message %s") % msg['number'],general.RED)
            self.delmesg2(msg)
            self.deleted_msgs.remove(msg)
        self.objpop.quit()
        self.finished()
#-------------------------------------------------------------
    def get_message(self, msg, smtp, header, nmesg):
        msg_list = []
        iter = 0
        total = 0
        first = 1

        # Some alias to optimize the loop
        readline = self.objpop.file.readline
        #takefrom = general.takefrom

        (optv, optquiet, optsmtp, stderr_write,
        msg_size, server_bytes_left, optsyslog, optnotlog, optcolors) = self.optimize(msg)


        self.objpop._shortcmd('RETR %d' % msg['number'])
        while 1:
            iter += 1
            #if ((iter % 200) == 0) and optsmtp:
                #smtp.smtpobj.noop()
            buffer = readline()
            if buffer[-2:] == '\r\n':
                if buffer[-3:] == '.\r\n': pass
                else:
                    buffer = buffer[:-2] + '\n'

            if first:
                #fromm = takefrom(buffer)
                try:
                    rfcObj = rfc822.Message(StringIO.StringIO(buffer))
                    fromm = rfcObj.getheader('Return-Path').replace("<","").replace(">","")
                except AttributeError: # Return-Path is not the first line,well...
                    fromm = 'Unknown'
                first = 0
                if not optsyslog:
                    print general.colorize(_("From: %s") % fromm, general.YELLOW)
                #end if not optsyslog
            #end if first
            if not optv:
                lenb = len(buffer)
                total += lenb
                self.totalserv += lenb
                # De aquí para abajo podría ir en el padre pero se pierde mucho rendimiento (quiero
                # macros en Python YA!)
                if not optsyslog and not optquiet:
                    stderr_write('\r')
                    if iter % 5 == 0:
                        strtmp = general.colorize(_("Downloaded: "),general.YELLOW)
                        strtmp2 = general.colorize("%3.0f%%" % (total / ( (msg_size + 0.001) * 1.0) * 100.0), general.WHITE)
                        stderr_write(strtmp + strtmp2)

                    #end if iter % 5 == 0
                #end if not optsyslog and not optquiet
            #end if not optv

            if buffer == '.\r\n':
                return ''.join(msg_list), fromm, ''
            else:
                msg_list.append(buffer)
#------------------------------------------------------------------------
    def needs_cleanup(self):
        return 1
