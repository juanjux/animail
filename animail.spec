%define name animail
%define version 2.0.6 
%define release 1 

Name: %{name} 
Summary: full featured mail downloader with interesting filtering capabilities
Version: %{version} 
Release: %{release} 
Source: http://www.escomposlinux.org/fer_y_juanjo/archivos/%{name}_%{version}.tar.bz2 
URL: http://animail.sourceforge.net
Group: Networking/Mail
BuildRoot: %{_tmppath}/%{name}-buildroot 
License: GPL
Requires: python 

%description
FIXME, To write.

%prep 
rm -rf $RPM_BUILD_ROOT 
%setup -a 1 
%patch -p1 

%build 
%make

%install 
%makeinstall

%clean 
rm -rf $RPM_BUILD_ROOT 

%files 
%defattr(-,root,root,0755) 
%doc README NEWS COPYING AUTHORS 
%{_mandir}/docs/animail.2.*
%{_bindir}/animail

%changelog 
* Mon Nov 02 1999 Camille Begnis <camille@mandrakesoft.com> 2.0.1-1mdk
- Upgraded to 2.0.1 

* Mon Oct 25 1999 Camille Begnis <camille@mandrakesoft.com> 2.0.0-1mdk
- Specfile adaptations for Mandrake
- add python requirement
- gz to bz2 compression
