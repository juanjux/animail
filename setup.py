#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup
setup(name="animail",
         version="2.0_pre19",
         license="GPL"
         description="Mail transfer Agent with featuritis",
         author="Juanjo Álvarez",
         author_email="juanjux@yahoo.es",
         url="http://animail.sourceforge.net"
         package_dir= {'': 'src'},
         packages = ['animail'],
#       data_files = DOC_FILES #y los .po...
         scripts=['animail'],
         long_description=""
         )

      
"""      py_modules=["AnimailMain", "configlib", "configwin", 
                  "general", "imap", "imapslib", "logger",
                  "mailserver", "pop3", "popslib", "postfilter",
                  "qtif", "qtif", "smtp", "update_config"])
"""                  

# Queda: 
# 1. Que instale la documentación (install_data)
# 2. Que instale los ficheros 'po' en el lugar adecuado (install_data y
#    cambiando probáblemente el código; también tiene que compilar los .po a 
#    .mo en el caso de los paquetes binarios).
