%define _unpackaged_files_terminate_build 1

Name: net-tui
Version: 0.2.0
Release: alt1
Summary: Terminal network settings for ALT Linux (NM, etcnet, networkd, resolvconf)
License: MIT
Group: System/Configuration/Other
URL: https://github.com/zerospirit79/net-tui

Source: %name-%version.tar
Patch: %name-%version-alt.patch
  
BuildArch: noarch

BuildRequires(pre): rpm-build-pyproject
BuildRequires: python3-module-build
BuildRequires: python3-module-installer
BuildRequires: python3-module-textual
BuildRequires: python3-module-typer
BuildRequires: python3-module-psutil

Requires: python3-module-textual
Requires: python3-module-typer
Requires: python3-module-psutil
Requires: systemd

%description
%name — console TUI/CLI tool to manage network settings on ALT p11.
Supports NetworkManager, ALT network (etcnet), systemd-networkd and resolvconf.

%prep
%setup
%autopatch -p1

%build
%pyproject_build

%install
%pyproject_install
  
%check
%pyproject_run_pytest

%files
%doc README.md
%bin_dir/%name
%python3_sitelibdir/%name
%python3_sitelibdir/%{pyproject_distinfo %pypi_name}/
  
%changelog
* Fri Nov 06 2026 Pavel Shilov <zerospirit@altlinux.org> 0.2.0-alt1
- Add a colorful dashboard with keyboard navigation and a server mode without mouse support.
- Configure hostname, hosts, static IPv4 and resolvconf with preview and recovery on errors.
- Fix double screen pop when returning to the main menu.
- Remove unused pydantic and netifaces dependencies.

* Sat Oct 25 2025 Pavel Shilov <zerospirit@altlinux.org> 0.1.0-alt1
- Initial build for Sisyphus.
