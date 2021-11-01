.PHONY: start stop enable install.dashboard install.scraper install
.DEFAULT_GOAL := start

stop:
	sudo systemctl stop dashboard.service

start:
	sudo systemctl start dashboard.service

enable:
	sudo systemctl enable dashboard.service

install.dashboard:
	@echo Install dashboard
	sudo systemctl stop dashboard.service
	sudo cp dashboard/dashboard.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable dashboard.service
	sudo systemctl start dashboard.service

install.scraper:
	@echo Install scraper
	sudo cp scraper/scraper_job.sh /etc/cron.d/scraper_job
	sudo chmod 600 /etc/cron.d/scraper_job

install: install.dashboard install.scraper
