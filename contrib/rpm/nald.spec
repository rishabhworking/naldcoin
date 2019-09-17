%define bdbv 4.8.30
%global selinux_variants mls strict targeted

%if 0%{?_no_gui:1}
%define _buildqt 0
%define buildargs --with-gui=no
%else
%define _buildqt 1
%if 0%{?_use_qt4}
%define buildargs --with-qrencode --with-gui=qt4
%else
%define buildargs --with-qrencode --with-gui=qt5
%endif
%endif

Name:		nald
Version:	0.12.0
Release:	2%{?dist}
Summary:	Peer to Peer Cryptographic Currency

Group:		Applications/System
License:	MIT
URL:		https://nald.org/
Source0:	https://nald.org/bin/nald-core-%{version}/nald-%{version}.tar.gz
Source1:	http://download.oracle.com/berkeley-db/db-%{bdbv}.NC.tar.gz

Source10:	https://raw.githubusercontent.com/nald/nald/v%{version}/contrib/debian/examples/nald.conf

#man pages
Source20:	https://raw.githubusercontent.com/nald/nald/v%{version}/doc/man/naldd.1
Source21:	https://raw.githubusercontent.com/nald/nald/v%{version}/doc/man/nald-cli.1
Source22:	https://raw.githubusercontent.com/nald/nald/v%{version}/doc/man/nald-qt.1

#selinux
Source30:	https://raw.githubusercontent.com/nald/nald/v%{version}/contrib/rpm/nald.te
# Source31 - what about nald-tx and bench_nald ???
Source31:	https://raw.githubusercontent.com/nald/nald/v%{version}/contrib/rpm/nald.fc
Source32:	https://raw.githubusercontent.com/nald/nald/v%{version}/contrib/rpm/nald.if

Source100:	https://upload.wikimedia.org/wikipedia/commons/4/46/Naldcoin.svg

%if 0%{?_use_libressl:1}
BuildRequires:	libressl-devel
%else
BuildRequires:	openssl-devel
%endif
BuildRequires:	boost-devel
BuildRequires:	miniupnpc-devel
BuildRequires:	autoconf automake libtool
BuildRequires:	libevent-devel


Patch0:		nald-0.12.0-libressl.patch


%description
Naldcoin is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of nalds is carried out collectively by the network.

%if %{_buildqt}
%package core
Summary:	Peer to Peer Cryptographic Currency
Group:		Applications/System
Obsoletes:	%{name} < %{version}-%{release}
Provides:	%{name} = %{version}-%{release}
%if 0%{?_use_qt4}
BuildRequires:	qt-devel
%else
BuildRequires:	qt5-qtbase-devel
# for /usr/bin/lrelease-qt5
BuildRequires:	qt5-linguist
%endif
BuildRequires:	protobuf-devel
BuildRequires:	qrencode-devel
BuildRequires:	%{_bindir}/desktop-file-validate
# for icon generation from SVG
BuildRequires:	%{_bindir}/inkscape
BuildRequires:	%{_bindir}/convert

%description core
Naldcoin is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of nalds is carried out collectively by the network.

This package contains the Qt based graphical client and node. If you are looking
to run a Naldcoin wallet, this is probably the package you want.
%endif


%package libs
Summary:	Naldcoin shared libraries
Group:		System Environment/Libraries

%description libs
This package provides the naldconsensus shared libraries. These libraries
may be used by third party software to provide consensus verification
functionality.

Unless you know need this package, you probably do not.

%package devel
Summary:	Development files for nald
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
This package contains the header files and static library for the
naldconsensus shared library. If you are developing or compiling software
that wants to link against that library, then you need this package installed.

Most people do not need this package installed.

%package server
Summary:	The nald daemon
Group:		System Environment/Daemons
Requires:	nald-utils = %{version}-%{release}
Requires:	selinux-policy policycoreutils-python
Requires(pre):	shadow-utils
Requires(post):	%{_sbindir}/semodule %{_sbindir}/restorecon %{_sbindir}/fixfiles %{_sbindir}/sestatus
Requires(postun):	%{_sbindir}/semodule %{_sbindir}/restorecon %{_sbindir}/fixfiles %{_sbindir}/sestatus
BuildRequires:	systemd
BuildRequires:	checkpolicy
BuildRequires:	%{_datadir}/selinux/devel/Makefile

%description server
This package provides a stand-alone nald-core daemon. For most users, this
package is only needed if they need a full-node without the graphical client.

Some third party wallet software will want this package to provide the actual
nald-core node they use to connect to the network.

If you use the graphical nald-core client then you almost certainly do not
need this package.

%package utils
Summary:	Naldcoin utilities
Group:		Applications/System

%description utils
This package provides several command line utilities for interacting with a
nald-core daemon.

The nald-cli utility allows you to communicate and control a nald daemon
over RPC, the nald-tx utility allows you to create a custom transaction, and
the bench_nald utility can be used to perform some benchmarks.

This package contains utilities needed by the nald-server package.


%prep
%setup -q
%patch0 -p1 -b .libressl
cp -p %{SOURCE10} ./nald.conf.example
tar -zxf %{SOURCE1}
cp -p db-%{bdbv}.NC/LICENSE ./db-%{bdbv}.NC-LICENSE
mkdir db4 SELinux
cp -p %{SOURCE30} %{SOURCE31} %{SOURCE32} SELinux/


%build
CWD=`pwd`
cd db-%{bdbv}.NC/build_unix/
../dist/configure --enable-cxx --disable-shared --with-pic --prefix=${CWD}/db4
make install
cd ../..

./autogen.sh
%configure LDFLAGS="-L${CWD}/db4/lib/" CPPFLAGS="-I${CWD}/db4/include/" --with-miniupnpc --enable-glibc-back-compat %{buildargs}
make %{?_smp_mflags}

pushd SELinux
for selinuxvariant in %{selinux_variants}; do
	make NAME=${selinuxvariant} -f %{_datadir}/selinux/devel/Makefile
	mv nald.pp nald.pp.${selinuxvariant}
	make NAME=${selinuxvariant} -f %{_datadir}/selinux/devel/Makefile clean
done
popd


%install
make install DESTDIR=%{buildroot}

mkdir -p -m755 %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/naldd %{buildroot}%{_sbindir}/naldd

# systemd stuff
mkdir -p %{buildroot}%{_tmpfilesdir}
cat <<EOF > %{buildroot}%{_tmpfilesdir}/nald.conf
d /run/naldd 0750 nald nald -
EOF
touch -a -m -t 201504280000 %{buildroot}%{_tmpfilesdir}/nald.conf

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cat <<EOF > %{buildroot}%{_sysconfdir}/sysconfig/nald
# Provide options to the nald daemon here, for example
# OPTIONS="-testnet -disable-wallet"

OPTIONS=""

# System service defaults.
# Don't change these unless you know what you're doing.
CONFIG_FILE="%{_sysconfdir}/nald/nald.conf"
DATA_DIR="%{_localstatedir}/lib/nald"
PID_FILE="/run/naldd/naldd.pid"
EOF
touch -a -m -t 201504280000 %{buildroot}%{_sysconfdir}/sysconfig/nald

mkdir -p %{buildroot}%{_unitdir}
cat <<EOF > %{buildroot}%{_unitdir}/nald.service
[Unit]
Description=Naldcoin daemon
After=syslog.target network.target

[Service]
Type=forking
ExecStart=%{_sbindir}/naldd -daemon -conf=\${CONFIG_FILE} -datadir=\${DATA_DIR} -pid=\${PID_FILE} \$OPTIONS
EnvironmentFile=%{_sysconfdir}/sysconfig/nald
User=nald
Group=nald

Restart=on-failure
PrivateTmp=true
TimeoutStopSec=120
TimeoutStartSec=60
StartLimitInterval=240
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
EOF
touch -a -m -t 201504280000 %{buildroot}%{_unitdir}/nald.service
#end systemd stuff

mkdir %{buildroot}%{_sysconfdir}/nald
mkdir -p %{buildroot}%{_localstatedir}/lib/nald

#SELinux
for selinuxvariant in %{selinux_variants}; do
	install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
	install -p -m 644 SELinux/nald.pp.${selinuxvariant} %{buildroot}%{_datadir}/selinux/${selinuxvariant}/nald.pp
done

%if %{_buildqt}
# qt icons
install -D -p share/pixmaps/nald.ico %{buildroot}%{_datadir}/pixmaps/nald.ico
install -p share/pixmaps/nsis-header.bmp %{buildroot}%{_datadir}/pixmaps/
install -p share/pixmaps/nsis-wizard.bmp %{buildroot}%{_datadir}/pixmaps/
install -p %{SOURCE100} %{buildroot}%{_datadir}/pixmaps/nald.svg
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/nald16.png -w16 -h16
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/nald32.png -w32 -h32
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/nald64.png -w64 -h64
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/nald128.png -w128 -h128
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/nald256.png -w256 -h256
%{_bindir}/convert -resize 16x16 %{buildroot}%{_datadir}/pixmaps/nald256.png %{buildroot}%{_datadir}/pixmaps/nald16.xpm
%{_bindir}/convert -resize 32x32 %{buildroot}%{_datadir}/pixmaps/nald256.png %{buildroot}%{_datadir}/pixmaps/nald32.xpm
%{_bindir}/convert -resize 64x64 %{buildroot}%{_datadir}/pixmaps/nald256.png %{buildroot}%{_datadir}/pixmaps/nald64.xpm
%{_bindir}/convert -resize 128x128 %{buildroot}%{_datadir}/pixmaps/nald256.png %{buildroot}%{_datadir}/pixmaps/nald128.xpm
%{_bindir}/convert %{buildroot}%{_datadir}/pixmaps/nald256.png %{buildroot}%{_datadir}/pixmaps/nald256.xpm
touch %{buildroot}%{_datadir}/pixmaps/*.png -r %{SOURCE100}
touch %{buildroot}%{_datadir}/pixmaps/*.xpm -r %{SOURCE100}

# Desktop File - change the touch timestamp if modifying
mkdir -p %{buildroot}%{_datadir}/applications
cat <<EOF > %{buildroot}%{_datadir}/applications/nald-core.desktop
[Desktop Entry]
Encoding=UTF-8
Name=Naldcoin
Comment=Naldcoin P2P Cryptocurrency
Comment[fr]=Naldcoin, monnaie virtuelle cryptographique pair à pair
Comment[tr]=Naldcoin, eşten eşe kriptografik sanal para birimi
Exec=nald-qt %u
Terminal=false
Type=Application
Icon=nald128
MimeType=x-scheme-handler/nald;
Categories=Office;Finance;
EOF
# change touch date when modifying desktop
touch -a -m -t 201511100546 %{buildroot}%{_datadir}/applications/nald-core.desktop
%{_bindir}/desktop-file-validate %{buildroot}%{_datadir}/applications/nald-core.desktop

# KDE protocol - change the touch timestamp if modifying
mkdir -p %{buildroot}%{_datadir}/kde4/services
cat <<EOF > %{buildroot}%{_datadir}/kde4/services/nald-core.protocol
[Protocol]
exec=nald-qt '%u'
protocol=nald
input=none
output=none
helper=true
listing=
reading=false
writing=false
makedir=false
deleting=false
EOF
# change touch date when modifying protocol
touch -a -m -t 201511100546 %{buildroot}%{_datadir}/kde4/services/nald-core.protocol
%endif

# man pages
install -D -p %{SOURCE20} %{buildroot}%{_mandir}/man1/naldd.1
install -p %{SOURCE21} %{buildroot}%{_mandir}/man1/nald-cli.1
%if %{_buildqt}
install -p %{SOURCE22} %{buildroot}%{_mandir}/man1/nald-qt.1
%endif

# nuke these, we do extensive testing of binaries in %%check before packaging
rm -f %{buildroot}%{_bindir}/test_*

%check
make check
srcdir=src test/nald-util-test.py
test/functional/test_runner.py --extended

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%pre server
getent group nald >/dev/null || groupadd -r nald
getent passwd nald >/dev/null ||
	useradd -r -g nald -d /var/lib/nald -s /sbin/nologin \
	-c "Naldcoin wallet server" nald
exit 0

%post server
%systemd_post nald.service
# SELinux
if [ `%{_sbindir}/sestatus |grep -c "disabled"` -eq 0 ]; then
for selinuxvariant in %{selinux_variants}; do
	%{_sbindir}/semodule -s ${selinuxvariant} -i %{_datadir}/selinux/${selinuxvariant}/nald.pp &> /dev/null || :
done
%{_sbindir}/semanage port -a -t nald_port_t -p tcp 8501
%{_sbindir}/semanage port -a -t nald_port_t -p tcp 7342
%{_sbindir}/semanage port -a -t nald_port_t -p tcp 18501
%{_sbindir}/semanage port -a -t nald_port_t -p tcp 17342
%{_sbindir}/semanage port -a -t nald_port_t -p tcp 18443
%{_sbindir}/semanage port -a -t nald_port_t -p tcp 18444
%{_sbindir}/fixfiles -R nald-server restore &> /dev/null || :
%{_sbindir}/restorecon -R %{_localstatedir}/lib/nald || :
fi

%posttrans server
%{_bindir}/systemd-tmpfiles --create

%preun server
%systemd_preun nald.service

%postun server
%systemd_postun nald.service
# SELinux
if [ $1 -eq 0 ]; then
	if [ `%{_sbindir}/sestatus |grep -c "disabled"` -eq 0 ]; then
	%{_sbindir}/semanage port -d -p tcp 8501
	%{_sbindir}/semanage port -d -p tcp 7342
	%{_sbindir}/semanage port -d -p tcp 18501
	%{_sbindir}/semanage port -d -p tcp 17342
	%{_sbindir}/semanage port -d -p tcp 18443
	%{_sbindir}/semanage port -d -p tcp 18444
	for selinuxvariant in %{selinux_variants}; do
		%{_sbindir}/semodule -s ${selinuxvariant} -r nald &> /dev/null || :
	done
	%{_sbindir}/fixfiles -R nald-server restore &> /dev/null || :
	[ -d %{_localstatedir}/lib/nald ] && \
		%{_sbindir}/restorecon -R %{_localstatedir}/lib/nald &> /dev/null || :
	fi
fi

%clean
rm -rf %{buildroot}

%if %{_buildqt}
%files core
%defattr(-,root,root,-)
%license COPYING db-%{bdbv}.NC-LICENSE
%doc COPYING nald.conf.example doc/README.md doc/bips.md doc/files.md doc/multiwallet-qt.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_bindir}/nald-qt
%attr(0644,root,root) %{_datadir}/applications/nald-core.desktop
%attr(0644,root,root) %{_datadir}/kde4/services/nald-core.protocol
%attr(0644,root,root) %{_datadir}/pixmaps/*.ico
%attr(0644,root,root) %{_datadir}/pixmaps/*.bmp
%attr(0644,root,root) %{_datadir}/pixmaps/*.svg
%attr(0644,root,root) %{_datadir}/pixmaps/*.png
%attr(0644,root,root) %{_datadir}/pixmaps/*.xpm
%attr(0644,root,root) %{_mandir}/man1/nald-qt.1*
%endif

%files libs
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/shared-libraries.md
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/developer-notes.md doc/shared-libraries.md
%attr(0644,root,root) %{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%attr(0644,root,root) %{_libdir}/pkgconfig/*.pc

%files server
%defattr(-,root,root,-)
%license COPYING db-%{bdbv}.NC-LICENSE
%doc COPYING nald.conf.example doc/README.md doc/REST-interface.md doc/bips.md doc/dnsseed-policy.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_sbindir}/naldd
%attr(0644,root,root) %{_tmpfilesdir}/nald.conf
%attr(0644,root,root) %{_unitdir}/nald.service
%dir %attr(0750,nald,nald) %{_sysconfdir}/nald
%dir %attr(0750,nald,nald) %{_localstatedir}/lib/nald
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/sysconfig/nald
%attr(0644,root,root) %{_datadir}/selinux/*/*.pp
%attr(0644,root,root) %{_mandir}/man1/naldd.1*

%files utils
%defattr(-,root,root,-)
%license COPYING
%doc COPYING nald.conf.example doc/README.md
%attr(0755,root,root) %{_bindir}/nald-cli
%attr(0755,root,root) %{_bindir}/nald-tx
%attr(0755,root,root) %{_bindir}/bench_nald
%attr(0644,root,root) %{_mandir}/man1/nald-cli.1*



%changelog
* Fri Feb 26 2016 Alice Wonder <buildmaster@librelamp.com> - 0.12.0-2
- Rename Qt package from nald to nald-core
- Make building of the Qt package optional
- When building the Qt package, default to Qt5 but allow building
-  against Qt4
- Only run SELinux stuff in post scripts if it is not set to disabled

* Wed Feb 24 2016 Alice Wonder <buildmaster@librelamp.com> - 0.12.0-1
- Initial spec file for 0.12.0 release

# This spec file is written from scratch but a lot of the packaging decisions are directly
# based upon the 0.11.2 package spec file from https://www.ringingliberty.com/nald/
