#
# Conditional build:
%bcond_with	tests		# build with tests
#
Summary:	Network Presence Binding Daemon
Name:		tang
Version:	15
Release:	2
License:	GPL v3
Group:		Applications
Source0:	https://github.com/latchset/tang/releases/download/v%{version}/%{name}-%{version}.tar.xz
# Source0-md5:	8697be932aa3593e6f2ca66c2b8cefd3
Source1:	%{name}.sysusers
URL:		https://github.com/latchset/tang
BuildRequires:	asciidoc
BuildRequires:	gcc
BuildRequires:	jose-devel >= 8
BuildRequires:	llhttp-devel
BuildRequires:	meson
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 2.011
BuildRequires:	systemd-devel
Requires(post,preun,postun):	systemd-units >= 1:250.1
Requires:	coreutils
Requires:	jose >= 8
Requires:	llhttp
Requires:	sed
Requires:	systemd-units >= 1:250.1
Provides:	group(tang)
Provides:	user(tang)

%description
Tang is a small daemon for binding data to the presence of a third
party.

%prep
%setup -q

%build
%meson
%meson_build

%{?with_tests:%meson_test}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/var/db/%{name},%{_sysusersdir},%{systemdunitdir}}

%meson_install

%{__mv} $RPM_BUILD_ROOT%{_prefix}%{systemdunitdir}/* $RPM_BUILD_ROOT%{systemdunitdir}/

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysusersdir}/tang.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 357 %{name}
%useradd -u 357 -d /usr/share/empty -g %{name} -c "Tang Network Presence Daemon User" %{name}

%post
%systemd_post tangd.socket

# Let's make sure any existing keys are readable only
# by the owner/group.
if [ -d /var/db/tang ]; then
    for k in /var/db/tang/*.jwk; do
        test -e "${k}" || continue
        chmod 0440 -- "${k}"
    done
    for k in /var/db/tang/.*.jwk; do
        test -e "${k}" || continue
        chmod 0440 -- "${k}"
    done
    chown tang:tang -R /var/db/tang
fi

%preun
%systemd_preun tangd.socket

%postun
%systemd_postun_with_restart tangd.socket

%files
%defattr(644,root,root,755)
%doc COPYING
%attr(750, tang, tang) /var/db/tang
%attr(755,root,root) %{_bindir}/tang-show-keys
%attr(755,root,root) %{_libexecdir}/tangd
%attr(755,root,root) %{_libexecdir}/tangd-keygen
%attr(755,root,root) %{_libexecdir}/tangd-rotate-keys
%{systemdunitdir}/tangd@.service
%{systemdunitdir}/tangd.socket
%{_mandir}/man8/tang.8*
%{_mandir}/man1/tang-show-keys.1*
%{_mandir}/man1/tangd-rotate-keys.1.*
%{_sysusersdir}/tang.conf
