#!/bin/bash -x

shopt -s nullglob

case $(uname -m) in
	i[3-9]86) INSTARCH=i386 ;;
	*) INSTARCH="$(uname -m)" ;;
esac

rpm -Uvh rpmforge-*${INSTARCH}*.rpm
yum -y install which ruby ruby-libs ruby-irb ruby-rdoc postgresql-libs createrepo thttpd git postgresql-server

rpm -Uvh both/*.rpm ${INSTARCH}-only/*.rpm

/etc/init.d/postgresql start
cp dist/hannibal /usr/local/bin
if [ -e /opt/python25/bin/python2.5 ] ; then
	ln -s /opt/python25/bin/python2.5 /usr/local/bin/
fi
git config --global user.name "Puppetmaster"
git config --global user.email "root"
