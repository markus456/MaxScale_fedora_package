Name:    maxscale
Version: 21.06.17
Release: 2%{?dist}

Summary: Database proxy for MariaDB Server
License: GPLv2+
URL:     https://www.mariadb.com

Source:  https://mdbe-ci-repo.mariadb.net/public/Maxscale/21.06-markusjm-src/sourcetar/maxscale-%{version}-Source.tar.gz

Patch0:  rpath.patch

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

# For dbfwfilter (21.06 only)
BuildRequires: bison flex

# MaxCtrl also needs Node.js at runtime
Requires: nodejs


%description
Database proxy that extends the high availability, scalability, and security
of MariaDB Server while at the same time simplifying application development
by decoupling it from underlying database infrastructure.


%prep
%setup -n maxscale-%{version}-Source

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
%cmake -DBUNDLE=N -DBUILD_TOOLS=N -DBUILD_CDC=N -DBUILD_MAXCTRL=N

%cmake_build


%install
%cmake_install

# Fedora use systemd, no need for init script
rm %{buildroot}%{_sysconfdir}/init/maxscale.conf
rm %{buildroot}%{_sysconfdir}/init.d/maxscale

%check
%ctest


%files
%{_bindir}/{maxscale,maxctrl,maxkeys,maxpasswd,maxscale_generate_support_info.py}
%{_mandir}/man1/maxscale.1.gz

# Part of dbfwfilter (21.06 only)
%{_bindir}/dbfwchk

%{_unitdir}/maxscale.service

%{_sysconfdir}/maxscale.cnf.template

%{_sysconfdir}/ld.so.conf.d/maxscale.conf
%{_sysconfdir}/logrotate.d/maxscale_logrotate
%{_sysconfdir}/prelink.conf.d/maxscale.conf

%{_libdir}/maxscale
%{_datadir}/maxscale


%changelog
* Sat Aug 24 2024 Michal Schorm <mschorm@redhat.com> - 21.06.17-2
- FTBFS fixes

* Fri Aug 23 2024 Markus Mäkelä <markus.makela@mariadb.com>
- Initial version
