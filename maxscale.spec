Name:    maxscale
Version: 21.06.17
Release: 5%{?dist}

Summary: Database proxy for MariaDB Server
License: GPLv2+
URL:     https://www.mariadb.com

Source:  https://dlm.mariadb.com/MaxScale/%{version}/sourcetar/maxscale-%{version}-Source.tar.gz
Patch0:  remove-dbfwfilter.patch

# Core MaxScale dependencies
BuildRequires: cmake gcc-c++

BuildRequires: boost-devel
BuildRequires: jansson-devel
BuildRequires: krb5-devel
BuildRequires: libatomic
BuildRequires: libcurl-devel
BuildRequires: libgcrypt-devel
BuildRequires: libmicrohttpd-devel
BuildRequires: librdkafka-devel
BuildRequires: libuuid-devel
BuildRequires: libxml2-devel
BuildRequires: openssl-devel
BuildRequires: pam-devel
BuildRequires: pcre2-devel
BuildRequires: sqlite-devel
BuildRequires: systemd-devel
BuildRequires: tcl-devel

# GUI and MaxCtrl
BuildRequires: nodejs npm

# MaxCtrl also needs Node.js at runtime
Requires: nodejs

# MaxScale installs a logrotate config file and thus needs a dependency on logrotate, otherwise rpmlint will
# warn about the lack of it.
Requires: logrotate

%description
Database proxy that extends the high availability, scalability, and security
of MariaDB Server while at the same time simplifying application development
by decoupling it from underlying database infrastructure.


%prep
%setup -q -n maxscale-%{version}-Source

%patch -P0 -p1

%build
# mariadb-connector-c and test_mxb_string cause warnings to be emitted during link-time optimization. The 3.2
# series of the connector-c doesn't have a release with these problems fixed and the one in test_mxb_string
# seems like a potential false positive
CFLAGS="-Wno-lto-type-mismatch -Wno-stringop-overread $CFLAGS"
CXXFLAGS="-Wno-lto-type-mismatch -Wno-stringop-overread $CXXFLAGS"
export CFLAGS CXXFLAGS

# The -DBUILD_CDC=N disables the CDC protocol and the avrorouter module, the latter of which requires
# libraries that aren't available in the system repositories. The CDC protocol itself is useless without it so
# it's better to disable them both.
%cmake -DBUNDLE=N -DBUILD_TOOLS=N -DBUILD_CDC=N

%cmake_build


%install
%cmake_install

# Fedora use systemd, no need for init script
rm %{buildroot}%{_sysconfdir}/init/maxscale.conf
rm %{buildroot}%{_sysconfdir}/init.d/maxscale

# Create a directory for the logrotate log
mkdir -p %{buildroot}%{_localstatedir}/log/maxscale

# Rename the logrotate file to comply with rpmlint expectations.
mv %{buildroot}%{_sysconfdir}/logrotate.d/maxscale_logrotate %{buildroot}%{_sysconfdir}/logrotate.d/maxscale

# The support report generation script is not necessary and if it was, it would need Python3 as a
# dependency. Since maxctrl is capable of generating reports with 'maxctrl create report', the script isn't
# absolutely necessary.
rm -f %{buildroot}%{_bindir}/maxscale_generate_support_info.py

# The prelink script is also not needed as MaxCtrl uses the system nodejs but
# MaxScale 21.06.17 still has it. In MaxScale 21.06.18 this file no longer
# exists.
rm -f %{buildroot}%{_sysconfdir}/prelink.conf.d/maxscale.conf

# https://jira.mariadb.org/browse/MXS-5264
# The maxctrl file gets installed with the wrong 0555 permissions instead of the
# normal 0755 permissions.
chmod 0755 %{buildroot}%{_bindir}/maxctrl

%check
%ctest


%files
%{_bindir}/{maxscale,maxctrl,maxkeys,maxpasswd}
%{_mandir}/man1/maxscale.1.gz
%{_mandir}/man1/maxctrl.1.gz
%{_mandir}/man1/maxkeys.1.gz
%{_mandir}/man1/maxpasswd.1.gz

%{_unitdir}/maxscale.service

%config(noreplace) %{_sysconfdir}/maxscale.cnf.template

%{_sysconfdir}/ld.so.conf.d/maxscale.conf

%config(noreplace) %{_sysconfdir}/logrotate.d/maxscale
%{_localstatedir}/log/maxscale

%{_libdir}/maxscale
%{_datadir}/maxscale


%changelog
* Sat Sep 14 2024  Markus Mäkelä <markus.makela@mariadb.com> - 21.06.17-5
- Update sources to the official 21.06.17 release
- Removed -DBUILD_MAXCTRL=N as it should be built now
- Removed the prelink config file, it's no longer needed for maxctrl
- Added installation of missing manual pages
- Removed dbfwfilter from the builds as it is deprecated in MaxScale 21.06 and is removed in MaxScale 22.08

* Wed Aug 28 2024  Markus Mäkelä <markus.makela@mariadb.com> - 21.06.17-4
- Update sources and remove the patch
- Added the missing dependency on logrotate and renamed the config files to comply with the expected format
- Removed the installation of maxscale_generate_support_info.py as it would require Python 3
- Bumped release

* Sun Aug 25 2024 Michal Schorm <mschorm@redhat.com> - 21.06.17-3
- Bump release for rebuild

* Sat Aug 24 2024 Michal Schorm <mschorm@redhat.com> - 21.06.17-2
- FTBFS fixes

* Fri Aug 23 2024 Markus Mäkelä <markus.makela@mariadb.com>
- Initial version
