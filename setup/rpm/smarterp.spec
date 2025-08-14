%global name smarterp
%global release 1
%global unmangled_version %{version}
%global __requires_exclude ^.*smarterp/addons/mail/static/scripts/smarterp-mailgate.py$

Summary: Smarterp Server
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: LGPL-3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: SmartBygg AS <info@smartbygg.no>
Requires: sassc
BuildRequires: python3-devel
BuildRequires: pyproject-rpm-macros
Url: https://www.smartbygg.no

%description
SmartErp is a complete ERP and CRM based on Odoo. The main features are accounting (analytic
and financial), stock management, sales and purchases management, tasks
automation, marketing campaigns, help desk, POS, etc. Technical features include
a distributed server, an object database, a dynamic GUI,
customizable reports, and XML-RPC interfaces.

%generate_buildrequires
%pyproject_buildrequires

%prep
%autosetup

%build
%py3_build

%install
%py3_install

%post
#!/bin/sh

set -e

smarterp_CONFIGURATION_DIR=/etc/smarterp
smarterp_CONFIGURATION_FILE=$smarterp_CONFIGURATION_DIR/smarterp.conf
smarterp_DATA_DIR=/var/lib/smarterp
smarterp_GROUP="smarterp"
smarterp_LOG_DIR=/var/log/smarterp
smarterp_LOG_FILE=$smarterp_LOG_DIR/smarterp-server.log
smarterp_USER="smarterp"

if ! getent passwd | grep -q "^smarterp:"; then
    groupadd $smarterp_GROUP
    adduser --system --no-create-home $smarterp_USER -g $smarterp_GROUP
fi
# Register "$smarterp_USER" as a postgres user with "Create DB" role attribute
su - postgres -c "createuser -d -R -S $smarterp_USER" 2> /dev/null || true
# Configuration file
mkdir -p $smarterp_CONFIGURATION_DIR
# can't copy debian config-file as addons_path is not the same
if [ ! -f $smarterp_CONFIGURATION_FILE ]
then
    echo "[options]
; This is the password that allows database operations:
; admin_passwd = admin
db_host = False
db_port = False
db_user = $smarterp_USER
db_password = False
addons_path = %{python3_sitelib}/smarterp/addons
default_productivity_apps = True
" > $smarterp_CONFIGURATION_FILE
    chown $smarterp_USER:$smarterp_GROUP $smarterp_CONFIGURATION_FILE
    chmod 0640 $smarterp_CONFIGURATION_FILE
fi
# Log
mkdir -p $smarterp_LOG_DIR
chown $smarterp_USER:$smarterp_GROUP $smarterp_LOG_DIR
chmod 0750 $smarterp_LOG_DIR
# Data dir
mkdir -p $smarterp_DATA_DIR
chown $smarterp_USER:$smarterp_GROUP $smarterp_DATA_DIR

INIT_FILE=/lib/systemd/system/smarterp.service
touch $INIT_FILE
chmod 0700 $INIT_FILE
cat << EOF > $INIT_FILE
[Unit]
Description=SmartErp Open Source ERP and CRM based on Odoo
After=network.target

[Service]
Type=simple
User=smarterp
Group=smarterp
ExecStart=/usr/bin/smarterp --config $smarterp_CONFIGURATION_FILE --logfile $smarterp_LOG_FILE
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF


%files
%{_bindir}/smarterp
%{python3_sitelib}/%{name}-*.egg-info
%{python3_sitelib}/%{name}
