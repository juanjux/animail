#from animail import AnimailMain, general
import fcntl, popen2, os, rfc822
from gettext import gettext
import AnimailMain, general

_ = gettext
aprint = general.aprint

class postFilterException(Exception):
    pass

class PostFilter(object):
    def __init__(self, path):
        self.path = path
        self.filtername = "No filter name, this should't be happening (this is a BUG)"
        self.inputstdin = True
        self.options = ''
        self.realoptions = ''
        self.killreturnvalues = []
        self.killprogramoutput = None
        self.showfilteroutput = False
        self.config = AnimailMain.Application.config
        self.savepostfilteredmails = 0

    def filter_mail(self,msgstr,msgpath):
        if self.options != '': self.realoptions = self.options.replace('%M',msgpath)
        try:      # Capture stdout and stderr on the same stream
            progPipe = None
            if self.savepostfilteredmails <= 2:
                progPipe = popen2.Popen4(self.path.strip() + " " + self.realoptions.strip())
            elif self.savepostfilteredmails == 3: # The same but without stderr
                progPipe = popen2.Popen3(self.path.strip() + " " + self.realoptions.strip())
            if self.inputstdin:
                progPipe.tochild.write(msgstr)
                progPipe.tochild.write('\n\n')
                progPipe.tochild.close()

            #FIXME: This could block forever (see in what cases and try to avoid them)!
            output = progPipe.fromchild.read()
            if (output != '') and self.showfilteroutput:
                aprint(_("Output of the post-filter '%s' was:\n%s") % (self.filtername, output),general.YELLOW)
            progPipe.fromchild.close()
            retcode = os.WEXITSTATUS(progPipe.poll())
        except:
            import traceback,cStringIO
            tb = cStringIO.StringIO()
            aprint(_("Uh, something bad happened while trying to use the post-filter %s") % self.filtername,general.RED)
            aprint(_("Error was:\n"), general.RED)
            traceback.print_exc(file=tb)
            aprint (tb.getvalue(),general.RED)
            aprint(_("Not using filter"),general.RED)
            return (0,'')
        if self.killreturnvalues != []:
            for i in self.killreturnvalues:
                if int(i) == retcode: 
                    aprint(_("Killer return code of filter %s matched for this message, won't be delivered") % self.filtername,general.RED)
                    return (1,output)

        if self.killprogramoutput != None:
            res = self.killprogramoutput.search(output)
            if res != None:
                aprint(_("Killer output from filter %s matched for this message, won't be delivered") % self.filtername,general.RED)
                return (1,output)

        return (0,'')

    def process_mail(self,mail):
        header = ''
        body = ''
        sep = mail.find('\n\n')

        header = mail[0:sep]
        body = mail[sep:]
        
        body = general.re_escapefrom.sub ('>\g<gts>From ', body)
        return header+body

    def write_mbox(self,msgstr,fromm):    
        if self.config.postfilteredmailsmbox == '':
            aprint(_("Warning: SavePostFilteredMails activated for this %s PostFilter but no") % self.filtername, general.RED)
            aprint(_("PostFilteredMailsMBox configured: Won't save the email"), general.RED)
            return
        aprint(_("Saving message to %s...") % self.config.postfilteredmailsmbox,general.RED)
        try:
            mbox = open(self.config.postfilteredmailsmbox,'a+')
            fcntl.flock(mbox.fileno(), fcntl.LOCK_EX)
            mbox.seek(0,2)
            (foo,emailaddr) = rfc822.parseaddr(fromm)
            strfromm = 'From %s' % emailaddr + ' ' + general.take_date() + '\n'
            mbox.write(strfromm)
            mbox.write(self.process_mail(msgstr))
            mbox.flush()
            fcntl.flock(mbox.fileno(), fcntl.LOCK_UN)
            mbox.close()
        except IOError, x:
            try:
                fcntl.flock(mbox.fileno(), fcntl.LOCK_UN)
                mbox.close()
            except:
                pass
            aprint(_("Sorry, couldn't save the filtered message to %s: %s") % (self.config.postfilteredmailsmbox,x), general.RED)

    def log_filtered_mail(self,msgstr,fromm,output):
        if self.savepostfilteredmails == 1:
            self.write_mbox(msgstr,fromm)
        elif self.savepostfilteredmails == 2 or self.savepostfilteredmails == 3:
            self.write_mbox(output,fromm)
        else: 
            aprint(_("Error: In log_filtered_mail value is not 1, 2 or 3"),general.RED)
        
                
                
        
            
            
            

