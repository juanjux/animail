# -*- coding: UTF-8 -*-
__copyright__ = """\
Copyright (c) 1999,2002            Juan José Álvarez Martínez


This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 dated June, 1991.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import socket, smtplib, poplib, sys, thread, threading, cPickle, os, time, tempfile
#from animail import configlib, general, logger, smtp
import configlib, general, logger, smtp

aprint = general.aprint

from pop3 import ConfigError
from imaplib import IMAP4
from gettext import gettext
_ = gettext

class OnlyCheckException(Exception):
        def __init__(self, server, user, nummsgs, optfetchmail):
            if optfetchmail:
                if nummsgs == 0:
                    print _("animail: No mail for %s in %s") % (user, server)
                elif nummsgs == 1:
                    print _("1 message for %s in %s") % (user, server)
                else:
                    print _("%d messages for %s in %s" % (nummsgs, user, server))
            else:
                print server+':'+str(nummsgs)
#-----------------------------------------------------------------------------

class AnimailMain(object):
        def __init__(self):
            self.logAgent           = None
            self.config             = None

            self.idquit                     = 0
            # Messages download lock; it'll be removed in the future
            self.CLock                      = None
            # replied addresses list lock
            self.repLock            = None
            self.repliedList        = []

        def run(self, argv):
            # The real thing starts here
            # FIXME: Maybe this should be done on __init__?
            self.config = configlib.ConfigAgent()
            self.config.parseCmdLine(sys.argv[1:]) # We need some config data before..
            self.config.parseConfigFile()
            # But we also need to give priority to parseCmdLine so it's parsed again...
            self.config.parseCmdLine(sys.argv[1:])
            self.config.setTermWidth()
            self.logAgent = logger.LogAgent()
            self.loadReplyList()

            self.checkLock()
            self.createLock()


            # Prevent the list growing too much
            if len(self.repliedList) > 500:
                for i in xrange(len(self.repliedList) - 500):
                    del self.repliedList[0]

            # Set the timeout
            # FIXME: Duplicated in configlib.py!!!
            if self.config.alarmtime != 0:
                # 60 by default
                socket.setdefaulttimeout(self.config.alarmtime)

            self.CLock = thread.allocate_lock()
            self.repLock = thread.allocate_lock()
            # Main thread will create per-server threads
            self.mainThread = threading.Thread(target=self.main)
            self.mainThread.start()
            return 0

        def main(self, *args):
            # Create one thread for each server
            threadList = []
            for serv in self.config.lservers:
                serverThread = threading.Thread(target=self.process, args=(serv,))
                serverThread.start()
                threadList.append(serverThread)

            # Wait for the threads to finish
            for t in threadList:
                t.join()

            # Reconnect and clean, if configured and needed
            if self.config.reconnect:
                cleanThreadList = []
                for serv in self.config.lservers:
                    if serv.optdelete and (not serv.clean_session) and serv.needs_cleanup():
                        serverCleanThread = threading.Thread(target=self.server_clean,args=(serv,))
                        serverCleanThread.start()
                        cleanThreadList.append(serverThread)
                
                if serv.needs_cleanup():
                    for t in cleanThreadList:
                        t.join()

            if not self.config.optnotlog:
                self.logAgent.show()

            try:
                repFile = open(self.config.configDir + 'repliedList.dat', 'w')
                cPickle.dump(self.repliedList, repFile)
            except IOError, x:
                aprint ("Warning: Error saving the replied list (%s)" % str(x), general.RED, iserror=True)

            self.deleteLock()

        def process (self, serv):
            """Code actually executed by every thread except the main thread"""
            config = self.config # Very used

            if config.optnotlog:
                log_index= 0
                logAgent = None
            else:
                # logAgent collects stadistics and show them at the end (see logger.py)
                # It has an entry for each server, which get indexed by log_index
                logAgent = self.logAgent
                log_index = logAgent.new(serv.alias, thread.get_ident())

            # If configured, send logging info to the system log
            # aprint() (see general.py) takes care of this automatically
            if  config.optsyslog:
                import syslog
                syslog.openlog("Animail", 0, syslog.LOG_MAIL)
            try:
                messages = False
                aprint(_("Trying to connect (%s)") % serv.alias, general.YELLOW)
                serv.connect()
                aprint(_("Authentificating (%s)") % serv.alias, general.YELLOW)
                serv.auth()

                aprint(_("Retrieving stats (%s)") % serv.alias, general.YELLOW)
                serv.stats()

                if not config.optnotlog:
                    #That's the way we inicialize the logAgent entry for this server
                    logAgent.giveme_size_num(serv.nummesg, serv.server_bytes_left, log_index)

                if serv.nummesg > 0:
                    aprint(_("You have %d new messages (%s)") % (serv.nummesg, serv.alias), general.YELLOW)
                    messages = True
                    if not config.optcheck:
                        aprint(_("Creating messages list (%s)") % serv.alias, general.YELLOW)
                        serv.make_list()
                else: aprint(_("No new messages (%s)") % serv.alias, general.CYAN)

                if config.optcheck:
                    #Nothing to do except show the stats (-C)
                    raise OnlyCheckException, (serv.adress, serv.name, serv.nummesg, config.optfetchmail)

                smtpobj = None
                get_messages = True
                if config.optsmtp or serv.delivery == 'mta':
                    smtpobj = smtp.SmtpServer()
                    smtpok = smtpobj.connect()
                    if smtpok != 'ok':
                        self.error_msg(smtpok, '', log_index)
                        get_messages = False

                if config.optonlyfilter and messages:
                    self.CLock.acquire()
                    serv.only_filter(logAgent, log_index, smtpobj)
                    messages = False
                    self.release_lock()

                #-DOWNLOAD AND DELETE MESSAGES FROM SERVER-----------------
                if messages and get_messages:
                    self.CLock.acquire()
                    # This is actually what do the transfer of messages
                    # We need the lock to don't mess the mbox files and
                    # the output
                    serv.get_messages(self.logAgent, log_index, 0, smtpobj)
                    self.release_lock()

                    # Close the connection with the smtp server
                    if config.optsmtp or serv.delivery=='mta': smtpobj.quit()

                    # Messages are removed from lmsg in the server objects
                    # when they are donwloaded, so this should be empty...
                    if serv.lmsg == []:
                        aprint(_("No more messages"), general.CYAN)

                # Exit this server
                serv.serv_exit()
                if config.optv: print _("Exiting...")

                # Bye!
                self.__exit_thread()

#-EXCEPTION HANDLERS
            except smtplib.SMTPException, x:
                self.error_msg("SMTP Error (%s): " % serv.adress, x, log_index)

            except socket.error, x:
                self.error_msg(_("Connection error (%s): ") % serv.name, x, log_index)

            except socket.sslerror, x:
                self.error_msg(_("SSL connection error (%s): ") % serv.name, x, log_index)
                
            except socket.gaierror, x:
                self.error_msg(_("Temporary name resolution error (%s): ") % serv.name, x, log_index)
                
            except socket.herror, x:
                self.error_msg(_("Name resolution error (%s): ") % serv.name, x, log_index)

            except poplib.error_proto, x:
                self.error_msg(_("Protocol Error (%s): ") % serv.adress, x, log_index)

            #except KeyboardInterrupt: # Disabled in development versions
                #general.cursor_on()
                #msg = _("Keyboard interrupt (%s)") % serv.name
                #mensaje(msg, optsyslog)
                #if config.optnotlog: logAgent.incident(log_index, msg)
                #self.__exit_thread()

            except socket.timeout, x:
                self.error_msg(_("Timeout expired (%s): ") % serv.adress, "", log_index)

            except ConfigError, x:
                self.error_msg(_("Configuration error (%s): ") % serv.adress, x, log_index)

            except IMAP4.error, x:
                self.error_msg(_("IMAP error (%s): ") % serv.adress, x, log_index)

            except OnlyCheckException, x:
                pass

            except SystemExit:
                self.error_msg(_("Thread exited"),"",log_index)

            except:
                aprint (_("Unhandled exception (%s)! This is probably a bug, please") % serv.adress,general.RED)
                aprint (_("send an email to <juanjux@yahoo.es> with the following message:"),general.RED)
                import traceback, cStringIO
                tb = cStringIO.StringIO()
                aprint ('-'*20,general.RED)
                traceback.print_exc(file=tb)
                aprint (tb.getvalue(),general.RED)
                aprint ('-'*20,general.RED)
                # end try
        # end for
            if config.optcheck:
                sys.exit(messages)
            if not serv.clean_session:
                serv.error_time = time.time()
            self.__exit_thread()

        def server_clean(self,serv):
            try:
                aprint(_("Trying to clean downloaded messages from %s") % serv.alias, general.YELLOW)
                curtime = time.time()
                diftime = curtime - serv.error_time

                if diftime < self.config.reconnect_wait:
                    wait = self.config.reconnect_wait - diftime
                    aprint(_("Waiting %d seconds before connecting again to the server") % wait, general.YELLOW)
                    time.sleep(wait)

                aprint(_("(Re)Connecting to %s") % serv.alias,general.YELLOW)
                serv.connect()
                aprint(_("Authentificating (%s)") % serv.alias, general.YELLOW)
                serv.auth()

                aprint(_("Starting downloaded messages deletion (%s)") % serv.alias,general.YELLOW)
                serv.cleanup()
            except:
                aprint (_("Something bad happened again! Bye server bye..."),general.RED)
                import traceback, cStringIO
                tb = cStringIO.StringIO()
                aprint (_("The exception text was:"),general.RED)
                traceback.print_exc(file=tb)
                aprint (tb.getvalue(),general.RED)

        def __exit_thread(self):
            self.release_lock()

        def release_lock(self):
            if self.CLock.locked():
                self.CLock.release()

        def release_repLock(self):
            if self.repLock.locked():
                self.repLock.release()

        def error_msg(self, msg_str, excep, log_index):
            msg = ' '.join( (msg_str, str(excep)) )
            aprint(msg, general.RED)
            if not self.config.optnotlog: self.logAgent.incident(log_index, msg)
            general.cursor_on()

        def loadReplyList(self):
            if not os.path.exists(self.config.configDir + 'repliedList.dat'):
                return
            else:
                try:
                    repFile = open(self.config.configDir + 'repliedList.dat', 'r')
                except IOError, x:
                    aprint(_("Warning: Error opening the replied messages list file! (%s)") % str(x), general.RED)
                    return
                self.repliedList = cPickle.load(repFile)

        def checkLock(self):
            tempdir = tempfile.gettempdir()
    
            if tempdir=="":
                aprint(_("Warning: Could not get the system TMP directory for checking the lockfile, continuing anyway"), general.RED)
                return
    
            lockfilename = os.path.join(tempdir, "animail-lock-" + self.config.sysuser)
    
            if os.path.exists(lockfilename):
                aprint(_("Error: Another Animail session seems to be active. If not (check with ps aux|grep animail) delete the file  %s") % (lockfilename), general.RED)
                sys.exit(1)
    
        def createLock(self):
            tempdir = tempfile.gettempdir()
    
            if tempdir=="":
                aprint(_("Warning: Could not get the system TMP directory for checking the lockfile, continuing anyway"), general.RED)
                return
    
            lockfilename = os.path.join(tempdir, "animail-lock-" + self.config.sysuser)
    
            try:
                lockfile = open(lockfilename,'w')
                os.chmod(lockfilename, 0600)
                lockfile.close()
            except IOError, x:
                aprint(_("Warning: Could not create the lockfile: %s") % (str(x)), general.RED)
    
        def deleteLock(self):
            tempdir = tempfile.gettempdir()
    
            if tempdir=="":
                aprint(_("Warning: Could not get the system TMP directory for checking the lockfile, continuing anyway"), general.RED)
                return
    
            lockfilename = os.path.join(tempdir, "animail-lock-" + self.config.sysuser)
    
            try:
                os.unlink(lockfilename)
            except OSError, x:
                aprint(_("Error trying to delete the lockfile %s: %s continuing anyway") % (lockfilename, str(x)), general.RED)


#--------------------------------------------------

Application = AnimailMain() # This is used by other objects to access the application object
general.Application = Application # So the general module functions has access to this

