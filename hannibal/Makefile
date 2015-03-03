all: clean hannibal

hannibal:
	mkdir dist
	cd src && find . -name "*py" | xargs zip -q ../dist/hannibal.zip 
	cat misc/runzip.sh dist/hannibal.zip > dist/hannibal
	chmod +x dist/hannibal
	rm dist/hannibal.zip

pkg: pkg-rhel5-master pkg-rhel4-client pkg-rhel5-mcp

pkg-rhel5-master: all
	cd pkg/rhel5-master && tar zcvf ../../dist/bootstrap-rhel5-master.tar.gz . ../../dist/hannibal
	cat misc/selfextract.sh dist/bootstrap-rhel5-master.tar.gz > dist/bootstrap-rhel5-master
	chmod +x dist/bootstrap-rhel5-master
	rm dist/bootstrap-rhel5-master.tar.gz

pkg-rhel4-client: all
	cd pkg/rhel4-client && tar zcvf ../../dist/bootstrap-rhel4-client.tar.gz . ../../dist/hannibal
	cat misc/selfextract.sh dist/bootstrap-rhel4-client.tar.gz > dist/bootstrap-rhel4-client
	chmod +x dist/bootstrap-rhel4-client
	rm dist/bootstrap-rhel4-client.tar.gz

pkg-rhel5-mcp: all
	cd pkg/rhel5-mcp && tar zcvf ../../dist/bootstrap-rhel5-mcp.tar.gz . ../../dist/hannibal
	cat misc/selfextract.sh dist/bootstrap-rhel5-mcp.tar.gz > dist/bootstrap-rhel5-mcp
	chmod +x dist/bootstrap-rhel5-mcp
	rm dist/bootstrap-rhel5-mcp.tar.gz

clean:
	rm -rf dist
	find src -name "*pyc" | xargs rm -f
