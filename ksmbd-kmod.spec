# based on the RPM Fusion Kmods2 template
# (https://rpmfusion.org/Packaging/KernelModules/Kmods2), adapted the way
# https://github.com/ferdiu/akmod-e1000e-no-nvm-check does: since ksmbd
# (fs/smb/server) isn't shipped/built by Fedora at all, its source is fetched
# from Fedora's own kernel source (via koji) matching the exact kernel it is
# being built against, instead of vendoring a fixed copy of an out-of-tree
# repository.

# (un)define the next line to either build for the newest or all current kernels
#define buildforkernels newest
#define buildforkernels current
%define buildforkernels akmod
%global debug_package %{nil}

%define kmod_name         ksmbd
%define kmod_driver_path  fs/smb/server
%define repo              local

# name should have a -kmod suffix
Name:           %{kmod_name}-kmod
Version:        6.10
Release:        1%{?dist}
Summary:        ksmbd (fs/smb/server) kernel module(s)
Group:          System Environment/Kernel
License:        GPL-2.0-only
URL:            https://cdn.kernel.org
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Standard kmod build requirements. AkmodsBuildRequires also becomes a
# Requires: of the generated akmod-ksmbd package (see kmodtool's
# print_akmodtemplate), so this is what makes the akmods service able to
# actually redo the koji fetch + build locally on the target machine
# whenever it rebuilds this akmod for a new kernel.
%global AkmodsBuildRequires %{_bindir}/kmodtool koji rpm-build
BuildRequires:  %{AkmodsBuildRequires}
BuildRequires:  kernel-devel

# kmodtool does its magic here. Note --kmodname is %{kmod_name} ("ksmbd"),
# not %{name} ("ksmbd-kmod") -- that's what makes the generated subpackages
# come out as the conventional akmod-ksmbd / kmod-ksmbd (matching e.g.
# RPM Fusion's akmod-nvidia / kmod-nvidia), instead of the redundant
# akmod-ksmbd-kmod / kmod-ksmbd-kmod you'd get from --kmodname %{name}.
%{expand:%(kmodtool --target %{_target_cpu} --repo %{repo} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null | sed 's|extra|updates|g' | sed 's|%{kmod_name}/||g') }

# NOTE: the sed calls above substitute the module's destination path to the
# "updates" directory (instead of "extra") since this driver mirrors an
# in-tree module, not a genuinely third-party one.

%description
The ksmbd (SMB3 kernel server, fs/smb/server) driver. Fedora's kernel
config ships this driver disabled and does not include its source, even
though the code lives upstream in the kernel tree. This package builds it
directly from the Linux kernel source matching each target kernel version,
rather than from a separately maintained out-of-tree copy.

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu} --repo %{repo} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

for kernel_version in %{?kernel_versions} ; do
    kernel_v=${kernel_version%%___*}                            # eg. 6.12.11-200.fc41.x86_64
    kernel_v_no_arch=${kernel_v%.*}                             # eg. 6.12.11-200.fc41
    kernel_extra=${kernel_v#*-}                                 # eg. 200.fc41.x86_64
    kernel_v_no_extra="$(echo -n ${kernel_v} | cut -d"-" -f1)"  # eg. 6.12.11
    kernel_src_dir=${kernel_version##*__}                       # eg. /usr/src/kernels/6.12.11-200.fc41.x86_64

    mkdir -p "${kernel_v_no_arch}"

    # ------------------------------------------------------------------------
    pushd "${kernel_v_no_arch}"

    # Download the exact kernel source used to build this kernel
    koji download-build --arch=src "kernel-${kernel_v}"

    # Unpack source and kernel.spec file
    rpm \
        --define "_sourcedir ${PWD}" \
        --define "_specdir ${PWD}" \
        --define "_builddir ${PWD}" \
        --define "_srcrpmdir ${PWD}" \
        --define "_rpmdir ${PWD}" \
        --define "_buildrootdir ${PWD}/.build" \
        -Uvh kernel-${kernel_v_no_arch}.src.rpm

    # Unpack source and apply (Fedora's own) patches
    # --nodeps here allows to skip build dependency checks (not all kernel build dependencies are needed)
    rpmbuild --nodeps \
        --define "_sourcedir ${PWD}" \
        --define "_specdir ${PWD}" \
        --define "_builddir ${PWD}" \
        --define "_srcrpmdir ${PWD}" \
        --define "_rpmdir ${PWD}" \
        --define "_buildrootdir ${PWD}/.build" \
        -bp --target="$(uname -m)" kernel.spec 2>&1 || true # Even if it fails we are ok!

    if [ %{fedora} -gt 40 ]; then
        build_dir="./kernel-${kernel_v_no_extra}-build/kernel-${kernel_v_no_extra}/linux-${kernel_v}"
    else
        build_dir="./kernel-${kernel_v_no_extra}/linux-${kernel_v}"
    fi

    # Prepare build directory
    mv "$build_dir" ../_kmod_build_${kernel_v}

    popd
    # ------------------------------------------------------------------------
    rm -r "${kernel_v_no_arch}"

    # Copy essential files from kernel src directory
    cp -a ${kernel_src_dir}/{.config,Module.symvers,System.map} ./_kmod_build_${kernel_v}/

    # Set correct extra version in Makefile
    sed -i 's/^EXTRAVERSION.*$/EXTRAVERSION=-'"${kernel_extra}"'/' "./_kmod_build_${kernel_v}/Makefile"
done


%build
for kernel_version in %{?kernel_versions}; do
    yes "" | make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" prepare
    yes "" | make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" modules_prepare
    make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" M=%{kmod_driver_path} CONFIG_SMB_SERVER=m modules
done


%install
for kernel_version in %{?kernel_versions}; do
    make %{?_smp_mflags} -C "${PWD}/_kmod_build_${kernel_version%%___*}/" M=%{kmod_driver_path} INSTALL_MOD_PATH=${RPM_BUILD_ROOT} modules_install

    # Delete modules.* files
    rm -f ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*}/modules.*
done
%{?akmod_install}


%changelog
* Sun August 23 2026 Arno Dubois <arno.du@orange.fr>
- Release 6.10-1
- Rewrite as an akmod/kmodtool package instead of raw DKMS. Rather than
  vendoring a fixed copy of the namjaejeon/ksmbd out-of-tree repository (or
  guessing a kernel.org tarball), the fs/smb/server driver source is fetched
  from Fedora's own matching kernel source via koji, mirroring the approach
  used by akmod-e1000e-no-nvm-check. Built with %%buildforkernels akmod, so
  the akmods service on the target machine compiles it locally against
  whichever kernel(s) are actually installed, and rebuilds automatically
  whenever a new kernel is added.
