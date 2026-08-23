#
# spec file for package ksmbd-dkms
#
# This is now an empty transitional package. ksmbd is no longer packaged
# with DKMS: it has been replaced by akmod-ksmbd (built from the exact
# matching Fedora kernel source via koji, instead of a vendored copy of an
# out-of-tree repository), with kmod-ksmbd pulling it in automatically.
# See ksmbd-kmod.spec.
#
# Keeping this package under its old name (rather than using Obsoletes/
# Provides) means a plain "dnf upgrade" on an existing ksmbd-dkms install
# picks this up as a normal same-name version bump and pulls in kmod-ksmbd
# with it. This package can be safely removed afterwards.
#

Name:           ksmbd-dkms
Version:        3.6.0
Release:        1%{?dist}
Summary:        Transitional package -- ksmbd is now packaged as kmod-ksmbd
License:        GPL-2.0-only
URL:            https://cdn.kernel.org
BuildArch:      noarch

Requires:       kmod-ksmbd

%description
Empty transitional package. ksmbd-dkms has been replaced by kmod-ksmbd
(which pulls in akmod-ksmbd), built directly from the matching Fedora
kernel source instead of a vendored out-of-tree DKMS copy. Installing
this package just pulls in kmod-ksmbd; it can be safely removed
afterwards.

%prep
%build
%install

%files

%changelog
* Sun Aug 23 2026 Arno Dubois <arno.du@orange.fr>
- Release 3.6.0-1
- Turn into an empty transitional package requiring kmod-ksmbd, so
  existing ksmbd-dkms installs pick up the akmod-based replacement via a
  plain "dnf upgrade" instead of being left on an abandoned package.
* Fri Jan 16 2026 Arno Dubois <arno.du@orange.fr>
- Release 3.5.4-1
* Fri Aug 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.2-1
* Fri Aug 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-12
* Fri Aug 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-11
* Fri Aug 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-10
* Fri Aug 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-9
* Fri Aug 29 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-8
* Sun Jun 26 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-7
* Sun Jun 1 2025 Arno Dubois <arno.du@orange.fr>
- Release 3.5.0-6
* Wed May 15 2024 Nicholas Kudriavtsev <nkudriavtsev@gmail.com>
- Release 3.5.0
* Mon Feb 05 2024 Nicholas Kudriavtsev <nkudriavtsev@gmail.com>
- Release 3.4.9
* Sun Sep 03 2023 Nicholas Kudriavtsev <nkudriavtsev@gmail.com>
- Release 20230721
