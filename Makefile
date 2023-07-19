.PHONY: db web app

web:
	cd web && $(MAKE) run

app:
	cd app && $(MAKE) run

db:
	sudo docker start db
