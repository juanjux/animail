#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Form implementation generated from reading ui file 'interface.ui'
#
# Created: Wed Nov 21 23:21:32 2001
#      by: The Python User Interface Compiler (pyuic)
#
# WARNING! All changes made in this file will be lost!


sys.path.append('/usr/lib/animail')

from qt import *
import configlib
#from animail import configlib


class window(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        self.configAgent = configlib.ConfigAgent()
        self.configAgent.parseConfigFile()

        QDialog.__init__(self,parent,name,modal,fl)

        if name == None:
            self.setName('window')                    

        self.resize(451,412)
        self.setCaption(self.tr('Animail configuration'))

        self.but_undo = QPushButton(self,'but_undo')
        self.but_undo.setGeometry(QRect(260,380,93,26))
        self.but_undo.setText(self.tr('Undo all'))

        self.but_save = QPushButton(self,'but_save')
        self.but_save.setGeometry(QRect(160,380,93,26))
        self.but_save.setText(self.tr('Save config'))

        self.but_cancel = QPushButton(self,'but_cancel')
        self.but_cancel.setGeometry(QRect(360,380,93,26))
        self.but_cancel.setText(self.tr('Cancel'))

        self.tab = QTabWidget(self,'tab')
        self.tab.setGeometry(QRect(10,0,440,380))

        self.tab_servers = QWidget(self.tab,'tab_servers')

        self.CheckBox1 = QCheckBox(self.tab_servers,'CheckBox1')
        self.CheckBox1.setGeometry(QRect(160,100,130,20))
        self.CheckBox1.setText(self.tr('Use user defined port'))

        self.label_address = QLabel(self.tab_servers,'label_address')
        self.label_address.setGeometry(QRect(160,10,90,20))
        self.label_address.setText(self.tr('Adress'))

        self.label_username = QLabel(self.tab_servers,'label_username')
        self.label_username.setGeometry(QRect(160,40,90,20))
        self.label_username.setText(self.tr('Username'))

        self.label_passwd = QLabel(self.tab_servers,'label_passwd')
        self.label_passwd.setGeometry(QRect(160,70,90,20))
        self.label_passwd.setText(self.tr('Password'))

        self.edit_address = QLineEdit(self.tab_servers,'edit_address')
        self.edit_address.setGeometry(QRect(290,10,110,22))

        self.edit_username = QLineEdit(self.tab_servers,'edit_username')
        self.edit_username.setGeometry(QRect(290,40,110,22))

        self.edit_passwd = QLineEdit(self.tab_servers,'edit_passwd')
        self.edit_passwd.setGeometry(QRect(290,70,110,22))
        self.edit_passwd.setEchoMode(QLineEdit.Password)

        self.label_port = QLabel(self.tab_servers,'label_port')
        self.label_port.setEnabled(0)
        self.label_port.setGeometry(QRect(160,130,90,20))
        self.label_port.setText(self.tr('Port'))

        self.spin_port = QSpinBox(self.tab_servers,'spin_port')
        self.spin_port.setEnabled(0)
        self.spin_port.setGeometry(QRect(290,130,110,21))
        self.spin_port.setMaxValue(65536)
        self.spin_port.setValue(110)

        self.label_protocol = QLabel(self.tab_servers,'label_protocol')
        self.label_protocol.setGeometry(QRect(160,160,90,20))
        self.label_protocol.setText(self.tr('Protocol'))

        self.check_ssl = QCheckBox(self.tab_servers,'check_ssl')
        self.check_ssl.setGeometry(QRect(160,190,130,20))
        self.check_ssl.setText(self.tr('Server uses SSL'))

        self.combo_protocol = QComboBox(0,self.tab_servers,'combo_protocol')
        self.combo_protocol.insertItem(self.tr('POP3'))
        self.combo_protocol.insertItem(self.tr('IMAP4'))
        self.combo_protocol.insertItem(self.tr('APOP'))
        self.combo_protocol.setGeometry(QRect(290,160,88,22))
        self.combo_protocol.setEditable(0)

        self.but_remove_server = QPushButton(self.tab_servers,'but_remove_server')
        self.but_remove_server.setGeometry(QRect(240,320,93,26))
        self.but_remove_server.setText(self.tr('Remove server'))

        self.but_modify_server = QPushButton(self.tab_servers,'but_modify_server')
        self.but_modify_server.setGeometry(QRect(340,320,93,26))
        self.but_modify_server.setText(self.tr('Modify server'))

        self.list_servers = QListBox(self.tab_servers,'list_servers')
        self.list_servers.setGeometry(QRect(10,10,140,240))

        self.check_keep = QCheckBox(self.tab_servers,'check_keep')
        self.check_keep.setGeometry(QRect(160,220,170,20))
        self.check_keep.setText(self.tr('Keep messages on the server'))

        self.combo_resend = QComboBox(0,self.tab_servers,'combo_resend')
        self.combo_resend.setEnabled(0)
        self.combo_resend.setGeometry(QRect(200,260,110,22))
        self.combo_resend.setEditable(1)

        self.but_add_resend = QPushButton(self.tab_servers,'but_add_resend')
        self.but_add_resend.setEnabled(0)
        self.but_add_resend.setGeometry(QRect(320,260,50,26))
        self.but_add_resend.setText(self.tr('Add'))

        self.but_remove_resend = QPushButton(self.tab_servers,'but_remove_resend')
        self.but_remove_resend.setEnabled(0)
        self.but_remove_resend.setGeometry(QRect(380,260,50,26))
        self.but_remove_resend.setText(self.tr('Remove'))

        self.check_resend = QCheckBox(self.tab_servers,'check_resend')
        self.check_resend.setGeometry(QRect(10,260,190,20))
        self.check_resend.setText(self.tr('Resend messages of this server, to:'))

        self.Line1 = QFrame(self.tab_servers,'Line1')
        self.Line1.setGeometry(QRect(-20,300,450,20))
        self.Line1.setFrameStyle(QFrame.HLine | QFrame.Sunken)

        self.but_add_server = QPushButton(self.tab_servers,'but_add_server')
        self.but_add_server.setEnabled(1)
        self.but_add_server.setGeometry(QRect(140,320,93,26))
        self.but_add_server.setText(self.tr('Add server'))
        self.tab.insertTab(self.tab_servers,self.tr('Servers'))

        self.tab_delivery = QWidget(self.tab,'tab_delivery')

        self.butGroup_delivery = QButtonGroup(self.tab_delivery,'butGroup_delivery')
        self.butGroup_delivery.setGeometry(QRect(10,10,420,340))
        self.butGroup_delivery.setTitle(self.tr('Delivery options'))

        self.label_mbox = QLabel(self.butGroup_delivery,'label_mbox')
        self.label_mbox.setEnabled(0)
        self.label_mbox.setGeometry(QRect(30,70,56,20))
        self.label_mbox.setText(self.tr('MBox file'))

        self.edit_mbox = QLineEdit(self.butGroup_delivery,'edit_mbox')
        self.edit_mbox.setEnabled(0)
        self.edit_mbox.setGeometry(QRect(140,70,110,22))
		

        self.toolbut_maildir = QToolButton(self.butGroup_delivery,'toolbut_maildir')
        self.toolbut_maildir.setEnabled(0)
        self.toolbut_maildir.setGeometry(QRect(260,120,20,20))
        self.toolbut_maildir.setText(self.tr('...'))

        self.label_pipe = QLabel(self.butGroup_delivery,'label_pipe')
        self.label_pipe.setEnabled(0)
        self.label_pipe.setGeometry(QRect(30,180,56,20))
        self.label_pipe.setText(self.tr('Command'))

        self.label_maildir = QLabel(self.butGroup_delivery,'label_maildir')
        self.label_maildir.setEnabled(0)
        self.label_maildir.setGeometry(QRect(30,120,90,20))
        self.label_maildir.setText(self.tr('Maildir directory'))

        self.radio_smtp = QRadioButton(self.butGroup_delivery,'radio_smtp')
        self.radio_smtp.setGeometry(QRect(10,20,220,20))
        self.radio_smtp.setText(self.tr('To a local SMTP server'))
        self.butGroup_delivery.insert(self.radio_smtp,0)

        self.radio_mbox = QRadioButton(self.butGroup_delivery,'radio_mbox')
        self.radio_mbox.setGeometry(QRect(10,50,120,20))
        self.radio_mbox.setText(self.tr('To a mbox file'))

        self.radio_maildir = QRadioButton(self.butGroup_delivery,'radio_maildir')
        self.radio_maildir.setGeometry(QRect(10,100,130,20))
        self.radio_maildir.setText(self.tr('To a Maildir directory'))
        self.butGroup_delivery.insert(self.radio_maildir,0)

        self.radio_pipe = QRadioButton(self.butGroup_delivery,'radio_pipe')
        self.radio_pipe.setGeometry(QRect(10,150,230,20))
        self.radio_pipe.setText(self.tr('Pipe each downloaded mail to a command'))
        self.butGroup_delivery.insert(self.radio_pipe,0)

        self.toolbut_mbox = QToolButton(self.butGroup_delivery,'toolbut_mbox')
        self.toolbut_mbox.setEnabled(0)
        self.toolbut_mbox.setGeometry(QRect(260,70,20,20))
        self.toolbut_mbox.setText(self.tr('...'))

        self.edit_maildir = QLineEdit(self.butGroup_delivery,'edit_maildir')
        self.edit_maildir.setEnabled(0)
        self.edit_maildir.setGeometry(QRect(140,120,110,22))

        self.edit_pipe = QLineEdit(self.butGroup_delivery,'edit_pipe')
        self.edit_pipe.setEnabled(0)
        self.edit_pipe.setGeometry(QRect(140,180,110,22))
        self.tab.insertTab(self.tab_delivery,self.tr('Delivery'))

        self.tab_filtering = QWidget(self.tab,'tab_filtering')

        self.check_regular = QCheckBox(self.tab_filtering,'check_regular')
        self.check_regular.setGeometry(QRect(10,10,190,20))
        self.check_regular.setText(self.tr('Activate regular expresion filtering'))

        self.frame_filters = QFrame(self.tab_filtering,'frame_filters')
        self.frame_filters.setEnabled(0)
        self.frame_filters.setGeometry(QRect(10,40,240,150))
        self.frame_filters.setFrameShape(QFrame.StyledPanel)
        self.frame_filters.setFrameShadow(QFrame.Raised)

        self.edit_filters = QLineEdit(self.frame_filters,'edit_filters')
        self.edit_filters.setGeometry(QRect(110,10,110,22))

        self.but_add_filters = QPushButton(self.frame_filters,'but_add_filters')
        self.but_add_filters.setGeometry(QRect(110,40,99,26))
        self.but_add_filters.setText(self.tr('Add filter'))

        self.but_remove_filters = QPushButton(self.frame_filters,'but_remove_filters')
        self.but_remove_filters.setGeometry(QRect(110,70,99,26))
        self.but_remove_filters.setText(self.tr('Remove filter'))

        self.but_change_filters = QPushButton(self.frame_filters,'but_change_filters')
        self.but_change_filters.setGeometry(QRect(110,100,99,26))
        self.but_change_filters.setText(self.tr('Change filter'))

        self.list_filters = QListBox(self.frame_filters,'list_filters')
        self.list_filters.setGeometry(QRect(10,10,96,120))

        self.check_htmlfilter = QCheckBox(self.tab_filtering,'check_htmlfilter')
        self.check_htmlfilter.setGeometry(QRect(10,200,150,20))
        self.check_htmlfilter.setText(self.tr('Filter all HTML mail'))

        self.check_maxnumber = QCheckBox(self.tab_filtering,'check_maxnumber')
        self.check_maxnumber.setGeometry(QRect(10,320,160,20))
        self.check_maxnumber.setText(self.tr('Don\'t download more than'))

        self.check_autoreply_filter = QCheckBox(self.tab_filtering,'check_autoreply_filter')
        self.check_autoreply_filter.setGeometry(QRect(10,230,230,20))
        self.check_autoreply_filter.setText(self.tr('Auto reply to filtered messages with the file:'))

        self.check_autoreply_html = QCheckBox(self.tab_filtering,'check_autoreply_html')
        self.check_autoreply_html.setGeometry(QRect(10,260,220,20))
        self.check_autoreply_html.setText(self.tr('Auto reply to HTML messages with the file:'))

        self.edit_autoreply_html = QLineEdit(self.tab_filtering,'edit_autoreply_html')
        self.edit_autoreply_html.setEnabled(0)
        self.edit_autoreply_html.setGeometry(QRect(240,260,110,22))

        self.check_maxsize = QCheckBox(self.tab_filtering,'check_maxsize')
        self.check_maxsize.setGeometry(QRect(10,290,160,20))
        self.check_maxsize.setText(self.tr('Filter messages greater than:'))

        self.spin_maxsize = QSpinBox(self.tab_filtering,'spin_maxsize')
        self.spin_maxsize.setEnabled(0)
        self.spin_maxsize.setGeometry(QRect(180,290,70,20))

        self.spin_maxnumber = QSpinBox(self.tab_filtering,'spin_maxnumber')
        self.spin_maxnumber.setGeometry(QRect(180,320,70,21))

        self.label_maxsize = QLabel(self.tab_filtering,'label_maxsize')
        self.label_maxsize.setGeometry(QRect(260,290,56,20))
        self.label_maxsize.setText(self.tr('bytes'))

        self.label_maxnumber = QLabel(self.tab_filtering,'label_maxnumber')
        self.label_maxnumber.setGeometry(QRect(258,317,130,20))
        self.label_maxnumber.setText(self.tr('messages in a single session'))

        self.tool_autoreply_filter = QToolButton(self.tab_filtering,'tool_autoreply_filter')
        self.tool_autoreply_filter.setEnabled(0)
        self.tool_autoreply_filter.setGeometry(QRect(360,230,20,20))
        self.tool_autoreply_filter.setText(self.tr('...'))

        self.edit_autoreply_filter = QLineEdit(self.tab_filtering,'edit_autoreply_filter')
        self.edit_autoreply_filter.setEnabled(0)
        self.edit_autoreply_filter.setGeometry(QRect(240,230,110,22))

        self.tool_autoreply_html = QToolButton(self.tab_filtering,'tool_autoreply_html')
        self.tool_autoreply_html.setEnabled(0)
        self.tool_autoreply_html.setGeometry(QRect(360,260,20,20))
        self.tool_autoreply_html.setText(self.tr('...'))
        self.tab.insertTab(self.tab_filtering,self.tr('Filtering'))

        self.tab_misc = QWidget(self.tab,'tab_misc')

        self.check_colorize = QCheckBox(self.tab_misc,'check_colorize')
        self.check_colorize.setGeometry(QRect(10,10,220,20))
        self.check_colorize.setText(self.tr('Use ANSI codes to colorize Animail output'))

        self.check_download_order = QCheckBox(self.tab_misc,'check_download_order')
        self.check_download_order.setGeometry(QRect(10,40,110,20))
        self.check_download_order.setText(self.tr('Download order:'))

        self.combo_download_order = QComboBox(0,self.tab_misc,'combo_download_order')
        self.combo_download_order.insertItem(self.tr('Smaller messages first'))
        self.combo_download_order.insertItem(self.tr('Bigger messages first'))
        self.combo_download_order.insertItem(self.tr('Server arrival oder'))
        self.combo_download_order.setEnabled(0)
        self.combo_download_order.setGeometry(QRect(120,40,170,22))
        self.tab.insertTab(self.tab_misc,self.tr('Misc'))

        self.connect(self.check_regular,SIGNAL('toggled(bool)'),self.frame_filters,SLOT('setEnabled(bool)'))
        self.connect(self.CheckBox1,SIGNAL('toggled(bool)'),self.label_port,SLOT('setEnabled(bool)'))
        self.connect(self.CheckBox1,SIGNAL('toggled(bool)'),self.spin_port,SLOT('setEnabled(bool)'))
        self.connect(self.check_resend,SIGNAL('toggled(bool)'),self.combo_resend,SLOT('setEnabled(bool)'))
        self.connect(self.check_resend,SIGNAL('toggled(bool)'),self.but_add_resend,SLOT('setEnabled(bool)'))
        self.connect(self.check_resend,SIGNAL('toggled(bool)'),self.but_remove_resend,SLOT('setEnabled(bool)'))
        self.connect(self.radio_mbox,SIGNAL('toggled(bool)'),self.label_mbox,SLOT('setEnabled(bool)'))
        self.connect(self.radio_mbox,SIGNAL('toggled(bool)'),self.edit_mbox,SLOT('setEnabled(bool)'))
        self.connect(self.radio_mbox,SIGNAL('toggled(bool)'),self.toolbut_mbox,SLOT('setEnabled(bool)'))
        self.connect(self.radio_maildir,SIGNAL('toggled(bool)'),self.label_maildir,SLOT('setEnabled(bool)'))
        self.connect(self.radio_maildir,SIGNAL('toggled(bool)'),self.edit_maildir,SLOT('setEnabled(bool)'))
        self.connect(self.radio_maildir,SIGNAL('toggled(bool)'),self.toolbut_maildir,SLOT('setEnabled(bool)'))
        self.connect(self.radio_pipe,SIGNAL('toggled(bool)'),self.label_pipe,SLOT('setEnabled(bool)'))
        self.connect(self.radio_pipe,SIGNAL('toggled(bool)'),self.edit_pipe,SLOT('setEnabled(bool)'))
        self.connect(self.check_download_order,SIGNAL('toggled(bool)'),self.combo_download_order,SLOT('setEnabled(bool)'))

        self.setTabOrder(self.but_undo,self.but_save)
        self.setTabOrder(self.but_save,self.tab)
        self.setTabOrder(self.tab,self.CheckBox1)
        self.setTabOrder(self.CheckBox1,self.list_servers)
        self.setTabOrder(self.list_servers,self.edit_address)
        self.setTabOrder(self.edit_address,self.edit_username)
        self.setTabOrder(self.edit_username,self.edit_passwd)
        self.setTabOrder(self.edit_passwd,self.spin_port)
        self.setTabOrder(self.spin_port,self.check_ssl)
        self.setTabOrder(self.check_ssl,self.check_keep)
        self.setTabOrder(self.check_keep,self.combo_protocol)
        self.setTabOrder(self.combo_protocol,self.combo_resend)
        self.setTabOrder(self.combo_resend,self.but_add_resend)
        self.setTabOrder(self.but_add_resend,self.but_remove_resend)
        self.setTabOrder(self.but_remove_resend,self.but_add_server)
        self.setTabOrder(self.but_add_server,self.but_remove_server)
        self.setTabOrder(self.but_remove_server,self.but_modify_server)
        self.setTabOrder(self.but_modify_server,self.edit_mbox)
        self.setTabOrder(self.edit_mbox,self.edit_maildir)
        self.setTabOrder(self.edit_maildir,self.edit_pipe)
        self.setTabOrder(self.edit_pipe,self.radio_smtp)
        self.setTabOrder(self.radio_smtp,self.radio_mbox)
        self.setTabOrder(self.radio_mbox,self.radio_maildir)
        self.setTabOrder(self.radio_maildir,self.radio_pipe)
        self.setTabOrder(self.radio_pipe,self.check_regular)
        self.setTabOrder(self.check_regular,self.list_filters)
        self.setTabOrder(self.list_filters,self.edit_filters)
        self.setTabOrder(self.edit_filters,self.but_add_filters)
        self.setTabOrder(self.but_add_filters,self.but_remove_filters)
        self.setTabOrder(self.but_remove_filters,self.but_change_filters)
        self.setTabOrder(self.but_change_filters,self.check_htmlfilter)
        self.setTabOrder(self.check_htmlfilter,self.check_maxnumber)
        self.setTabOrder(self.check_maxnumber,self.check_autoreply_filter)
        self.setTabOrder(self.check_autoreply_filter,self.check_autoreply_html)
        self.setTabOrder(self.check_autoreply_html,self.edit_autoreply_html)
        self.setTabOrder(self.edit_autoreply_html,self.check_maxsize)
        self.setTabOrder(self.check_maxsize,self.spin_maxsize)
        self.setTabOrder(self.spin_maxsize,self.spin_maxnumber)
        self.setTabOrder(self.spin_maxnumber,self.edit_autoreply_filter)
        self.setTabOrder(self.edit_autoreply_filter,self.check_colorize)
        self.setTabOrder(self.check_colorize,self.check_download_order)
        self.setTabOrder(self.check_download_order,self.combo_download_order)
        self.setTabOrder(self.combo_download_order,self.but_cancel)
