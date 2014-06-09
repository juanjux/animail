# -*- coding: UTF-8 -*-
#from animail import AnimailMain, general
import AnimailMain
from general import compute, colorize, RED, CYAN, VIOLET, GREEN

from gettext import gettext
_ = gettext

import time

"""
    Don't Panic.

    self.lserv is:

    A LIST which elements (D) are DICTIONARIES with two keys
    'dfilt' and 'ddesc'. The value of each is another DICTIONARY that have and
    key for each regular expresion / origin,
    and which value is a LIST with two INTEGER elements, the number of filtered
    messages | downloaded, for each regular expresion | origin, and the volume

|__D__|__D__|__D__|__D__|  self.lserv
        |
,- '                                               (d)
|
|                ,-> 'dfilt':  ,-> ".*spammer.spam.*" : |__number__|__volume__|
|                |                         |
|                |                         |-> ".*mierda.com.*"   : |__number__|__volume__|
|                |                         |
|                |                         `->     (etc)                  : |__number__|__volume__|
|                |                                                                                      [0]                [1]
`-> D: --|
                        |                                         (d)
                        |                                              |
                        `-> 'ddesc':  ,-> "jajs@retemail.es" : |__number__|__volume__|
                                            |
                                            `-> "amigote@amig.es"  : |__number__|__volume__|
                                                [0]                     [1]

Example: to access the volume of the downloaded messages with origin pepe@pepe.com of
the server with index 3:

self.lserv[3]['ddesc']['pepe@pepe.com'][VOLUME]

Easy, Isn't it? ;)
"""

# To make things cleaner:
VOLUME = 1
NUMBER = 0

class LogAgent(object):
            def __init__(self):
                    self.config = AnimailMain.Application.config
                    self.lserv = {}
#-----------------------------
            def new(self,adress,key):
                    dservtmp = {}
                    dservtmp['name'] = adress
                    dservtmp['numdesc'] = 0
                    dservtmp['numpost'] = 0
                    dservtmp['dfilt'] = {}
                    dservtmp['ddesc'] = {}
                    dservtmp['dpost'] = {}
                    dservtmp['incidents'] = []
                    dservtmp['numfilt'] = 0
                    dservtmp['numtotal'] = 0
                    dservtmp['tamtotal'] = 0
                    dservtmp['filtered_vol'] = 0
                    dservtmp['downloaded_vol'] = 0
                    dservtmp['post_vol'] = 0

                    self.lserv[key] = dservtmp
                    return key
                    #return self.lserv.index(dservtmp)
#---------------------------------------------------------
            def giveme_size_num(self, number, tamanio, key):
                    self.lserv[key]['numtotal'] = number
                    self.lserv[key]['tamtotal'] = tamanio
#---------------------------------------------------------
            def append_filtered(self, key, pattern, volume):
                    if self.lserv[key]['dfilt'].has_key(pattern):
                            self.lserv[key]['dfilt'][pattern][NUMBER] += 1
                            self.lserv[key]['dfilt'][pattern][VOLUME] += volume
                    else:
                            self.lserv[key]['dfilt'][pattern] = []
                            self.lserv[key]['dfilt'][pattern].append(1) # First element on this pattern
                            self.lserv[key]['dfilt'][pattern].append(volume)
                    # end if
                    self.lserv[key]['numfilt'] += 1
                    self.lserv[key]['filtered_vol'] += volume
#---------------------------------------------------------

            def append_downloaded(self, key, from_, volume):
                    if self.lserv[key]['ddesc'].has_key(from_):
                            self.lserv[key]['ddesc'][from_][NUMBER] += 1
                            self.lserv[key]['ddesc'][from_][VOLUME] += volume
                    else:
                            self.lserv[key]['ddesc'][from_] = []
                            self.lserv[key]['ddesc'][from_].append(1)
                            self.lserv[key]['ddesc'][from_].append(volume)
                    # end if
                    self.lserv[key]['numdesc'] += 1
                    self.lserv[key]['downloaded_vol'] += volume
#---------------------------------------------------------
            def append_postergated(self,key,from_,volume):
                    if self.lserv[key]['dpost'].has_key(from_):
                            self.lserv[key]['dpost'][from_][NUMBER] += 1
                            self.lserv[key]['dpost'][from_][VOLUME] += volume
                    else:
                            self.lserv[key]['dpost'][from_] = []
                            self.lserv[key]['dpost'][from_].append(1)
                            self.lserv[key]['dpost'][from_].append(volume)
                    self.lserv[key]['numpost'] += 1
                    self.lserv[key]['post_vol'] += volume
#---------------------------------------------------------
            def incident(self, key, strena):
                    self.lserv[key]['incidents'].append(strena)
#---------------------------------------------------------
            def show(self):
                    str = ''
                    tmpstr = colorize(_("\n####### Operation summary #######\n\n"), VIOLET)
                    str = ''.join(tmpstr)
                    #FIXME: This should be on local time format (including weekday names)
                    date = time.strftime( ('%a %b %d %H:%M:%S %Y\n'), time.localtime(time.time()))
                    str = ''.join( (str, colorize(date, GREEN)) )
                    for serv in self.lserv.values():
                            tmpstr = colorize(_("\n--- Server: "), CYAN)
                            tmpstr2 = colorize("%s\n\n" % serv['name'], RED)
                            str = ''.join( (str, tmpstr, tmpstr2) )

                            tmpstr = colorize(_("* Total messages: "), CYAN)
                            tmpstr2 = colorize("%s\n" % serv['numtotal'], GREEN)
                            str = ''.join( (str, tmpstr, tmpstr2) )

                            tmpstr = colorize(_("* Total volume on server: "), CYAN)
                            tmpstr2 = colorize("%.2f %s\n" % (compute(serv['tamtotal'])), GREEN)
                            str = ''.join( (str, tmpstr, tmpstr2) )

                            tmpstr = colorize(_("* Filtered messages: "), CYAN)
                            tmpstr2 = colorize("%d\n" % serv['numfilt'], GREEN)
                            str = ''.join( (str, tmpstr, tmpstr2) )
                            if serv['numfilt'] > 0:
                                    tmpstr = colorize(_("\tTotal filtered volume: "), CYAN)
                                    tmpstr2 = colorize("%.2f %s\n" % compute(serv['filtered_vol']), RED)
                                    str = ''.join( (str, tmpstr, tmpstr2) )

                            tmpstr = colorize(_("* Downloaded messages: "), CYAN)
                            tmpstr2 = colorize("%d\n" % serv['numdesc'], GREEN)
                            str = ''.join( (str, tmpstr, tmpstr2) )
                            if serv['numdesc'] > 0:
                                    tmpstr = colorize(_("\tDownloaded Volume: "), CYAN)
                                    tmpstr2 = colorize("%.2f %s\n" % compute(serv['downloaded_vol']), GREEN)
                                    str = ''.join( (str, tmpstr, tmpstr2) )

                            tmpstr = colorize(_("* Postergated messages: "), CYAN)
                            tmpstr2 = colorize("%d\n" % serv['numpost'], GREEN)
                            str = ''.join( (str, tmpstr, tmpstr2) )
                            if serv['numpost'] > 0:
                                    tmpstr = colorize(_("\tPostergated Volume: "), CYAN)
                                    tmpstr2 = colorize("%.2f %s\n" % compute(serv['post_vol']),GREEN)
                                    str = ''.join( (str,tmpstr,tmpstr2) )

                            if serv['numfilt'] > 0:
                                    tmpstr = colorize(_("\n* Patterns of filtered messages:\n"), CYAN)
                                    str = ''.join( (str, tmpstr) )
                                    for pattern in serv['dfilt'].keys():
                                        str = ''.join( (str, colorize("\t%d" % serv['dfilt'][pattern][NUMBER],RED)) )
                                        str = ''.join( (str, colorize(" %s " % pattern, RED)))
                                        str = ''.join( (str, colorize("\t\t%.2f %s\n" % compute(serv['dfilt'][pattern][VOLUME]), RED)) )

                            if serv['numdesc'] > 0:
                                    tmpstr = colorize(_("* Origin of downloaded messages:\n"), CYAN)
                                    str = ''.join( (str, tmpstr) )
                                    for origin in serv['ddesc'].keys():
                                        str = ''.join( (str, colorize("\t%d" % serv['ddesc'][origin][NUMBER], GREEN)))
                                        str = ''.join( (str, colorize(" %s " % origin, GREEN)))
                                        str = ''.join( (str, colorize("%.2f %s\n" % compute(serv['ddesc'][origin][VOLUME]), GREEN)))

                            if serv['numpost'] > 0:
                                    tmpstr = colorize(_("* Origin of postergated messages:\n"),CYAN)
                                    str = ''.join( (str, tmpstr) )
                                    for origin in serv['dpost'].keys():
                                        str = ''.join( (str,colorize("\t%d" % serv['dpost'][origin][NUMBER], GREEN)))
                                        str = ''.join( (str, colorize(" %s " % origin, GREEN)))
                                        str = ''.join( (str, colorize("%.2f %s\n" % compute(serv['dpost'][origin][VOLUME]),GREEN)))

                            if serv['incidents'] != []:
                                    tmpstr = colorize(_("* Incidents:\n"), CYAN)
                                    str = ''.join( (str, tmpstr) )
                                    for inc in serv['incidents']:
                                        str = ''.join( (str, colorize("\t-%s\n" % inc, RED)) )
                    print str
# end class LogAgent

