# -*- coding: UTF-8 -*-

""" General utility functions and Application globals"""
import time, syslog, sys, locale, os, re, rfc822, StringIO
from gettext import gettext
_ = gettext

re_escapefrom = re.compile(r'^(?P<gts>\>*)From ', re.MULTILINE)
Application = None # Reference initialized in AnimailMain

# Application Globals

PROG_HOME = '/usr/share/lib/animail'
VERSION = '2.0'

BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
VIOLET = 35
CYAN = 36
WHITE = 37

ReplyDefaultStr = """
[En español más abajo]
[In italiano in seguito]

[English]
------------------------------------------------------------------------
This  message has  been  automatically generated  by  an anti-spam  mail
system running  on my machine.  It's intented to avoid  unsolicited mail
(spam) while assuring legitimate email don't get deleted.

The email you have send to my address  is not in my list of address that
are automatically allowed to pass my  filters. If your mail was not spam
then please take just a second to reply to this message without changing
the subject (re: prepositions to the subject are alloweb). This way your
mail will  shown on my  mail program and  future mails comming  from you
will be shown automatically. If you reply to this message this should be
the last time you see it.

Thanks,
        The Animail anti-spam system

[Español]
------------------------------------------------------------------------
Este   mensaje  ha   sido  generado   automáticamente  por   un  sistema
anti-publicidad que  se ejecuta  en mi máquina.  Su propósito  es evitar
correo electrónico no solicitado (spam) al  tiempo que se asegura de que
no se pierden emails legítimos.

El  email  que  ha enviado  a  mi  dirección  no  está en  mi  lista  de
direcciones a  aceptar automáticamente. Si  su correo no  era publicidad
entonces por favor  tómese un segundo para responder a  este mensaje sin
modificar el  asunto del mismo, y  tanto su mensaje anterior  como todos
los  mensajes que  envíe en  un futuro  a mi  dirección serán  aceptados
automáticamente, y esta será la última vez que vea este mensaje.

Gracias,
        El sistema anti-publicidad Animail

[Italiano]
-------------------------------------------------------------------------

Questo  messaggio   é  stato   creato  automaticamente  da   un  sistema
anti-pubblicitá eseguito dal  mio computer,al fine sia  di evitare posta
elettronica non desiderata (spam) sia per assicurarsi che non si perdano
e-mails legittimi.

L'e-mail  che  ha  inviato  al  mio indirizzo  non  é  nella  mia  lista
di  indirizzi  da  accettare  automaticamente.  Se  il  suo  e-mail  non
era  pubblicitario, la  prego  di rispondere  a  questo messaggio  senza
modificarne il  "subject". Cosí,  tanto il suo  messaggio come  i futuri
e-mails che mi manderá, saranno accettati automaticamente, e questa sará
l'ultima volta che riceverá questo e-mail.

Grazie,
        Il sistema anti-pubblicitá Animail
-------------------------------------------------------------------------

[If you want to know more about Animail visit http://animail.sf.net]
[Si desea saber más sobre Animail visite http://escomposlinux.org/fer_y_juanjo/animail.html]
[Se desidera ulteriori informazioni sull'Animail visiti http://animail.sf.net]
"""

ConfirmDefaultStr = """
[En español más abajo]
[In italiano in seguito]

[English]
-------------------------------------------------------------------------
Ok,  your message/s have  been  delivered to  me and  you're  now in  my
auto-accept list. Thanks.

[Español]
-------------------------------------------------------------------------
Su mensaje o mensajes han sido  entregados, y  usted ha sido añadido a mi
lista de aceptados automáticamente. Gracias.

[Italiano]
-------------------------------------------------------------------------
Il suo messaggio o messaggi sono stati ricevuti, e lei é stato aggiunto
alla mia lista di accettati automaticamente. Grazie.
"""

# Utility functions

class PideMensajeError(Exception): pass
#-------------------------------------------------------------------
def take_date():
        """returns a date string in a format suitable for email messages"""
        loc = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, "C")
        date = time.strftime( ('%a %b %d %H:%M:%S %Y'), time.localtime(time.time()))
        locale.setlocale(locale.LC_ALL, loc)
        return date
#-------------------------------------------------------------------
def aprint(str, color,prioridad=syslog.LOG_NOTICE, iserror=0):
        """print to the standar output, error or system log, and apply colors"""
        if Application.config.optcheck: return
        if Application.config.optsyslog: syslog.syslog(prioridad, str)
        elif iserror: sys.stderr.write(str+'\n')
        else:
            if not Application.config.optcolors: print str
            else: print "\033[%d;01m%s\033[m" % (color, str)

#-------------------------------------------------------------------
def colorize(str, color):
        """colorize a string with the color specified in the parameter"""
        if Application.config.optcolors:
            return "\033[%d;01m%s\033[00m" % (color, str)
        else:
            return str
#-------------------------------------------------------------------

def compute(bytes):
    if   bytes < 1024:
        return (bytes, 'Bytes')
    elif bytes >= 1024 and bytes < (1024 * 1024):
        return (bytes / 1024.0, 'KiloBytes')
    elif bytes < (1024 * 1024 * 1024.0):
        return (bytes / (1024 * 1024.0), 'MegaBytes')
    else: return (bytes / (1024 * 1024 * 1024.0), 'TeraBytes')
#-------------------------------------------------------------------
def cursor_on():
    print '\33[?25h'

def cursor_off():
    print '\33[?25l'
#-------------------------------------------------------------------
def ins_ordered(list, element):
        pos = 0
        try:
            while element['size'] < list[pos]['size']:
                pos += 1
        except IndexError:
            list.append(element)
            return
        list.insert(pos,element)
#-------------------------------------------------------------------
def ins_ordered_inv(list, element):
        pos = 0
        try:
            while element['size'] > list[pos]['size']:
                pos += 1
        except IndexError:
            list.append(element)
            return
        list.insert(pos,element)
#-------------------------------------------------------------------
def PipeToCmd(msgfile, resend, towho, pipecmd):
        if resend: destList = towho
        else:
            caduser = ''.join((Application.config.sysuser, '@localhost'))
            destList = [caduser]

        if Application.config.optv: print _("ISAY: (Piping the message to the program)")

        for dest in destList:
            pipeCmd = pipecmd.strip() + ' ' + dest
            pip = os.popen(pipeCmd, 'w')
            msgfile.seek(0)
            mail = msgfile.read()
            pip.write(mail)
            pip.write('\n\n')
            pip.close()
#-------------------------------------------------------------------
def usage():
    print """
Animail (c) 1998-2002 Juan José Álvarez Martínez

This program is FREE software. You can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your opinion) any later version.

This program is distributed in the HOPE that it will be USEFUL,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

COMMAND LINE OPTIONS

The following options will override the config file settings
when passed as command line options

-h or --help                    Show this help
-F or --only-filter             Only filter, don't download messages
-l or --no-summary              Don't show the operation summary at the end
-o or --download-order=arrival  Transfer messages by arrival order
-o or --download-order=small    Transfer first the smaller messages
-o or --download-order=big      Transfer first the bigger messages
-f or --mbox-file=file          Save message to the specified mbox format file
-v or --verbose                 Verbose mode
-s or --max-size=num            Maximun message size, in bytes
-n or --max-to-download=num     Maximun number of messages to download
-B or --syslog-output           Redirect all program output to the syslog
-t or --quiet                   Don't show the downloaded percent while downloading messages
-O or --only-from=servers       Only dowload messages from the given list of servers
-C or --check                   Only check for existing mail, don't download if
-F or --fetchmail               Only check for existing mail, don't download if (fetchmail style)

To get more information about the config file please read the program
documentation.
"""
    sys.exit(1)



