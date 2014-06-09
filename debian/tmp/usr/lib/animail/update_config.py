#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os, pwd, sys, copy

def nothing(str):
    return str

_ = nothing

class ConfigAgent:
#-------------------------------------
    def __init__(self):
        pwddata = pwd.getpwuid( os.getuid() )
        self.sysuser = pwddata[0]
        self.homedir = pwddata[5]
        #del foo
        self.nconfigfile = ''.join( (self.homedir, '/.animailrc'))
        self.globalconf = {}
        self.lservers = []
#-----------------------------------------
    def printdata(self):
        print str(self.lservers)
        print str(self.globalconf)
#-----------------------------------------
    def parseConfigFile(self):
        globalconf = self.globalconf
        linecount = 0
        try:
            fsize = os.stat(self.nconfigfile)[6]
        except OSError, x:
            print _("Error trying to open the config file %s: %s") % (self.nconfigfile, str(x))
            sys.exit(1)
        if fsize == 0 or (not os.path.exists(self.nconfigfile)):
            print _("WARNING: Config file don't exists or it's empty. Please configure Animail")
            sys.exit(1)

        try:
            lconfig = open(self.nconfigfile, 'r').readlines()
        except IOError:
            print _("I can't read the config file (%s)!") % self.nconfigfile
            sys.exit(1)

        for line in lconfig:
            linecount+=1
            tmplist = line.split(':', 2)
            if tmplist == ['\012'] or tmplist == ['#']: continue
            if tmplist[0][0] == '#': continue
            spaced_value = ''

            try:
                [command, spaced_value] = tmplist
            except ValueError: # <command>
                command = tmplist[0].strip()
            command = command.lower()

            if spaced_value.isspace():
                print _("Error (line %d), the parameter of '%s' is empty") % (linecount,command)
                sys.exit(1)

            value = spaced_value.strip()
#--------------------BY SERVER OPTIONS----------------------------------------------
            if command == 'servidor' or command == 'server' or command == 'servidorpop3' or command == 'pop3server':
                thisserver = {}
                thisserver['address'] = value

            elif command == 'port' or command == 'puerto':
                thisserver['port'] = value

            elif command == 'username' or command == 'nombreusuario':
                thisserver['username'] = value

            elif command == 'protocol' or command == 'protocolo':
                thisserver['protocol']=value

            elif command == 'ssl':
                thisserver['ssl'] = value

            elif command == 'keeponserver' or command == 'mantenerenservidor':
                thisserver['optdelete']=value

            elif command == 'resendto' or command == 'reenviara':
                thisserver['towho_list'] = spaced_value

            elif command == 'pass' or command == 'passwd' or command == 'password' or command=='clave' or command=='contraseña':
                thisserver['pass'] = value
                self.lservers.append(copy.deepcopy(thisserver))
                del thisserver #FIXME: Comprobar que lo borra realmente
#-----------------GLOBAL OPTIONS---------------------------------------------------
            elif command == 'smtpserver' or command == 'servidorsmtp':
                globalconf['smtpserver'] = value

            elif command == 'timeout':
                globalconf['timeout'] = value

            elif command == 'moretime' or command == 'mastiempo':
                globalconf['moretime'] = value

            elif command == 'smtpport' or command == 'puertosmtp':
                globalconf['smtpport'] = value

            elif command == 'maxsize' or command == 'tamañomaximo':
                globalconf['maxsize'] = value

            elif command == 'maxnumber' or command == 'numeromaximo':
                globalconf['maxnumber'] = value

            elif command == 'mboxfile' or command == 'archivobuzon':
                globalconf['mboxfile'] = value

            elif command == 'maildir':
                globalconf['maildir'] = value

            elif command == 'colorize' or command == 'colorear':
                globalconf['colorize'] = value

            elif command == 'downloadorder' or command == 'ordendetransferencia':
                globalconf['downloadorder'] = value

            elif command == 'uselocalmta' or command == 'usarmtalocal':
                globalconf['optsmtp'] = value

            elif command == 'usesendmail' or command == 'usarsendmail':
                globalconf['optsendmail'] = value

            elif command == 'sendmailcommand' or command == 'comandosendmail':
                globalconf['sendmailcmd'] = spaced_value

            elif command == 'useregexp' or command == 'usarexpreg':
                globalconf['regularexp'] = value

            elif command == 'mailer' or command == 'lector':
                globalconf['mailer'] = value
#---------------OUTSIDE SCOPE--------------------------------------------------

            elif command != '' and command !='\n':
                print _("Error in config file (%s, line %d)") % (self.nconfigfile,linecount)
                print _("I don't understand: "), command,":", spaced_value
                sys.exit(1)

    def writeconfig(self):
        print "# animailrc file created from old config file by update_config.py"
        print "# Edit at you hearth contents..."
        print
        print "#Servers sections", "-"*25
        for server in self.lservers:
            print "<Server>"

            if server.has_key('address'):
                print "Address:", server['address']

            if server.has_key('username'):
                print "Username:", server['username']

            if server.has_key('pass'):
                print "Password:", server['pass']

            if server.has_key('port'):
                print "Port:", server['port']

            if server.has_key('protocol'):
                print "Protocol:", server['protocol']

            if server.has_key('ssl'):
                print "SSL:", server['ssl']

            if server.has_key('optdelete'):
                print "KeepOnServer:", server['optdelete']

            if server.has_key('towho_list'):
                print "ResendTo:", server['towho_list']

            print "</Server>"
            print

        g = self.globalconf

        print "#Global section", "-"*25
        print "<Global>"

        if g.has_key('smtpserver'):
            print "SMTPServer:", g['smtpserver']

        if g.has_key('timeoout'):
            print "Timeout:", g['timeout']

        if g.has_key('moretime'):
            print "MoreTime:", g['moretime']

        if g.has_key('smtpport'):
            print "SMTPPort:", g['smtpport']

        if g.has_key('maxsize'):
            print "MaxSize:", g['maxsize']

        if g.has_key('moretime'):
            print "MoreTime:", g['moretime']

        if g.has_key('maxnumber'):
            print "MaxNumber:", g['maxnumber']

        if g.has_key('mboxfile'):
            print "MBoxfile:", g['mboxfile']

        if g.has_key('maildir'):
            print "MailDir:", g['maildir']

        if g.has_key('colorize'):
            print "Colorize:", g['colorize']

        if g.has_key('downloadorder'):
            print "DownloadOrder:", g['downloadorder']

        if g.has_key('optsmtp'):
            print "UseLocalMTA:", g['optsmtp']

        if g.has_key('optsendmail'):
            print "UseSendmail:", g['optsendmail']

        if g.has_key('sendmailcmd'):
            print "SendmailCommand:", g['sendmailcmd']

        if g.has_key('regularexp'):
            param = g['regularexp'].lower()
            if param == 'yes' or param == 'si' or param == 'sí':
                print "FilterFile:", ''.join( (self.homedir, '/.animailfilters'))

        if g.has_key('mailer'):
            print "Mailer:", g['mailer']

        print "</Global>"


c = ConfigAgent()
c.parseConfigFile()
c.writeconfig()

