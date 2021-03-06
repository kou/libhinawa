Name:			libhinawa
Version:		0.7.0
Release:		1%{?dist}
Summary:		GObject introspection library for devices connected to IEEE 1394 bus

License:		LGPLv2
URL:			https://github.com/takaswie/libhinawa
Source:			%{name}-%{version}.tar.gz

BuildRequires:  automake >= 1.10
BuildRequires:  autoconf >= 2.62
BuildRequires:  libtool >= 2.2.6
BuildRequires:  glib2 >= 2.32, glib2-devel >= 2.32
BuildRequires:  gtk-doc >= 1.18-2
BuildRequires:  gobject-introspection >= 1.32.1, gobject-introspection-devel >= 1.32.1


%description
Hinawa is an gobject introspection library for devices connected to
IEEE 1394 bus. This library supports any types of transactions over
IEEE 1394 bus.  This library also supports some functionality which
ALSA firewire stack produces.

%package		devel
Summary:		Development files for %{name}
Requires:		%{name}%{?_isa} = %{version}-%{release}

%description	devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q


%build
%configure --enable-gtk-doc --disable-static
#make %{?_smp_mflags}
make


%install
rm -rf $RPM_BUILD_ROOT
%make_install
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%{_libdir}/libhinawa.so.*
%{_libdir}/girepository-1.0/*

%files devel
%{_includedir}/libhinawa/*
%{_libdir}/pkgconfig/*
%{_libdir}/libhinawa.so
%{_datadir}/gir-1.0/*
%{_datadir}/gtk-doc/html/hinawa/*
%{_docdir}/libhinawa/*


%changelog
* Fri Feb  5 2016 HAYASHI Kentaro <hayashi@clear-code.com> - 0.7.0-1
- new upstream release.

* Tue Mar  3 2015 Yoshihiro Okada - 0.5.0-1
- new upstream release.
