all: clean
	mkdir dist
	cd src && find . -name "*py" | xargs zip -q ../dist/ender.zip 
	cat misc/runzip.sh dist/ender.zip > dist/ender
	chmod +x dist/ender
	rm dist/ender.zip

clean:
	rm -rf dist
	find src -name "*pyc" | xargs rm -f
