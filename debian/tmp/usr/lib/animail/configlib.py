# -*- coding: UTF-8 -*-
import getopt, os, pwd, shutil, sys,socket,poplib,re

try: import psyco
except ImportError: pass

#from animail import imaplib, postfiler, timeoutsocket, general
from pop3 import Pop3Server, ConfigError
from imap import Imap4Server
from imaplib import IMAP4
from postfilter import PostFilter
from timeoutsocket import Timeout
from gettext import gettext
import general
_ = gettext
aprint = general.aprint

__copyright__ = """\
Copyright (c) 1998,2002            Juan José Álvarez Martínez


This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 dated June, 1991.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""


class ConfigAgent:
#-------------------------------------
    def __init__(self):
        self.opthost =  0
        self.optsmtp =  1
        self.smtpserver = ''
        self.smtpport = 25
        self.alarmtime = 60
        self.more_time = 0
        self.optsize = 0
        self.max_size = 0
        self.optmax = 0
        self.max_number = 0
        self.optmbox = 0
        self.optmaildir = 0
        self.mboxfile = ''
        self.maildir = ''
        self.optorder = 'arrival'
        self.optexpresion = 0
        self.optaccept = 0
        self.optsyslog = 0
        self.optv = 0
        self.optquiet = 0
        self.optonlyfilter = 0
        self.optnotlog = 0
        self.mailer = ''
        self.mailer_args = ()
        self.optsendmail = 0
        self.sendmailcmd = '/usr/sbin/sendmail -bm'
        self.optcolors = 1
        self.optcheck = 0
        self.optfetchmail = 0
        self.notInAccept = 'none'
        self.replyaddress = ''
        self.replysubject = 'Auto-generated message'
        self.confirmsubject = "Ok, your messages have been delivered"
        self.filewithreply = ''
        self.filewithaccept = ''
        self.autoacceptconfirm = 1
        self.onlyonereply = 0
        self.verboselevel = 0
        self.onlyServersList = []
        self.reconnect = 1
        self.reconnect_wait = 30
        self.lacceptedcomp = []
        self.lfilterscomp = []
        self.postfilteredmailsmbox = ''
        self.lservers = []
        self.lfilters = []
        self.laccepted = []
        self.lpostfilters = []
        self.smtpspamcodes = []
        self.usingsmtpspamcodes = 0

        pwddata = pwd.getpwuid( os.getuid() )
        self.sysuser = pwddata[0]
        self.homedir = pwddata[5]
        self.configDir = self.homedir + '/.animail/'
        self.nconfigfileold = self.homedir + '/.animailrc'
        self.nconfigfile = self.configDir + 'animailrc'
        self.nconfigfile2 = self.homedir + '/.animailrc2'

        try:
            # Psyco increase the speed of those methods about 200%...
            psyco.bind(self.parseFilterFile)
            psyco.bind(self.parseAcceptFile)
        except NameError:
            pass

#-----------------------------------------
    def check_mbox(self):
        if not os.path.exists(self.mboxfile):
            print _("Critical Error: Can't deliver mail to unexistent mbox!! (%s)") % self.mboxfile
            sys.exit(1)
        if os.path.islink(self.mboxfile):
            print _("Critical Error: Destination mbox (%s) can't be a symlink") % self.mboxfile
            sys.exit(1)

#------------------------------------------
    def parseFilterFile(self):
        try:
            self.lfilters = open(self.nfilterfile, 'r').readlines()
        except IOError,x:
            print _("Error trying to open the filter file (%s):")\
                                                % self.nfilterfile, str(x)
            return []
        for regex in self.lfilters[:]:
            if regex[0] == '#':
                continue
            if regex in ['\n','\t']:
                self.lfilters.remove(regex)
                continue
            try:
                self.lfilterscomp.append( re.compile(regex.strip(), re.M) )
            except re.error:
                print _("Error compiling regular expression from the filters file\n")
                print _("the offending regex was: %s") % regex
                sys.exit(1)
#-------------------------------
    def parseAcceptFile(self):
        try:
            self.laccepted = open(self.nacceptfile, 'r').readlines()
        except IOError,x:
            print _("Error trying to open the accept file (%s):") % self.nacceptfile, str(x)
            return []
        for regex in self.laccepted[:]:
            if regex[0] == '#':
                continue
            if regex in ['\n','\t']:
                self.laccepted.remove(regex)
                continue
            try:
                self.lacceptedcomp.append( re.compile(regex.strip(), re.M) )
            except re.error:
                print _("Error compiling regular expression from the accepted file\n")
                print _("the offending regex was: %s") % regex
                sys.exit(1)
#------------------------------------------------------
    def writeFilterFile(self):
        if os.path.exists(self.nfilterfile) and os.path.getsize(self.nfilterfile) > 0:
            nbakfile = self.nfilterfile + '.bak'
            shutil.copyfile(self.nfilterfile, nbakfile)
        filterfile = open(self.nfilterfile, 'w')
        filterfile.close()
        os.chmod(self.nfilterfile, 0600)
        filterfile = open(self.nfilterfile, 'w')
        for i in self.lfilters:
            filterfile.write(i)
        filterfile.close()


#-----------------------------------------
    def parseCmdLine(self, argv):
        optlist, args = [], []
        short_opts = 'hBo:f:kvs:n:tFlCMO:V'
        long_opts = ['no-summary',
                        'only-filter',
                        'activate-cursor',
                        'help',
                        'download-order=',
                        'mbox-file=',
                        'verbose',
                        'max-size=',
                        'max-to-download=',
                        'syslog-output',
                        'quiet',
                        'check',
                        'fetchmail',
                        'only-from=',
                        'version']
        try:
            optslist, args = getopt.getopt(argv, short_opts, long_opts)
            for cmdline, value in optslist:
                if cmdline in ['-l', '--no-summary']:
                    self.optnotlog = 1
                elif cmdline in ['-F', '--only-filter']:
                    self.optonlyfilter = 1
                elif cmdline in ['-k', '--activate-cursor']:
                    general.cursor_on()
                    sys.exit(0)
                elif cmdline in ['-h', '--help']:
                    general.usage()
                    sys.exit(0)
                elif cmdline in ['-o', '--download-order']:
                    if not value or not \
                        value.lower() in ['arrival', 'bin', 'small']:
                        raise getopt.error, _("option --download-order \
supplied with invalid value.")
                    self.optorder = value
                elif cmdline in ['-f', '--mbox-file']:
                    self.mboxfile = value
                    self.check_mbox()
                    self.optmbox = 1
                elif cmdline in ['-v', '--verbose']:
                    self.optv = 1
                elif cmdline in ['-s', '--max-size']:
                    try:
                                    if not value:
                                            raise ValueError
                                    self.max_size = int(value)
                                    self.optsize = 1
                    except ValueError:
                                    raise getopt.error, _("option --max-to-download \
suplied with invalid value.")
                elif cmdline in ['-n', '--max-to-download']:
                    self.optmax = 1
                    self.max_number = int(value[1])
                elif cmdline in ['-B', '--syslog-output']:
                    self.optsyslog = 1
                    self.optv = 0
                    self.optnotlog = 1
                    self.optcolors = 0
                elif cmdline in ['-t', '--quiet']:
                    self.optquiet = 1
                elif cmdline  == '--display': pass
                elif cmdline in ['-C', '--check']:
                    self.optcheck = 1
                    self.optnotlog = 1
                elif cmdline in ['-M', '--fetchmail']:
                    self.optfetchmail = 1
                    self.optcheck = 1
                    self.optnotlog = 1
                elif cmdline in ['-O', '--only-from']:
                    self.onlyServersList = value.split(',')
                elif cmdline in ['-V', '--version']:
                    print general.VERSION
                    sys.exit(0)
                else: general.usage()
                # end for
        except getopt.error, x:
            print _("%s:error: %s") % (sys.argv[0], str(x))
            general.usage()
            sys.exit(1)
        except SystemExit, x:
            sys.exit(x)

        if not hasattr(self, 'optmbox'):
            self.mboxfile = ''.join( (self.homedir, '/mbox'))
        if not hasattr(self, 'optmaildir'):
            self.maildir = ''.join( (self.homedir, '/Maildir/'))
    # end def parseCmdLine
#-----------------------------------------------------------------------
    def server_setdefaults(self):
        self.adressaux = ''
        self.aux_username = ''
        self.aux_passwd = ''
        self.aux_alias = ''
        self.aux_port = 110
        self.aux_protocol = 'POP3'
        self.aux_changedport = 0
        self.aux_optdelete = 1
        self.aux_ssl = 0
        self.aux_delivery = 'global'
        self.aux_mbox = ''
        self.aux_maildir = ''
        self.aux_sendmailcmd = ''
        self.aux_resend = 0
        self.aux_towho_list = []

    def postfilter_setdefaults(self):
        self.aux_postfilter_filtername = ''
        self.aux_postfilter_binarypath = ''
        self.aux_postfilter_inputstdin = 1
        self.aux_postfilter_options = ''
        self.aux_postfilter_killreturnvalues = []
        self.aux_postfilter_killprogramoutput = None #Is a compiled regex
        self.aux_postfilter_showfilteroutput = 0
        self.aux_postfilter_savepostfilteredmails = 0

    def set_defaults(self):
        self.server_setdefaults()
        self.postfilter_setdefaults()
        self.insideserver = 0
        self.insideglobal = 0
        self.insidepostfilter = 0

    def config_server(self,serv):
        serv.ssl = self.aux_ssl
        if self.aux_alias == '': serv.alias = self.adressaux
        else: serv.alias = self.aux_alias
        serv.optdelete = self.aux_optdelete
        serv.towho = self.aux_towho_list
        serv.optresend = self.aux_resend
        serv.protocol = self.aux_protocol
        serv.delivery = self.aux_delivery
        if self.aux_delivery != 'global':
            serv.mbox = self.aux_mbox
            serv.maildir = self.aux_maildir
            serv.sendmailcmd = self.aux_sendmailcmd

#------------------------------------------------------------------------
    def parseConfigFile(self):

        if not os.path.exists(self.homedir + '/.animail'):
            os.mkdir(self.homedir + '/.animail')
        else:
            if not os.path.isdir(self.homedir + '/.animail'):
	    	print _("Error: %s/.animail is not a directory!") % (self.homedir)
                sys.exit(1)

        if not os.path.exists(self.nconfigfile):
            if not os.path.exists(self.nconfigfile2):
                if not os.path.exists(self.nconfigfileold):
                    print _("Config file %sanimailrc not found!") % self.configDir
                    sys.exit(1)
                else:
                    self.nconfigfile = self.nconfigfileold
                    print _("Warning: animailrc file should be on %sanimailrc (current location is in %s)") % (self.configDir, self.homedir)
            else:
                self.nconfigfile = self.nconfigfile2
                print _("Warning: animailrc file should be on %sanimailrc (current location is %s)") % (self.configDir, self.homedir)

        try:
            fsize = os.stat(self.nconfigfile)[6] #File size
            fmode = os.stat(self.nconfigfile)[0] #File perms
        except OSError, x:
            print _("Error trying to open the config file %s: %s") % (self.nconfigfile, str(x))
            sys.exit(1)

        if fmode != 33152:
            print _("ERROR: For security reasons the animailrc config file must have 600 perms!")
            print _("(to change the permissions you can do: chmod 600 animailrc)")
            sys.exit(1)

        if fsize == 0 or (not os.path.exists(self.nconfigfile)):
            print _("WARNING: Config file don't exists or it's empty. Please configure Animail")

        try:
            lconfig = open(self.nconfigfile, 'r').readlines()
        except IOError:
            print _("I can't read the config file (%s)!") % self.nconfigfile
            sys.exit(1)

        self.set_defaults()

        linecount = 0

        #In Python 2.3 this can be done with an enumerate() of lconfig. This way we can remove
        #linecount and the need to increase it (and is more elegant and Pythonic)


        for line in lconfig:
            linecount+=1
            tmplist = line.split(':', 1)

            # Strip whitespace from beginning and end of line
            line = line.strip()

            # Ignore blank lines
            if len(line) == 0: continue

            if tmplist == ['\012'] or tmplist == ['#']: continue
            if tmplist[0][0] == '#': continue
            spaced_value = ''

            try:
                [command, spaced_value] = tmplist
            except ValueError: # <command>
                command = tmplist[0].strip()
            command = command.lower()

            try:
                if command[0] != '<' and spaced_value.isspace():
                    print _("Error (line %d), the parameter of '%s' is empty") % (linecount,command)
                    sys.exit(1)
            except IndexError: continue

            value = spaced_value.strip()
            lowval = value.lower()
#--------------------BY SERVER OPTIONS----------------------------------------------
            if self.insideserver:
            #Mmmmm, this won't scale to many block types... I'll change it...
                if command == '<server>' or command == '<servidor>':
                    print _("Config file error (line %d): <server> inside another <server>") % linecount
                    sys.exit(1)

                elif command == '<global>':
                    print _("Config file error (line %d): <global> inside <server>") % linecount
                    sys.exit(1)

                elif command == '</global>':
                    print _("Config file error (line %d): </global> inside <server>") % linecount
                    sys.exit(1)

                elif command == '<postfilter>' or command == '<postfiltro>':
                    print _("Config file error (line %d): <postfilter> inside <server>") % linecount
                    sys.exit(1)

                elif command == '</postfilter>' or command == '</postfiltro>':
                    print _("Config file error (line %d): </postfilter> inside <server>") % linecount
                    sys.exit(1)

                elif command == 'address' or command == 'direccion' or command == 'dirección':
                    self.opthost = 1
                    self.adressaux = value

                elif command == 'port' or command == 'puerto':
                    self.aux_port = int(value)
                    self.aux_changedport = 1

                elif command == 'username' or command == 'nombreusuario':
                    self.aux_username = value

                elif command == 'protocol' or command == 'protocolo':
                    if lowval == 'pop3': self.aux_protocol='POP3'
                    elif lowval == 'apop': self.aux_protocol='APOP'
                    elif lowval == 'imap4': self.aux_protocol='IMAP4'
                    else:
                                    print 'Config file error (line %d): Protocol %s not supported, POP3     will be used' % (linecount,value)

                elif command == 'ssl':
                    if lowval == 'yes' or lowval == 'si':
                        self.aux_ssl = 1
                    else:
                        self.aux_ssl = 0

                elif command=='pass' or command=='passwd' or command=='password' or command=='clave' or command == 'contraseña':
                    self.aux_passwd = value

                elif command == 'keeponserver' or command == 'mantenerenservidor':
                    if lowval == 'yes' or lowval == 'si':
                        self.aux_optdelete = 0
                    else:
                        self.aux_optdelete = 1

                elif command == 'resendto' or command == 'reenviara':
                    self.aux_resend = 1
                    self.aux_towho_list = value.split(',')

                elif command == 'alias':
                    self.aux_alias = spaced_value
                    self.aux_alias = self.aux_alias.strip()

                elif command == 'mboxfile' or command == 'archivobuzon' or command == 'deliver_mbox' or command == 'entrega_mbox':
                    self.aux_delivery = 'mbox'
                    self.aux_mbox = value

                elif command == 'maildir' or command == 'deliver_maildir' or command == 'entrega_maildir':
                    self.aux_delivery = 'maildir'
                    if value[:-1] != '/': self.maildir = value + '/'
                    self.aux_maildir = value

                elif command == 'uselocalmta' or command == 'usarmtalocal' or command == 'deliver_localmta' or command == 'entrega_mtalocal':
                    if lowval == 'yes' or lowval == 'si':
                        self.aux_delivery = 'mta'

                elif command == 'usesendmail' or command == 'usarsendmail':
                    if lowval == 'yes' or lowval == 'si':
                        self.aux_delivery = 'pipe'
                elif command == 'sendmailcommand' or command == 'comandosendmail':
                    self.aux_delivery = 'pipe'
                    self.aux_sendmailcmd = spaced_value

                elif command == 'deliver_pipe' or command == 'entrega_pipe' or command == 'entrega_tuberia':
                    self.aux_delivery = 'pipe'
                    self.aux_sendmailcmd = spaced_value

                elif command == '</server>' or command == '</servidor>':
                    if (self.onlyServersList != []) and (self.aux_alias != ''):
                                    if self.aux_alias not in self.onlyServersList:
                                            self.set_defaults()
                                            continue

                    if self.aux_protocol == 'POP3':

                        if self.aux_changedport:
                                serverport = self.aux_port
                                self.aux_changedport = 0
                        else:
                                if self.aux_ssl: serverport = 995
                                else: serverport = 110

                        serv = Pop3Server(self.adressaux, self.aux_username, self.aux_passwd,serverport)
                        self.config_server(serv)

                    elif self.aux_protocol == 'IMAP4':
                        if self.aux_changedport:
                                serverport = self.aux_port
                                self.aux_changedport = 0
                        else:
                                if self.aux_ssl: serverport = 993
                                else: serverport = 143

                        serv = Imap4Server(self.adressaux,self.aux_username,self.aux_passwd,serverport)
                        self.config_server(serv)

                    self.lservers.append(serv)
                    self.set_defaults()

                elif command != '' and command !='\n':
                    print _("Error in config file [server section, line %d] (%s)") % (linecount,
                    self.nconfigfile)
                    print _("I don't understand: ")+command+":"+spaced_value
                    print _("(Maybe a <global> or <postfilter> command in a <server> section?)");
                    sys.exit(1)
#-----------------GLOBAL OPTIONS---------------------------------------------------
            elif self.insideglobal:
                if command == '<global>':
                    print _("Config file error (line %d): <global> inside another <global>") % linecount
                    sys.exit(1)

                elif command == '<server>' or command == '<servidor>':
                    print _("Config file error (line %d): <server> inside <global>") % linecount
                    sys.exit(1)

                elif command == '</server>' or command == '</servidor>':
                    print _("Config file error (line %d): </server> inside <global>") % linecount
                    sys.exit(1)

                elif command == '<postfilter>' or command == '<postfiltro>':
                    print _("Config file error (line %d): <postfilter> inside <global>") % linecount
                    sys.exit(1)

                elif command == '</postfilter>' or command == '</postfilter>':
                    print _("Config file error (line %d): </postfilter> inside <global>") % linecount
                    sys.exit(1)

                elif command == 'smtpserver' or command == 'servidorsmtp':
                    self.smtpserver = value

                elif command == 'timeout':
                    self.alarmtime = int(value)
                    if self.alarmtime != 0:
                        import timeoutsocket
                        timeoutsocket.setDefaultSocketTimeout(self.alarmtime)

                elif command == 'reconnect' or command == 'reconectar':
                    if lowval == 'yes' or lowval == 'si':
                        self.reconnect = 1
                    else:
                        self.reconnect = 0

                elif command == 'waitbeforereconnection' or command == 'esperaantesreconectar':
                    self.reconnect_wait = int(value)

                elif command == 'moretime' or command == 'mastiempo':
                    self.more_time = int(value)

                elif command == 'smtpport' or command == 'puertosmtp':
                    self.smtpport = int(value)

                elif command == 'maxsize' or command == 'tamañomaximo':
                    self.optsize = 1
                    self.max_size = int(value)

                elif command == 'maxnumber' or command == 'numeromaximo':
                    self.optmax = 1
                    self.max_number = int(value)

                elif command == 'mboxfile' or command == 'archivobuzon' or command == 'deliver_mbox' or command == 'entrega_mbox':
                    self.optmbox = 1
                    self.mboxfile = value
                    self.check_mbox()
                    self.optsmtp = 0
                    self.optsendmail = 0
                    self.maildir = 0

                elif command == 'maildir' or command == 'deliver_maildir' or command == 'entrega_maildir':
                    self.optmaildir = 1
                    if value[:-1] != '/': self.maildir = value + '/'
                    else: self.maildir = value
                    self.optsmtp = 0
                    self.optsendmail = 0
                    self.optmbox = 0

                elif command == 'colorize' or command == 'colorear':
                    if lowval == 'yes' or lowval == 'si':
                        self.optcolors = 1
                    else:
                        self.optcolors = 0

                elif command == 'downloadorder' or command == 'ordendetransferencia':
                    if   lowval == 'arrival' or lowval == 'llegada':
                        self.optorder = 'arrival'
                    elif lowval == 'firstbig' or lowval == 'primerograndes':
                        self.optorder = 'big'
                    elif lowval == 'firstsmall' or lowval == 'primeropequeños':
                        self.optorder = 'small'
                    else:
                                    print _("Error in download order config (%s), line %d") % (value,linecount)
                                    sys.exit(1)

                elif command == 'uselocalmta' or command == 'usarmtalocal' or command == 'deliver_localmta' or command == 'entrega_mtalocal':
                    if lowval == 'yes' or lowval == 'si':
                        self.optsmtp = 1
                        self.optsnedmail = 0
                        self.optmbox = 0
                        self.maildir = 0

                elif command == 'usesendmail' or command == 'usarsendmail':
                    if lowval == 'yes' or lowval == 'si':
                        self.optsendmail = 1
                        self.optsmtp = 0
                        self.optmbox = 0
                        self.optmaildir = 0
                        self.optmaildir = 0

                elif command == 'sendmailcommand' or command == 'comandosendmail':
                    self.sendmailcmd = spaced_value

                elif command == 'deliver_pipe' or command == 'entrega_pipe':
                    self.optsendmail = 1
                    self.optsmtp = 0
                    self.optmbox = 0
                    self.optmaildir = 0
                    self.sendmailcmd = spaced_value

                elif command == 'filterfile' or command == 'ficherofiltros':
                    if lowval != '':
                        self.optexpresion = 1
                        self.nfilterfile = value
                        self.parseFilterFile()
                    else: self.optexpresion = 0

                elif command == 'acceptfile' or command == 'ficheroaceptar' or command == 'ficheroaceptados':
                    if lowval != '':
                        self.optexpresion = 1
                        self.optaccept = 1
                        self.nacceptfile = value
                        self.parseAcceptFile()
                    else: self.optaccept = 1

                elif command == 'mailer' or command == 'lector':
                    tokens = value.split()
                    self.mailer = tokens[0]
                    self.mailer_args = tuple(tokens[1:])

                elif command == 'notinacceptfile' or command == 'noenficheroaceptar' or command == 'noenficheroaceptados':
                    if lowval == 'none' or lowval == 'nada':
                        self.notInAccept = 'filterfile'
                    elif lowval == 'reply' or lowval == 'responder':
                        self.notInAccept = 'reply'
                    elif lowval == 'delete' or lowval == 'borrar':
                        self.notInAccept = 'delete'
                    elif lowval == 'ignore' or lowval == 'ignorar':
                        self.notInAccept = 'ignore'

                    else:
                                    print _("Error in 'NotInAcceptFile' config (%s), line %d") % (value,linecount)
                                    sys.exit(1)

                elif command == 'replyaddress' or command == 'direccionrespuesta':
                    self.replyaddress = spaced_value

                elif command == 'replysubject' or command == 'asuntorespuesta':
                    self.replysubject = spaced_value

                elif command == 'confirmsubject' or command == 'asuntoconfirmacion':
                    self.confirmsubject = spaced_value

                elif command == 'filewithreply' or command == 'archivoconrespuesta':
                    self.filewithreply = spaced_value

                elif command == 'filewithconfirm' or command == 'archivoconconfirmacion':
                    self.filewithaccept = spaced_value

                elif command == 'autoacceptconfirmations' or command == 'autoaceptarconfirmaciones':
                    if lowval == 'no': self.autoacceptconfirm = 0

                elif command == 'onlyonereply' or command == 'solounarespuesta':
                    if lowval == 'yes' or lowval == 'si' or lowval == 'sí':
                        self.onlyonereply = 1

                elif command == 'postfilteredmailsmbox' or command == 'mboxmensajespostfiltrados':
                    self.postfilteredmailsmbox = spaced_value.strip()
                    try:
                        open(self.postfilteredmailsmbox,'a+').close()
                    except IOError:
                        print _("Couldn't open or create the postfiltered messages log mbox file (%s)!!!") % self.postfilteredmailsmbox
                        print _("Please check the permissions of the file and his directory")
                        sys.exit(1)
                elif command == 'smtpspamcodes' or command == 'codigosspamsmtp' or command == 'códigosspamsmtp':
                    self.smtpspamcodes = value.split(',')
                    for code in self.smtpspamcodes:
                        if ( not code.isdigit() ) or ( len(code) != 3 ):
                            print _("Error in config file [global section, line %d] (%s)") % (linecount, self.nconfigfile)
                            print _("The value of SMTPSpamCodes must be a comma separated list of numeric")
                            print _("three digit codes; either some code includes a non-numeric character")
                            print _("or some code is not three-digits length (or both)")
                            sys.exit(1)
                    if self.smtpspamcodes != []: self.usingsmtpspamcodes = 1

                elif command == '</global>':
                    self.insideglobal = 0

                elif command != '' and command !='\n':
                    print _("Error in config file [global section, line %d] (%s)") % (linecount,self.nconfigfile)
                    print _("I don't understand: '"), command,":", spaced_value,"'"
                    print _("(Maybe a <server> or <postfilter> command in a <global> section?)")
                    sys.exit(1)
#---------------POSTFILTER--------------------------------------------------
            elif self.insidepostfilter:
                if command == '<postfilter>' or command == '<postfiltro>':
                    print _("Config file error (line %d): <postfilter> inside another <postfilter>") % linecount
                    sys.exit(1)
                elif command == '<server>' or command == '<servidor>':
                    print _("Config file error (line %d): <server> inside <postfilter>") % linecount
                    sys.exit(1)

                elif command == '</server>' or command == '</servidor>':
                    print _("Config file error (line %d): </server> inside <postfilter>") % linecount

                elif command == '<global>':
                    print _("Config file error (line %d): <global> inside <postfilter>") % linecount

                elif command == '</global>':
                    print _("Config file error (line %d): </global> inside <postfilter>") % linecount

                elif command == 'postfiltername' or command == 'nombrepostfiltro':
                    self.aux_postfilter_filtername = value

                elif command == 'path' or command == 'filtro':
                    self.aux_postfilter_binarypath = spaced_value

                elif command == 'inputmessagebystdin' or command == 'darmensajeporstdin':
                    if lowval == 'no':
                        self.aux_postfilter_inputstdin = 0

                elif command == 'options' or command == 'opciones':
                    self.aux_postfilter_options = spaced_value

                elif command == 'killerreturnvalues' or command == 'valoresderetornoasesinos':
                    self.aux_postfilter_killreturnvalues = value.split(',')
                    for i in self.aux_postfilter_killreturnvalues:
                        try:
                            int(i)
                        except ValueError:
                            print _("Error in configfile [postfilter section, line %d]:") % linecount
                            print _("the argument for KillerReturnValues must be a NUMBER or ")
                            print _("a comma separated list of NUMBERS")
                            sys.exit(1)

                elif command == 'killerprogramoutput' or command == 'salidadeprogramaasesina':
                    try:
                        self.aux_postfilter_killprogramoutput = re.compile(value.strip(), re.M)
                    except re.error:
                        print _("Error in configfile [postfilter section, line %d]:") % linecount
                        print _("invalid regular expression as argumento to KillerProgramOutput")
                        sys.exit(1)
                elif command == 'showfilteroutput' or command == 'mostrarsalidafiltro':
                    if lowval == 'yes' or lowval == 'si' or lowval == 'sí':
                        self.aux_postfilter_showfilteroutput = 1

                elif command == 'savepostfilteredmails' or command == 'guardarmensajespostfiltrados':
                    if lowval == 'yes' or lowval == 'si' or lowval == 'sí':
                        self.aux_postfilter_savepostfilteredmails = 1
                    elif lowval == 'no':
                        self.aux_postfilter_savepostfilteredmails = 0
                    elif lowval == 'output' or lowval == 'salida':
                        self.aux_postfilter_savepostfilteredmails = 2
                    elif lowval == 'stdout':
                        self.aux_postfilter_savepostfilteredmails = 3

                elif command == '</postfilter>' or command == '</postfiltro>':
                    def error_msg(linecount):
                        print _("Error in configfile [postfiler section, line %d]:") % linecount

                    if self.aux_postfilter_binarypath == '':
                        error_msg(linecount)
                        print _("No Path given to the post-filter")
                        sys.exit(1)
                    else: postfilter = PostFilter(self.aux_postfilter_binarypath)

                    if self.aux_postfilter_filtername == '':
                        error_msg(linecount)
                        print _("No PostFilterName given to this filter")
                        sys.exit(1)
                    else: postfilter.filtername = self.aux_postfilter_filtername

                    postfilter.inputstdin = self.aux_postfilter_inputstdin
                    postfilter.options = self.aux_postfilter_options
                    postfilter.killreturnvalues = self.aux_postfilter_killreturnvalues
                    postfilter.killprogramoutput = self.aux_postfilter_killprogramoutput
                    postfilter.savepostfilteredmails = self.aux_postfilter_savepostfilteredmails
                    if (postfilter.inputstdin == []) and (postfilter.killprogramoutput == None):
                        error_msg(linecount)
                        print _("Both KillerReturnValues and KillerProgramOutput non specified")
                        print _("You must specify at least one of them")
                        sys.exit(1)
                    postfilter.showfilteroutput = self.aux_postfilter_showfilteroutput
                    self.lpostfilters.append(postfilter)

                    self.insidepostfilter = 0

                elif command != '' and command != '\n':
                    print _("Error in config file [postfilter section, line %d] (%s)") % (linecount,self.nconfigfile)
                    print _("I don't understand: '"), command,":", spaced_value,"'"
                    print _("(Maybe a <server> or <global> command in a <postfilter> section?)")
                    sys.exit(1)




#---------------OUTSIDE SCOPE--------------------------------------------------
            elif command == '<server>' or command == '<servidor>':
                self.server_setdefaults()
                self.insideserver = 1

            elif command == '<global>':
                self.insideglobal = 1

            elif command == '<postfilter>' or command == '<postfiltro>':
                self.postfilter_setdefaults()
                self.insidepostfilter = 1

            elif command == '</server>' or command == '</servidor>':
                print _("Config file error (line %d): </server> outside <server>") % linecount
                sys.exit(1)

            elif command == '</global>':
                print _("Config file error (line %d): </global> outside <global>") % linecount

            elif command == '</postfilter>' or command == '</postfiltro>':
                print _("Config file error (line %d): </postfilter> outside <postfilter>") % linecount

            elif command != '' and command !='\n':
                print _("Error in config file (%s, line %d)") % (self.nconfigfile,linecount)
                print _("I don't understand: "), command,":", spaced_value
                print _("(Maybe a command outside of a <server> or <global> group?)")
                sys.exit(1)

        #Now some integrity checks...
        if self.notInAccept == 'reply' and self.replyaddress == '':
            print _("Error in config file, 'reply to messages not in the accept file' enabled")
            print _("but no ReplyAddress specified")
            sys.exit(1)
