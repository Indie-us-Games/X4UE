build: clean
	zip -r x4ue.zip x4ue/

build-dev:
	zip -r x4ue_dev.zip x4ue/

clean:
	rm -f x4ue.zip

clean-dev:
	rm -f x4ue_dev.zip
