Name:    maxscale
Version: 21.06.17
Release: 6%{?dist}

Summary: Database proxy for MariaDB Server
License: (AFL-2.1 OR BSD-3-Clause) AND (BSD-3-Clause OR GPL-2.0-only) AND (MIT OR Apache-2.0) AND (MIT OR CC0-1.0) AND (WTFPL OR MIT) AND 0BSD AND Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND CC-BY-3.0 AND CC-BY-4.0 AND CC0-1.0 AND GPL-2.0-or-later AND ISC AND LGPL-2.1-only AND MIT AND MPL-2.0 AND PSF-2.0 AND Unlicense AND Zlib AND blessing
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

# Requires for the systemd service
%{?systemd_requires}

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

%post
%systemd_post maxscale.service
%preun
%systemd_preun maxscale.service
%postun
%systemd_postun_with_restart maxscale.service

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
%license %{_datadir}/maxscale/LICENSE.TXT
%license %{_datadir}/maxscale/LICENSE-THIRDPARTY.TXT
%license %{_datadir}/maxscale/COPYRIGHT


%changelog
%autochangelog
