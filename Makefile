all: clean sub-ender sub-hannibal sub-puppet

clean:
	rm -rf dist build

prep: clean
	mkdir dist build

sub-ender: prep
	cd ender && make all
	cp ender/dist/* dist/

sub-hannibal: prep
	cd hannibal && make all pkg
	cp hannibal/dist/* dist/

sub-puppet: prep sub-ender sub-hannibal
	mkdir build/puppet
	cp -R puppet/* build/puppet/
	mkdir build/puppet/runit/files
	cp dist/ender build/puppet/runit/files/ender
	cp dist/hannibal build/puppet/puppet/files/hannibal
	cd build && tar zcvf ../dist/puppet.bundle.tar.gz puppet
