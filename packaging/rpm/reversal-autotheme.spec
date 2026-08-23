Name:           reversal-autotheme
Version:        1.0.0
Release:        1%{?dist}
Summary:        Universal macOS Squircle Icon Theming Engine for Linux Desktops

License:        MIT
URL:            https://github.com/reversal-icon-theme/reversal-autotheme
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3-pillow
Requires:       python3-numpy
Requires:       librsvg2-tools
Requires:       libnotify

%description
Reversal Auto-Theme dynamically scans all installed desktop applications,
extracts upstream branding, and generates pixel-perfect macOS-style squircle
icons matching the Reversal theme specification with live desktop refreshing.

%prep
%autosetup

%build
%py3_build

%install
%py3_install
install -Dm644 data/reversal-autotheme.desktop %{buildroot}%{_datadir}/applications/reversal-autotheme.desktop
install -Dm644 data/icons/reversal-autotheme.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/reversal-autotheme.svg
install -Dm644 data/icons/512x512/reversal-autotheme.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/reversal-autotheme.png

%files
%license LICENSE
%doc README.md
%{_bindir}/reversal-autotheme
%{python3_sitelib}/reversal_autotheme/
%{python3_sitelib}/reversal_autotheme-*.egg-info/
%{_datadir}/applications/reversal-autotheme.desktop
%{_datadir}/icons/hicolor/scalable/apps/reversal-autotheme.svg
%{_datadir}/icons/hicolor/512x512/apps/reversal-autotheme.png

%changelog
* Sun Aug 23 2026 Maintainers <support@example.com> - 1.0.0-1
- Initial production release.
