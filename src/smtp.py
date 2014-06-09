# -*- coding: UTF-8 -*-

#from animail import AnimailMain, general 
import general, AnimailMain
import smtplib, rfc822
from socket import gethostname, error
from gettext import gettext
_ = gettext
aprint = general.aprint

def generatereply(toaddr):
    config = AnimailMain.Application.config
    fromaddr = config.replyaddress
    serv = smtplib.SMTP('localhost')
    (foo,emailaddr) = rfc822.parseaddr(config.replyaddress.strip())
    heads = ("Subject: %s [%s]\r\n\r\n" % (config.replysubject,emailaddr))
    if config.filewithreply == '':
        tmpmsg = general.ReplyDefaultStr
    else: 
        tmpmsg = ''.join(open(config.filewithreply).readlines())
    msg = heads + tmpmsg
    serv.sendmail(fromaddr, toaddr, msg)
    aprint(_("Reply succesfully send to %s") % toaddr, general.VIOLET)
    
    # It's necessary to always lock the write access to the repliedList since
    # is used globally 
    AnimailMain.Application.repLock.acquire()
    AnimailMain.Application.repliedList.append(toaddr)
    AnimailMain.Application.release_repLock()
    serv.quit()

def generateConfirmation(toaddr): 
    config = AnimailMain.Application.config
    (foo,fromaddr) = rfc822.parseaddr(config.replyaddress)
    serv = smtplib.SMTP('localhost')
    heads = ("Subject: %s [%s]\r\n\r\n" % (config.confirmsubject,fromaddr))
    if config.filewithreply == '':
        tmpmsg = general.ConfirmDefaultStr
    else:
        tmpmsg = ''.join(open(config.filewithreply).readlines())
    msg = heads + tmpmsg
    serv.sendmail(fromaddr, toaddr, msg)
    aprint(_("Confirmation succesfully send to %s") % toaddr, general.VIOLET)
    serv.quit()

class SmtpServer(object):
    def __init__(self):
        self.config = AnimailMain.Application.config
        
    def connect(self):
        try:
            self.hostname = gethostname()
        except error: 
            self.hostname = '127.0.0.1'
        try:
            self.smtpobj = smtplib.SMTP()
            buffer = self.smtpobj.connect(self.hostname, self.config.smtpport)
            if self.config.optv: print 'SMTP: %d %s' % (buffer[0], buffer[1])
        except error, x:
            return _('Error connecting to the SMTP %s') % str(x)
            
        buffer = self.smtpobj.helo('localhost')

        if self.config.optv: 
            print 'ISAY: HELO localhost\nSMTP: %d %s' % (buffer[0], buffer[1])
        return 'ok'


    def quit(self):
        try:
            self.smtpobj.quit()
            if self.config.optv: print _("Closing SMTP connection")
        except smtplib.SMTPException:
            if self.config.optv: print _("SMTP Error: Already Closed")

    def send(self, msgfile, resend, towho):
        if resend: destList = towho
        else:
            caduser = ''.join((self.config.sysuser, '@localhost'))
            destList = [caduser]

        if self.config.optv: print _("ISAY: (Sending the message to the SMTP)")

        for dest in destList:
            code = 0
            msgfile.seek(0)
            mail = msgfile.read()
            
            try:
                self.smtpobj.sendmail(dest, dest, mail)
            except smtplib.SMTPException, codestring:
                # First, let's check if the returned code is configured by the user
                # as a SMTP Spam rejection code and return the error tuple in that case:
                if self.config.usingsmtpspamcodes:
                    code = codestring[0]
                    for rejcode in self.config.smtpspamcodes:
                        # This try is neccesary because if the server disconnected us (because
                        # of a timeout, for example) code and rejcode will not be numbers
                        try:
                            if int(code) == int(rejcode): return codestring
                        except ValueError: pass


                # If it's not a spamcode (or the user has not configured Animail to consideer
                # some SMTP rejection codes as spam codes try to deliver using the sendmail
                # command as a fallback:
                self.connect()
                self.smtpobj.sendmail(dest, dest, mail)

