%global majorminor 1.0
%global date 20120405
# Avoid to emit gstreamer provides - rhbz#1184975
%undefine __gstreamer1_provides

Summary:       Broadcom Crystal HD device interface library
Name:          libcrystalhd
Version:       3.10.0
Release:       3
License:       LGPLv2+
URL:           http://www.broadcom.com/support/crystal-hd/
ExcludeArch:   s390 s390x

#Source:       http://www.broadcom.com/docs/support/crystalhd/crystalhd_linux_20100703.zip
# This tarball and README are inside the above zip file...
# Patch generated from http://git.linuxtv.org/jarod/crystalhd.git
Source0:       libcrystalhd-%{date}.tar.bz2
Source1:       README_07032010
# We're going to use even newer firmware for now
Source2:       bcm70012fw.bin
Source3:       bcm70015fw.bin
# LICENSE file is copy-n-pasted from http://www.broadcom.com/support/crystal_hd/
Source4:       LICENSE
Source5:       libcrystalhd-snapshot.sh
Patch0:        libcrystalhd-nosse2.patch
# https://patchwork2.kernel.org/patch/2247431/
Patch1:        crystalhd-gst-Port-to-GStreamer-1.0-API.patch
%if "%toolchain"=="clang"
Patch2:        fix-clang.patch
%endif
BuildRequires: gcc-c++
BuildRequires: autoconf automake libtool
BuildRequires: gstreamer1-devel >= %{majorminor}
BuildRequires: gstreamer1-plugins-base-devel >= %{majorminor}
BuildRequires: make
Requires:      crystalhd-firmware

%description
The libcrystalhd library provides userspace access to Broadcom Crystal HD
video decoder devices. The device supports hardware decoding of MPEG-2,
h.264 and VC1 video codecs, up to 1080p at 40fps for the first-generation
bcm970012 hardware, and up to 1080p at 60fps for the second-generation
bcm970015 hardware.

%package devel
Summary:       Development libs for libcrystalhd
Requires:      %{name} = %{version}-%{release}

%description devel
Development libraries needed to build applications against libcrystalhd.

%package -n crystalhd-firmware
Summary:       Firmware for the Broadcom Crystal HD video decoder
License:       Redistributable, no modification permitted
BuildArch:     noarch
Requires:      %{name} = %{version}-%{release}

%description -n crystalhd-firmware
Firmwares for the Broadcom Crystal HD (bcm970012 and bcm970015)
video decoders.

%package -n gstreamer-plugin-crystalhd
Summary:       Gstreamer crystalhd decoder plugin
Requires:      %{name} = %{version}-%{release}
Requires:      gstreamer1-plugins-base

%description -n gstreamer-plugin-crystalhd
Gstreamer crystalhd decoder plugin

%prep
%setup -q -n libcrystalhd-%{date}
cp %{SOURCE1} %{SOURCE4} .
%ifnarch %{ix86} ia64 x86_64
%patch0 -p1 -b .nosse2
sed -i -e 's|-msse2||' linux_lib/libcrystalhd/Makefile
%endif
%patch1 -p1 -b .gst1
%patch2 -p1

%build
pushd linux_lib/libcrystalhd/ > /dev/null 2>&1
sed -i -e 's|-D__LINUX_USER__|-D__LINUX_USER__ %{optflags}|' Makefile
%{make_build}
popd > /dev/null 2>&1

pushd filters/gst/gst-plugin/ > /dev/null 2>&1
sh autogen.sh || :

%configure
make %{?_smp_mflags} \
  CFLAGS="%{optflags} -I%{_builddir}/%{buildsubdir}/include -I%{_builddir}/%{buildsubdir}/linux_lib/libcrystalhd" \
  BCMDEC_LDFLAGS="%{?__global_ldflags} -L%{_builddir}/%{buildsubdir}/linux_lib/libcrystalhd -lcrystalhd"
popd > /dev/null 2>&1

%install
pushd linux_lib/libcrystalhd/ > /dev/null 2>&1
make install LIBDIR=%{_libdir} DESTDIR=$RPM_BUILD_ROOT
popd > /dev/null 2>&1

pushd filters/gst/gst-plugin/ > /dev/null 2>&1
make install DESTDIR=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{_libdir}/gstreamer-1.0/libgstbcmdec.{a,la}
popd > /dev/null 2>&1

rm -rf $RPM_BUILD_ROOT/lib/firmware/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/firmware/
install -pm 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_prefix}/lib/firmware/
install -pm 0644 %{SOURCE3} $RPM_BUILD_ROOT%{_prefix}/lib/firmware/

#Install udev rule
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/udev/rules.d
install -pm 0644 driver/linux/20-crystalhd.rules \
  $RPM_BUILD_ROOT%{_prefix}/lib/udev/rules.d


%ldconfig_scriptlets

%files
%doc README_07032010 LICENSE
%{_libdir}/libcrystalhd.so.*

%files devel
%dir %{_includedir}/libcrystalhd
%{_includedir}/libcrystalhd/*
%{_libdir}/libcrystalhd.so

%files -n crystalhd-firmware
%doc LICENSE
%{_prefix}/lib/udev/rules.d/20-crystalhd.rules
%{_prefix}/lib/firmware/bcm70012fw.bin
%{_prefix}/lib/firmware/bcm70015fw.bin

%files -n gstreamer-plugin-crystalhd
%{_libdir}/gstreamer-%{majorminor}/*.so


%changelog
* Mon Jun 19 2023 zhangxiang <zhangxiang@iscas.ac.cn> - 3.10.0-3
- Fix clang build error

* Mon May 23 2022 tanyulong<tanyulong@kylinos.cn> - 3.10.0-2
- Improve the project according to the requirements of compliance improvement

* Mon Aug 23 2021 peijiankang <peijiankang@kylinos.cn> - 3.10.0-1
- Init libcrystalhd for openeular
