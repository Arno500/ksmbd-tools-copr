#
# spec file for package ksmbd-dkms
#
%global forgeurl https://github.com/cifsd-team/ksmbd
%global commit  bf249dcef4d5a20eabf9656154419a0042769b90
%forgemeta

%define module  ksmbd

Name:           ksmbd-dkms
Version:        20230721
Release:        1%{?dist}
Summary:        Kernel module(s) (dkms)

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
%setup -q -n %{module}-%{commit}

%install
if [ "$RPM_BUILD_ROOT" != "/" ]; then
    rm -rf $RPM_BUILD_ROOT
fi
mkdir -p $RPM_BUILD_ROOT/usr/src/%{module}-%{version}
cp -rf ${RPM_BUILD_DIR}/%{module}-%{commit}/* $RPM_BUILD_ROOT/usr/src/%{module}-%{version}

%clean
if [ "$RPM_BUILD_ROOT" != "/" ]; then
    rm -rf $RPM_BUILD_ROOT
fi

%files
%defattr(-,root,root)
/usr/src/%{module}-%{version}

%preun
dkms remove -m %{module} -v %{version} --all

%posttrans
/usr/lib/dkms/common.postinst %{module} %{version}

%changelog
* Sun Sep 03 2023 Nicholas Kudriavtsev <nkudriavtsev@gmail.com>
- Release 3.4.8
