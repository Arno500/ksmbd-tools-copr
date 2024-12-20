#
# spec file for package ksmbd-dkms
#
%global forgeurl https://github.com/cifsd-team/ksmbd

%define module  ksmbd

Name:           ksmbd-dkms
Version:        3.5.0
Release:        5%{?dist}
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
%setup -q -n %{module}-%{version}

%install
if [ "$RPM_BUILD_ROOT" != "/" ]; then
    rm -rf $RPM_BUILD_ROOT
fi
mkdir -p $RPM_BUILD_ROOT/usr/src/%{module}-%{version}
cp -rf ${RPM_BUILD_DIR}/%{module}-%{version} $RPM_BUILD_ROOT/usr/src/

%clean
if [ "$RPM_BUILD_ROOT" != "/" ]; then
    rm -rf $RPM_BUILD_ROOT
fi

%files
%defattr(-,root,root)
/usr/src/%{module}-%{version}

%preun
dkms remove -m %{module} -v %{version} --all --rpm_safe_upgrade

%post
dkms add -m %{module} -v %{version} --rpm_safe_upgrade
dkms install --force -m %{module} -v %{version} --rpm_safe_upgrade

%changelog
* Wed May 15 2024 Nicholas Kudriavtsev <nkudriavtsev@gmail.com>
- Release 3.5.0
* Mon Feb 05 2024 Nicholas Kudriavtsev <nkudriavtsev@gmail.com>
- Release 3.4.9
* Sun Sep 03 2023 Nicholas Kudriavtsev <nkudriavtsev@gmail.com>
- Release 20230721
