WORKFLOW_NAME?="sample-project"
KN?="kn"

project-clean:
	rm -rfv $WORKFLOW_NAME

project-create:
	$(kn) create workflow --name $(WORKFLOW_NAME)

project-run:
	cd $(WORKFLOW_NAME) && kn run

load-data:
	python main.py load-data specification.md
	python main.py load-data examples.md


clean-data:
	rm -rf chats.db
	rm -rf /tmp/db_faiss
