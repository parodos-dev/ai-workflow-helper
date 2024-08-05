WORKFLOW_NAME?="sample-project"
KN?="kn"

project-clean:
	rm -rfv $WORKFLOW_NAME

project-create:
	$(kn) create workflow --name $(WORKFLOW_NAME)

project-run:
	cd $(WORKFLOW_NAME) && kn run

