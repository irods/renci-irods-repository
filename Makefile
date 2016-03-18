.PHONY: all clean

all:
	./generate_packages.py -v

clean:
	rm -rf build*
	rm -f *.deb
	rm -f *.rpm
