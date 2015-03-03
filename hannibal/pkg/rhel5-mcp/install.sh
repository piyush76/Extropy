#!/bin/bash -x

shopt -s nullglob

case $(uname -m) in
	i[3-9]86) INSTARCH=i386 ;;
	*) INSTARCH="$(uname -m)" ;;
esac

rpm -Uvh rpmforge-*${INSTARCH}*.rpm
yum -y install git

rpm -Uvh both/*.rpm ${INSTARCH}-only/*.rpm

cp dist/hannibal /usr/local/bin

# Setup git
yum -y install git
git config --global user.name "MasterControlProgram"
git config --global user.email "root"

mkdir -p /var/service

# symlink python interpreter
if [ -e /opt/python25/bin/python2.5 ] ; then
	ln -s /opt/python25/bin/python2.5 /usr/local/bin/
fi

# Setup runit service for hannibal
mkdir -p /etc/sv/hannibal/log /var/log/services/hannibal

cat > /etc/sv/hannibal/run <<EOF
#!/bin/bash
exec 2>&1
env PATH=\$PATH:/usr/bin:/usr/local/bin:/opt/python25/bin hannibal http-serve 9021
EOF
chmod +x /etc/sv/hannibal/run

cat > /etc/sv/hannibal/log/run <<EOF
#!/bin/bash
exec svlogd -tt /var/log/services/hannibal
EOF
chmod +x /etc/sv/hannibal/log/run

ln -s /etc/sv/hannibal /var/service/hannibal
ln -sf /sbin/sv /etc/init.d/hannibal

# git-daemon service
mkdir -p /etc/sv/git-daemon/log /var/log/services/git-daemon

cat > /etc/sv/git-daemon/run <<EOF
#!/bin/bash
exec 2>&1
exec git-daemon \
	--base-path=/var/lib/git \
	--export-all \
	/var/lib/git
EOF
chmod +x /etc/sv/git-daemon/run

cat > /etc/sv/git-daemon/log/run <<EOF
#!/bin/bash
exec svlogd -tt /var/log/services/git-daemon
EOF
chmod +x /etc/sv/git-daemon/log/run

ln -s /etc/sv/git-daemon /var/service/git-daemon
ln -sf /sbin/sv /etc/init.d/git-daemon
