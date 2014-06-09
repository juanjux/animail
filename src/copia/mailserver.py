# -*- coding: UTF-8 -*-
#from animail import AnimailMain, general, smtp
import socket, re, os, sys, tempfile, time, stat,rfc822,StringIO,fcntl, mailbox, smtplib

try: import psyco
except ImportError: pass

import AnimailMain, general, smtp
from smtplib import SMTPException
from gettext import gettext

_ = gettext
aprint = general.aprint

#re_escapeLFNL = re.compile(r'', re.MULTILINE)

re_wuimap = re.compile('X-IMAP:')

class mboxException(Exception):
        pass

class maildirException(Exception):
        pass

class MailServer(object):
        def __init__(self, adress, name, passwd, port):
        
            self.nummesg = 0
            # Bytes totales que quedan en el servidor x transferir:
            self.server_bytes_left = 0
            self.totalserv = 0
            self.downloaded = []
            self.adress = adress
            self.name = name
            self.passwd = passwd
            self.port = port
            self.config = AnimailMain.Application.config
            self.num_trans = 0
            self.deliverycount = 0
            self.some_deleted = False
            self.info = {}
            self.lmsg = []
            self.clean_session = True
            self.error_time = 0
            try:
                psyco.bind(self.process_body)
                psyco.bind(self.look_message)
            except NameError:
                pass

#--------------------------------------------------
        def optimize(self, msg):
            optv = self.config.optv
            optquiet = self.config.optquiet
            optsmtp = self.config.optsmtp
            stderr_write = sys.stderr.write
            msg_size = msg['size']
            server_bytes_left = self.server_bytes_left
            optsyslog = self.config.optsyslog
            optnotlog = self.config.optnotlog
            optcolors = self.config.optcolors

            return (optv, optquiet, optsmtp,
                stderr_write, msg_size, server_bytes_left, optsyslog,
                            optnotlog, optcolors)

#--------------------------------------------------
        def insert_to_list(self, tmpd, order):
            #lmsg is a member of the childs
            if order == 'small':
                    general.ins_ordered_inv(self.lmsg, tmpd)
            elif order == 'big':
                    general.ins_ordered(self.lmsg, tmpd)
            else: self.lmsg.append(tmpd)
#--------------------------------------------------
        def delmesg(self, msg): pass
        def delmesg2(self, msg): pass
        def connect(self): pass
        def serv_exit(self): pass
        def auth(self): pass
        def make_list(self): pass
        def get_header(self, msg, left): pass
        def stats(self): pass
        def clean(self): pass
 #--------------------------------------------------
        def finished(self):
            self.clean_session = True
#--------------------------------------------------
        def started(self):
            self.clean_session = False
#--------------------------------------------------
        def process_body(self, body):
            return general.re_escapefrom.sub ('>\g<gts>From ', body)
#--------------------------------------------------
        def deliver_smtp(self, header, body, fromm, smtp):
            tmpfile = open(tempfile.mktemp(), 'w+')
            os.chmod(tmpfile.name, 0600)

            if self.__class__.__name__ != "Pop3Server":
                    tmpfile.write(header)

            tmpfile.write(self.process_body(body))

            spamreject = smtp.send(tmpfile, self.optresend, self.towho)
            if spamreject != None:
                if spamreject[1] != "":
                    aprint(_("The SMTP rejected the message using a configured SMTPSpamCode (%d): Deleting it from the remote server (SMTP: %s)") % (spamreject[0], spamreject[1]),general.RED)
            tmpfile.close()
            os.unlink(tmpfile.name)
#---------------------------------------------------
        def deliver_pipe(self, header, body, fromm, smtp):
            #FIXME: Add error checking and exceptions
            if self.delivery == 'pipe':
                    pipeCmd = self.sendmailcmd
            else:
                    pipeCmd = self.config.sendmailcmd

            tmpfile = open(tempfile.mktemp(), 'w+')
            os.chmod(tmpfile.name, 0600)

            if self.__class__.__name__ != "Pop3Server":
                    tmpfile.write(header)

            tmpfile.write(self.process_body(body))

            general.PipeToCmd(tmpfile,self.optresend,self.towho,pipeCmd)
            tmpfile.close()
            os.unlink(tmpfile.name)
#----------------------------------------------------
        def write_mbox(self, mbox, header, body, fromm):
            try:
                    fcntl.flock(mbox.fileno(), fcntl.LOCK_EX)
                    mbox.seek(0,2)
                    (foo,emailaddr) = rfc822.parseaddr(fromm)
                    strfromm = 'From %s' % emailaddr + ' ' + general.take_date() + '\n'
                    mbox.write(strfromm)
                    if self.__class__.__name__ != "Pop3Server":
                                mbox.write(header)
                    if body[:-1] != '\n': body += '\n'
                    mbox.write(self.process_body(body))
                    mbox.flush()
                    fcntl.flock(mbox.fileno(), fcntl.LOCK_UN)
                    mbox.close()
            except IOError, x:
                    try:
                                fcntl.flock(mbox.fileno(), fcntl.LOCK_UN)
                                mbox.close()
                    except:
                                pass
                    raise mboxException, _("Failure writing to mbox file '%s' (%s)") % (mbox.name,x)
#------------------------------------------------------
        def deliver_mbox(self, header, body, fromm, smtp):
            try:
                if self.delivery == 'mbox':
                        mbox = open(self.mbox, 'a+')
                else:
                        mbox = open(self.config.mboxfile, 'a+')
                self.write_mbox(mbox, header, body, fromm)
            except IOError, x:
                raise mboxException,_("Failure writing or opening the mbox file '%s' (%s)") % (mbox.name,x)
#------------------------------------------------------
        def deliver_maildir(self, header, body, fromm, smtp):
            '''Adapted (mostly copied) from Charles Cazabon's getmail
            <getmail @ discworld.dyndns.org>'''

            if self.delivery == 'maildir':
                    Maildirpath = self.maildir
            else:
                    Maildirpath = self.config.maildir

            self.info['time'] = int(time.time())
            self.info['deliverycount'] = self.deliverycount
            self.info['hostname'] = socket.gethostname()
            self.info['pid'] = os.getpid()
            filename = '%(time)s.%(pid)s_%(deliverycount)s.%(hostname)s' % self.info

            fname_tmp = os.path.join(Maildirpath, 'tmp', filename)
            fname_new = os.path.join(Maildirpath, 'new', filename)

            if not os.path.exists(Maildirpath):
                    raise maildirException, _("Maildir '%s' was not found") % Maildirpath

            if not os.path.exists(os.path.join(Maildirpath, 'tmp')):
                    os.mkdir(os.path.join(Maildirpath, 'tmp'), 0700)

            if not os.path.exists(os.path.join(Maildirpath, 'new')):
                    os.mkdir(os.path.join(Maildirpath, 'new'), 0700)

            if not os.path.exists(os.path.join(Maildirpath, 'cur')):
                    os.mkdir(os.path.join(Maildirpath, 'cur'), 0700)

            if os.path.exists(fname_tmp):
                    raise maildirException, fname_tmp + _("already exist")
            if os.path.exists(fname_new):
                    raise maildirException, fname_tmp + _("already exist")

            s_maildir = os.stat(Maildirpath)
            maildir_owner = s_maildir[stat.ST_UID]
            maildir_group = s_maildir[stat.ST_GID]

            try:
                    f = open(fname_tmp, 'wb')
                    try:
                                os.chown(fname_tmp, maildir_owner, maildir_group)
                    except OSError:
                                pass
                    os.chmod(fname_tmp, 0600)
                    if self.__class__.__name__ != "Pop3Server":
                                f.write(header)
                    f.write(body)
                    f.close()
            except IOError:
                    raise maildirException, _("failure writing file ") + fname_tmp

            try:
                    os.rename(fname_tmp, fname_new)
            except OSError:
                    raise maildirException, _("failure renaming '%s' to '%s'") \
                                    % (fname_tmp, fname_new)

            self.deliverycount += 1
#------------------------------------------------------
        def look_message(self,msg, logAgent, indice_log, left, smtpobj):
            """ Look a message header and delete it if matchs some regular expresion
            of the list given by the user in the filterfile.
            """
            #FIXME: This need reorganization
            # Some alias to optimize the "for patron in lfilters" loop
            # (yeah, this speed up things a lot)
            optnotlog = self.config.optnotlog
            lfilters = self.config.lfilters
            lfilterscomp = self.config.lfilterscomp
            laccepted = self.config.laccepted
            lacceptedcomp = self.config.lacceptedcomp
            laterReply = False
            isConfirmation = False
            notAccepted = False
            resultWUIMAP = None

            re_compile = re.compile

            if self.config.optsize and (msg['size'] >= self.config.max_size):
                    aprint(_("Message %d size exceed limit (%d), deleting it") % (msg['orignumber'], self.config.max_size), general.RED)
                    if not optnotlog:
                                logAgent.incident(indice_log, _("Message %d deleted, size limit reached") %
                                                        msg['orignumber'])
                    self.server_bytes_left = self.server_bytes_left - msg['size']
                    self.delmesg(msg)
                    return ('delete', None, None)

            listacab = self.get_header(msg, left)

            #FIXME: This is protocol-dependent, don't fit in the base class...
            if self.protocol == 'POP3':
                    header = '\n'.join(listacab[1])
            elif self.protocol == 'IMAP4': header = listacab

            rfcObj = rfc822.Message(StringIO.StringIO(header))
            fromwho = rfcObj.getheader('From')
            (foo,emailaddr) = rfc822.parseaddr(fromwho)

            # Check if the message is one of those pesky 'DON'T DELETE THIS MESSAGE, FOLDER INTERNAL DATA'
            if msg['orignumber'] == 1:
                resultWUIMAP = re_wuimap.search(header)
                if resultWUIMAP is not None:
                    aprint(_("Ignoring message %d: DONTDELETETHISMESSAGE type message") % (msg['orignumber']), general.RED)
                    return ('wuimap', None, fromwho)

            if self.config.notInAccept == 'reply':
                    (foo,emailaddrReply) = rfc822.parseaddr(self.config.replyaddress.strip())
                    comp = re_compile('Subject:' + '.*' + self.config.replysubject + ' ' + '\[' + emailaddrReply + '\]' , re.M)
                    isMatch = comp.search(header)

                    if isMatch is not None: #it's a reply to an Animail message
                                aprint(_("We've an address confirmation from %s, recovering postergated messages") % fromwho, general.VIOLET)
                                self.recoverDelayed(emailaddr, smtpobj)
                                if self.config.autoacceptconfirm:
                                    faccept = open(self.config.nacceptfile, 'a+')
                                    faccept.seek(0,2)
                                    faccept.write(emailaddr)
                                    faccept.write('\n')
                                    aprint(_("%s Address added to auto-accept file") % emailaddr,general.VIOLET)
                                    try:
                                        smtp.generateConfirmation(emailaddr)
                                    except smtplib.SMTPException, x:
                                        aprint(_("SMTP Error delivering confirmation to %s, reply not sent: %s") % (fromwho, x), general.RED)
                                isConfirmation = True

            #Check if the message match some regexp in the auto-accept file
            #FIXME: Made a method of this: check_filter(self,header) returns None or the pattern
            # (problem: it could slow down animail a lot)
            if self.config.optaccept:
                    for comp in lacceptedcomp:
                        #comp = re_compile(patron.strip(), re.M)
                        result = comp.search(header)

                        if result is not None:
                            #Message in the auto-accepted list so auto-accepting it
                            return ('pass',header, fromwho)

                    #Delete, reply or do nothing (as configured) if the message don't match the auto-accept file
                    if self.config.notInAccept == 'delete':
                        aprint(_("Deleting message %d: Don't match anything in accept file") % msg['orignumber'],general.RED)
                        if not optnotlog:
                            logAgent.append_filtered(indice_log,"%s (Not in accept file)"%fromwho,msg['size'])
                        self.server_bytes_left = self.server_bytes_left - msg['size']
                        self.delmesg(msg)
                        return ('delete',None, fromwho)
                    elif self.config.notInAccept == 'none':
                        pass
                    elif self.config.notInAccept == 'ignore':
                        notAccepted = True
                    elif self.config.notInAccept == 'reply':
                        if not isConfirmation: laterReply = True #Gives the opportunity to filter it

            #Check if the message match some regexp in the filters file
            #Fixme: Made a method of this: check_filter(self, header), returns None or the pattern.
            for comp in lfilterscomp:
                    #comp = re_compile(patron.strip(), re.M)
                    result = comp.search(header)

                    if result is not None:
                        patron = lfilters[lfilterscomp.index(comp)]
                        aprint(_("Deleting message %d: Header match %s") % (msg['orignumber'], patron), general.RED)

                        if not optnotlog:
                            logAgent.append_filtered(indice_log, "%s (Prefiltered)"%patron,msg['size'])

                        self.server_bytes_left = self.server_bytes_left - msg['size']
                        self.delmesg(msg)
                        return ('delete', None, fromwho)

            if laterReply:
                aprint(_("Message %d (from %s) not in accept file: postergating it"\
                                    %(msg['orignumber'], fromwho)), general.VIOLET)
                if not optnotlog: 
                    logAgent.append_postergated(indice_log,emailaddr,msg['size'])

                if self.config.onlyonereply:
                    if fromwho not in AnimailMain.Application.repliedList:
                        # We never got a message from this address; add to
                        # the list and send a reply (just after the 'else')
                        AnimailMain.Application.repLock.acquire()
                        AnimailMain.Application.repliedList.append(emailaddr)
                        AnimailMain.Application.release_repLock()
                    else: # We know this guy, don't send more replies to him
                        return ('postergate',header,fromwho)
                try:
                    smtp.generatereply(fromwho)
                except smtplib.SMTPException, x:
                    aprint(_("SMTP Error delivering reply to %s, reply not sent: %s") % (fromwho,x), general.RED)
                return ('postergate',header,fromwho)
            if notAccepted:
                aprint(_("Message %d (from %s) not in accept file: ignoring it"\
                            %(msg['orignumber'], fromwho)),general.VIOLET)
                return ("delete",header,fromwho)
            return (0, header, fromwho)
#-------------------------------------------------------------
        def recoverDelayed(self, addr, smtp):
            try:
                    filename = self.config.homedir + '/.animail/animailDelayed/' + addr
                    fp = open(filename,'r+')
                    mbox = mailbox.UnixMailbox(fp)
                    mail = mbox.next()
                    mailcount = 0
                    while mail != None:
                                header = ''.join(mail.headers)
                                body = ''
                                line = 'Ugh, This is a BUG in ANIMAIL'
                                while (line[:5] != 'From ' ) and (line != ''):
                                    line = fp.readline()
                                    body += line

                                (foo,FROM) = rfc822.parseaddr(mail['from'])
                                if self.__class__.__name__ == "Pop3Server":
                                    body = header + body

                                self.deliver_smtp(header,body,FROM,smtp)
                                mailcount += 1
                                mail = mbox.next()
                    aprint(_("%d mails recovered from %s") % (mailcount, addr), general.VIOLET)
                    fp.close()
            except:
                    print _("Error trying to delete the delayed mbox of the address %s") % addr
                    print _("The mailbox won't be deleted, if you want to read those messages")
                    print _("open it manually (.animail/animailDelayed/%s)") % addr
                    print _("The error was: ")
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                    return
            os.unlink(filename)

#-------------------------------------------------------------
        def only_filter(self, logAgent, indice_log, smtp):
            nmesg = len(self.lmsg)
            i = 0
            for msg in self.lmsg[:]:
                    i += 1
                    self.look_message(msg, logAgent, indice_log,
                                                    nmesg - i, smtp)
#--------------------------------------------------------------
        def getuidl(self, number): pass
#--------------------------------------------------------------
        def create_msgstr(self,header,body):
            strmsg = ''
            if self.__class__.__name__ != "Pop3Server":
                strmsg += header
            strmsg += body
            return strmsg
#--------------------------------------------------------------
        def get_messages(self, logAgent, indice_log, is_retry, smtp):
            nmesg = len(self.lmsg)
            general.cursor_off()
            header = ''
            fromwho = ''

            if self.delivery == 'mta':
                    deliver = self.deliver_smtp
            elif self.delivery == 'mbox':
                    deliver = self.deliver_mbox
            elif self.delivery == 'maildir':
                    deliver = self.deliver_maildir
            elif self.delivery == 'pipe':
                    deliver = self.deliver_pipe
            elif self.delivery == 'global':
                    if self.config.optsmtp:
                                deliver = self.deliver_smtp
                    elif self.config.optmbox:
                                deliver = self.deliver_mbox
                    elif self.config.optmaildir:
                                deliver = self.deliver_maildir
                    elif self.config.optsendmail:
                                deliver = self.deliver_pipe

            num_trans = 0
            retcode = 'pass'
            for msg in self.lmsg[:]:
                    must_deliver = True
                    num_trans += 1
                    (size, unit) = general.compute(msg['size'])

                    if not self.config.optsyslog:
                                aprint('-'* 21, general.GREEN)
                    if self.config.optexpresion:
                                (retcode, header, fromwho) = self.look_message(msg,logAgent,indice_log,nmesg - num_trans,smtp)
                                if retcode == 'delete': #Deleted
                                    if self.config.optsmtp:
                                            smtp.smtpobj.noop()
                                    continue
                    # end if self.config.optexpresion

                    aprint(_("Downloading message %d (%.2f %s), Left: %d (%s)") % (msg['orignumber'], size, unit, nmesg - num_trans, self.alias),general.VIOLET)
                    
                    (msgbody, fromm, tmpheader) = self.get_message(msg, smtp, header, nmesg)
                    if fromm != '' and fromwho == '':
                                fromwho = fromm

                    if tmpheader != '':
                                header = tmpheader

                    if not self.config.optsyslog and not self.config.optquiet:
                                sys.stderr.write(general.colorize(_("\rDownloaded: "),general.YELLOW))
                                sys.stderr.write(general.colorize("100%\n",general.WHITE))


                    # If self.config.optexpression we've already looked for the IMAP
                    # DONTDELETETHISMESSAGE messages in the look_header method
                    if not self.config.optexpresion:
                        if msg['orignumber'] == 1:
                            resultWUIMAP = re_wuimap.search(msgbody)
                            resultWUIMAP2 = re_wuimap.search(header)
                            if (resultWUIMAP is not None) or (resultWUIMAP2 is not None):
                                aprint(_("Ignoring message %d: DONTDELETETHISMESSAGE type message") % (msg['orignumber']), general.RED)
                                retcode = 'wuimap'

                    if retcode == 'wuimap': must_deliver = False

                    try:
                                if retcode == 'postergate': #Message delayed
                                    animailBoxPath = self.config.homedir + '/.animail/animailDelayed'
                                    if not os.path.exists(animailBoxPath):
                                            os.mkdir(animailBoxPath, 0700)
                                    (foo,emailaddress) = rfc822.parseaddr(fromwho)
                                    tmpbox = open(animailBoxPath + '/' + emailaddress, 'a+')
                                    self.write_mbox(tmpbox, header, msgbody, fromm)
                                else:
                                    if retcode != 'wuimap': must_deliver = True
                                    if (self.config.lpostfilters != []) and (retcode != 'wuimap'):
                                        #FIXME SESSION: En realidad sólo sería necesario pasarle al
                                        #postfiltro el msgstr; después este, en su método
                                        #filter_mail ya se encargaría de crear el archivo temporal,
                                        #y sólo de ser necesario (si el filtro tiene opciones y
                                        #si estas opciones contienen un %M).

                                        #el create_msgstr también podría ir en el postfiltro pero
                                        #depende de la subclase de mailserver (pop3 o imap4). Eso
                                        #habría que arreglarlo definitivamente para que en la clase
                                        #base no se depende del tipo, quizás añadiendo un método a
                                        #las clases derivadas header_and_body o algo así.
                                        
                                        msgstr = self.create_msgstr(header,msgbody)
                                        tmpfile = open(tempfile.mktemp(), 'w+')
                                        os.chmod(tmpfile.name, 0600)
                                        tmpfile.write(msgstr)

                                        # Number of filters that have matched this message:
                                        npositives = 0
                                        # Have we copied this email to the spambox yet?
                                        alreadycopied = 0
                                        for pfilter in self.config.lpostfilters:
                                            output = ''
                                            aprint(_("Executing postfilter %s on message...") % pfilter.filtername, general.YELLOW)
                                            (pretcode, output) = pfilter.filter_mail(msgstr,tmpfile.name)
                                            if pretcode == 1:
                                                # Matched!
                                                npositives += 1

                                                if self.config.allpostfilters and ( npositives != len( self.config.lpostfilters) ):
                                                        # allpostfilters needs all the postfilters to match a 
                                                        # message for having it filtered:
                                                        continue

                                                must_deliver = False
                                                if not self.config.optnotlog: logAgent.append_filtered(indice_log,_("%s (Postfiltered by'%s')")%(fromm,pfilter.filtername),msg['size'])
                                                if pfilter.savepostfilteredmails != 0 and not alreadycopied:
                                                    pfilter.log_filtered_mail(msgstr,fromm, output)
                                                    alreadycopied = 1
                                                if npositives >= self.config.minpostfilters:
                                                    break
                                        tmpfile.close()
                                        os.unlink(tmpfile.name)
                                    if must_deliver:
                                        deliver(header, msgbody, fromm, smtp)

                                if self.optdelete and retcode != 'wuimap':
                                    aprint(_("Deleting message"), general.YELLOW)
                                    self.delmesg(msg)
                    except SMTPException, x:
                                print
                                print _("The local SMTP rejected this message so it won't be deleted from the mail server:"), str(x)
                                smtp.quit()
                                smtp.connect()
                                if not self.config.optnotlog:
                                    logAgent.incident(indice_log, str(x))
                    except socket.error, x:
                                print
                                print _("Socket error sending to the local SMTP, it won't be deleted from the mail server:"), str(x)
                                try:
                                    smtp.quit()
                                    smtp.connect()
                                except AttributeError: pass
                                if not self.config.optnotlog:
                                    logAgent.incident(indice_log, str(x))
                                continue
                    except mboxException, x:
                                print
                                print _("CRITICAL ERROR. There was an error delivering to MBox, aborting, message won't be deleted from the mail server: "), str(x)
                                sys.exit(1)
                    except maildirException, x:
                                print
                                print _("CRITICAL ERROR. There was an error delivering to Maildir, aborting, message won't be deleted from the mail server: "), str(x)
                                sys.exit(1)
                    except socket.sslerror, x:
                                print
                                print _("Socket error on SSL connection:"), str(x)


                    if not self.config.optnotlog and must_deliver:
                        (foo,emailaddr) = rfc822.parseaddr(fromm)
                        logAgent.append_downloaded(indice_log, emailaddr, msg['size'])

            if not self.config.optsyslog:
                    aprint('-'* 21, general.GREEN)
            general.cursor_on()
#********************************************************************************

