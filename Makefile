MSGFMT = msgfmt

#Change this if you want Animail installed on other location:
DESTDIR=/usr
#PREFIX=usr/local/

SHLIB = /share/lib/animail
LOCALES = /share/locale
LIB = /lib/animail
DOC = /share/doc/animail
BIN = /bin
MAN = /share/man/man2


make:
install: 
	
	install -d $(DESTDIR)$(PREFIX)$(LOCALES)/ca/LC_MESSAGES
	install -d $(DESTDIR)$(PREFIX)$(LOCALES)/es/LC_MESSAGES	
	install -d $(DESTDIR)$(PREFIX)$(BIN)
	install -d $(DESTDIR)$(PREFIX)$(LIB)
	install -d $(DESTDIR)$(PREFIX)$(DOC)
	install -d $(DESTDIR)$(PREFIX)$(MAN)

	$(MSGFMT) po/es.po -o $(DESTDIR)$(PREFIX)$(LOCALES)/es/LC_MESSAGES/animail.mo
	$(MSGFMT) po/de.po -o $(DESTDIR)$(PREFIX)$(LOCALES)/de/LC_MESSAGES/animail.mo
	
	sh compile.sh
	cp src/*.py src/*.pyo $(DESTDIR)$(PREFIX)$(LIB)
	cp animail $(DESTDIR)$(PREFIX)$(BIN)
	chmod +x $(DESTDIR)$(PREFIX)$(BIN)/animail
	cp -R docs/* 	$(DESTDIR)$(PREFIX)$(DOC)
	cp docs/animail.2.gz $(DESTDIR)$(PREFIX)$(MAN)
	
uninstall:
	rm -f		$(DESTDIR)$(PREFIX)$(BIN)/animail
	rm -rf		$(DESTDIR)$(PREFIX)$(LIB)
	rm -rf 		$(DESTDIR)$(PREFIX)$(SHLIB)
	rm -rf 		$(DESTDIR)$(PREFIX)$(DOC)
clean:
	rm src/*.pyc src/*.pyo

deb: 
	dpkg-buildpackage -rfakeroot
  
