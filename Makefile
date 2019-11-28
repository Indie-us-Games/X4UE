build: clean
	zip -r bin/x4ue.zip x4ue/

build-dev: clean-dev
	zip -r bin/x4ue_dev.zip x4ue/

clean:
	rm -f bin/x4ue.zip

clean-dev:
	rm -f bin/x4ue_dev.zip
