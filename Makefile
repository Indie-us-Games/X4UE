build: clean mkdir-bin
	zip -r bin/x4ue.zip x4ue/

build-dev: clean-dev mkdir-bin
	zip -r bin/x4ue_dev.zip x4ue/

clean:
	rm -f bin/x4ue.zip

clean-dev:
	rm -f bin/x4ue_dev.zip

mkdir-bin:
	mkdir bin/
