HOST=schoool.kr
RSYNC_FILES=*

deploy:
	rsync -Pravdtze ssh $(RSYNC_FILES) $(HOST):"\$$HOME/schoool"
	ssh $(HOST) "\
		cd schoool &&\
		(test -d venv || virtualenv venv) &&\
		source venv/bin/activate &&\
		xargs -a requirements.txt -n 1 pip install&&\
		ps aux\
			| grep uwsgi\
			| grep schoool\
			| grep -v grep\
			| awk '{ print \$$2 }'\
			| xargs kill -9 2>/dev/null || echo "" &&\
		uwsgi \$$PWD/config/uwsgi.ini --enable-threads"
	@echo "Done."
