.PHONY: db web app lambda

web:
	cd web && $(MAKE) run

app:
	cd app && $(MAKE) run

db:
	sudo docker start db

clean:
	-rm -r build/**
