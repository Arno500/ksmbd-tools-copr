#
# spec file for package ksmbd-dkms
#
%global forgeurl https://github.com/namjaejeon/ksmbd

%define module  ksmbd

Name:           ksmbd-dkms
Version:        3.5.4
Release:        1%{?dist}
Summary:        Kernel module(s) (dkms)

%global branch master
%forgemeta

License:        GPL-2.0-or-later
URL:            %{forgeurl}
Source0:        %{forgesource}
BuildArch:      noarch

Requires:       dkms >= 2.2.0.3
Requires(post): dkms >= 2.2.0.3
Requires(preun): dkms >= 2.2.0.3
Requires:       gcc, make, diffutils
Requires(post): gcc, make, diffutils
Requires:       kernel-devel >= 6.3
Requires(post): kernel-devel >= 6.3
Provides:       %{module}-dkms = %{version}
AutoReqProv:    no

%description
This package contains the dkms ksmbd kernel module.

%prep
%setup -q -n %{module}-master

%install
if [ "$RPM_BUILD_ROOT" != "/" ]; then
    rm -rf $RPM_BUILD_ROOT
fi
mkdir -p $RPM_BUILD_ROOT/usr/src/%{module}-%{version}-%{release}
cp -rf ${RPM_BUILD_DIR}/%{module}-master/. $RPM_BUILD_ROOT/usr/src/%{module}-%{version}-%{release}

%clean
if [ "$RPM_BUILD_ROOT" != "/" ]; then
    rm -rf $RPM_BUILD_ROOT
fi

%files
%defattr(-,root,root)
/usr/src/%{module}-%{version}-%{release}

%preun
dkms remove -m %{module} -v %{version}-%{release} --all --rpm_safe_upgrade

%post
dkms add -m %{module} -v %{version}-%{release} --rpm_safe_upgrade
dkms install --force -m %{module} -v %{version}-%{release} --rpm_safe_upgrade

%changelog
* Fri January 16 2026 Arno Dubois <arno.du@orange.fr>
- Release 3.5.4-1
* Fri August 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.2-1
* Fri August 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-12
* Fri August 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-11
* Fri August 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-10
* Fri August 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-9
* Fri August 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-8
* Sun June 26 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-7
* Sun June 1 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-6
* Wed May 15 2024 Nicholas Kudriavtsev <nkudriavtsev@gmail.com>
- Release 3.5.0
* Mon Feb 05 2024 Nicholas Kudriavtsev <nkudriavtsev@gmail.com>
- Release 3.4.9
* Sun Sep 03 2023 Nicholas Kudriavtsev <nkudriavtsev@gmail.com>
- Release 20230721
