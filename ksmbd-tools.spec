#
# spec file for package ksmbd-tools
#
# Copyright (c) 2021 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.
#
# Please submit bugfixes or comments via https://bugs.opensuse.org/
#

Name:           ksmbd-tools
Version:        3.5.7
Release:        1%{?dist}
Summary:        ksmbd kernel server userspace utilities
License:        GPL-2.0-or-later
Group:          System/Filesystems
Url:            https://github.com/cifsd-team/ksmbd-tools
Source:         %{url}/archive/%{version}/%{name}-%{version}.tar.gz
Patch0:         ksmbd-tools-service-retry.patch

BuildRequires:  glib2-devel
BuildRequires:  libnl3-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  systemd-rpm-macros

Requires(pre):	kernel >= 5.15
Requires(pre):	systemd >= 245

%description
Collection of userspace utilities for the ksmbd kernel server.

%prep
%setup -q
%patch0 -p1

%build
./autogen.sh
%configure --with-systemdsystemunitdir=%{_unitdir}
make %{?_smp_mflags}

%install
%make_install

%files
%{_sbindir}/ksmbd.addshare
%{_sbindir}/ksmbd.adduser
%{_sbindir}/ksmbd.control
%{_sbindir}/ksmbd.mountd
%{_libexecdir}/ksmbd.tools
%{_mandir}/man8/ksmbd.addshare.8*
%{_mandir}/man8/ksmbd.adduser.8*
%{_mandir}/man8/ksmbd.control.8*
%{_mandir}/man8/ksmbd.mountd.8*
%{_mandir}/man5/ksmbd.conf.5*
%{_mandir}/man5/ksmbdpwd.db.5*
%{_sysconfdir}/ksmbd/ksmbd.conf.example
%{_unitdir}/ksmbd.service

%changelog
* Sun August 23 2026 Arno Dubois <arno.du@orange.fr>
- Release 3.5.7-1
- Bump to upstream 3.5.7.
- Patch ksmbd.service to retry on failure (Restart=on-failure,
  RestartSec=15, StartLimitIntervalSec=0 to disable rate-limiting). The
  unit Requires=modprobe@ksmbd.service, so if the ksmbd kernel module
  isn't built yet at boot (e.g. akmod-ksmbd is still compiling it in the
  background), ksmbd.service used to fail once and stay down; now it
  keeps retrying, and each retry re-attempts modprobe@ksmbd.service too,
  so it self-heals once the module becomes available instead of requiring
  a manual restart.
