%define _unpackaged_files_terminate_build 1

Name: net-tui
Version: 0.1.0
Release: alt1
Summary: TUI/CLI for network settings (ALT p11, NM, networkd, resolved)
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
BuildRequires: python3-module-pydantic
BuildRequires: python3-module-psutil
BuildRequires: python3-module-netifaces

Requires: python3-module-textual
Requires: python3-module-typer
Requires: python3-module-pydantic
Requires: python3-module-psutil
Requires: python3-module-netifaces
Requires: systemd

%description
%name — console TUI/CLI tool to manage network settings on ALT p11.
Supports NetworkManager, systemd-networkd and DNS via systemd-resolved.

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
* Sat Oct 25 2025 Pavel Shilov <zerospirit@altlinux.org> 0.1.0-alt1
- Initial build for Sisyphus.
