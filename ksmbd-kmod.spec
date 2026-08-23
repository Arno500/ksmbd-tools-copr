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
%define repo              local

# name should have a -kmod suffix
Name:           %{kmod_name}-kmod
Version:        6.10
Release:        5%{?dist}
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
%{expand:%(kmodtool --target %{_target_cpu} --repo %{repo} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null | sed 's|extra|updates|g' | sed 's|%{kmod_name}/||g' | sed -E 's|^nohup (.*) &> /dev/null &$|\1|') }

# NOTE: the first sed call above substitutes the module's destination path
# to the "updates" directory (instead of "extra") since this driver mirrors
# an in-tree module, not a genuinely third-party one.
#
# The third sed call strips the "nohup ... &> /dev/null &" backgrounding
# kmodtool puts on akmod-%{kmod_name}'s %posttrans rebuild trigger, so that
# "dnf install kmod-ksmbd" (and any package-level %posttrans re-trigger,
# e.g. on a ksmbd-kmod version bump) actually waits for the koji fetch +
# build to finish and fails loudly, with visible output, if it doesn't --
# instead of silently backgrounding it and reporting success regardless.
# NOTE: this does NOT cover a future *kernel* upgrade -- that rebuild is
# triggered by /etc/kernel/postinst.d/akmodsposttrans, which ships in the
# akmods package itself (not ours to patch) and still backgrounds the
# build. A kernel bump can still leave the module un-built until you check
# `journalctl` or `akmods --force --kmod ksmbd` yourself.

%description
The ksmbd (SMB3 kernel server, fs/smb/server) driver. Fedora's kernel
config ships this driver disabled and does not include its source, even
though the code lives upstream in the kernel tree. This package builds it
directly from the Linux kernel source matching each target kernel version,
rather than from a separately maintained out-of-tree copy.

# kmodtool's generated akmod-%{kmod_name} and kmod-%{kmod_name}-<kernel>
# packages unconditionally Require: %{kmod_name}-kmod-common >= %{version}
# (a version-locked, kernel-independent companion package), but kmodtool
# does not generate that package itself -- RPM Fusion ships it as a fully
# separate sibling spec (e.g. nvidia-kmod-common.spec). We have no actual
# kernel-independent payload to ship, so just provide it as an empty
# subpackage here instead of a whole separate spec/COPR package.
%package -n %{kmod_name}-kmod-common
Summary:        Common files for the %{kmod_name} kernel module variants
Group:          System Environment/Kernel
BuildArch:      noarch

%description -n %{kmod_name}-kmod-common
Empty version-lock placeholder required by kmodtool's generated
akmod-%{kmod_name}/kmod-%{kmod_name} packages. Carries no payload.

%files -n %{kmod_name}-kmod-common
%defattr(-,root,root,-)

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu} --repo %{repo} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

for kernel_version in %{?kernel_versions} ; do
    kernel_v=${kernel_version%%___*}                            # eg. 6.12.11-200.fc41.x86_64
    kernel_v_no_arch=${kernel_v%.*}                             # eg. 6.12.11-200.fc41
    kernel_v_no_extra="$(echo -n ${kernel_v} | cut -d"-" -f1)"  # eg. 6.12.11

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

    mv "$build_dir" ../_koji_src_${kernel_v}

    popd
    # ------------------------------------------------------------------------
    rm -r "${kernel_v_no_arch}"

    # We only need *source* out of the koji-fetched, patch-applied tree --
    # NOT a locally re-prepared kernel build tree. Running our own
    # "make prepare"/"modules_prepare" on that tree (as this spec used to)
    # re-detects the LOCAL machine's gcc/rustc/pahole versions, which can
    # silently drift from whatever produced the actual running kernel (e.g.
    # a gcc update since the kernel was built, or rustc/pahole simply not
    # being installed at all -- Fedora's own koji builders have them, a
    # plain server usually doesn't). That drift changes real CONFIG_*
    # values (seen in the wild: CONFIG_SCHED_CLASS_EXT and other
    # rustc-gated options silently disappearing), which changes struct
    # module's size, which makes the kernel refuse to load the otherwise-
    # fine, correctly-signed module ("Exec format error" /
    # ".gnu.linkonce.this_module section size must match..." in dmesg).
    #
    # The fix: build straight against the already-fully-prepared kernel-devel
    # tree (${kernel_src_dir}, used as KDIR in %build/%install below) --
    # it's guaranteed to match the real running kernel's ABI by construction,
    # no local prepare or toolchain-matching required.
    #
    # We copy the whole fs/ subtree (not just fs/smb/server + fs/smb/common)
    # and point M= directly at fs/smb/server within it, using that
    # directory's own real Makefile as-is. fs/smb/server's sources reach
    # outside fs/smb/ via plain relative includes (e.g. unicode.h pulls in
    # "../../nls/nls_ucs2_utils.h"), so preserving the real fs/ layout is
    # what makes every such include resolve correctly, instead of chasing
    # each cross-directory reference by hand.
    mkdir -p "_kmod_src_${kernel_v}"
    cp -a "_koji_src_${kernel_v}/fs" "_kmod_src_${kernel_v}/"
    rm -rf "_koji_src_${kernel_v}"
done


%build
for kernel_version in %{?kernel_versions}; do
    kernel_v=${kernel_version%%___*}
    kernel_src_dir=${kernel_version##*__}
    make %{?_smp_mflags} -C "${kernel_src_dir}" M="${PWD}/_kmod_src_${kernel_v}/fs/smb/server" CONFIG_SMB_SERVER=m modules
done


%install
for kernel_version in %{?kernel_versions}; do
    kernel_v=${kernel_version%%___*}
    kernel_src_dir=${kernel_version##*__}
    make %{?_smp_mflags} -C "${kernel_src_dir}" M="${PWD}/_kmod_src_${kernel_v}/fs/smb/server" INSTALL_MOD_PATH=${RPM_BUILD_ROOT} modules_install

    # Delete modules.* files
    rm -f ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_v}/modules.*
done
%{?akmod_install}


%changelog
* Sun August 23 2026 Arno Dubois <arno.du@orange.fr>
- Release 6.10-5
- Copy the whole fs/ subtree from the koji-fetched source, instead of just
  fs/smb/server + fs/smb/common, and point M= directly at fs/smb/server
  within it. fs/smb/server's sources reach outside fs/smb/ via plain
  relative includes (e.g. unicode.h pulls in "../../nls/nls_ucs2_utils.h"),
  which broke the build ("fatal error: ../../nls/nls_ucs2_utils.h: No such
  file or directory") once we stopped copying the full kernel tree in
  6.10-4. Preserving the real fs/ layout resolves every such include
  without having to chase each cross-directory reference by hand.
* Sun August 23 2026 Arno Dubois <arno.du@orange.fr>
- Release 6.10-4
- Stop running "make prepare"/"modules_prepare" on the koji-fetched kernel
  tree. That step re-detects the local machine's gcc/rustc/pahole versions
  and can silently disable real CONFIG_* options that don't match what
  actually built the running kernel (observed: CONFIG_SCHED_CLASS_EXT and
  other rustc-gated options vanishing because rustc isn't installed
  locally), changing struct module's size and making the kernel reject an
  otherwise correctly built and signed module with "Exec format error" /
  ".gnu.linkonce.this_module section size must match...". Now only the
  fs/smb/server + fs/smb/common source is taken from the koji tree; the
  actual build happens against the already-fully-prepared kernel-devel
  tree directly, which is guaranteed ABI-correct with no local
  toolchain-matching required.
* Sun August 23 2026 Arno Dubois <arno.du@orange.fr>
- Release 6.10-3
- Strip the "nohup ... &> /dev/null &" backgrounding kmodtool puts on
  akmod-ksmbd's %posttrans rebuild trigger, so "dnf install kmod-ksmbd"
  waits for the actual koji-fetch + build and fails loudly, with visible
  output, instead of silently backgrounding it. Does not cover kernel
  upgrades, whose rebuild trigger lives in the akmods package itself.
* Sun August 23 2026 Arno Dubois <arno.du@orange.fr>
- Release 6.10-2
- Add the ksmbd-kmod-common subpackage that kmodtool's generated
  akmod-ksmbd/kmod-ksmbd packages require but that kmodtool itself does
  not generate. Without it, "dnf install kmod-ksmbd" failed to resolve
  with "no provider for ksmbd-kmod-common >= 6.10".
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
