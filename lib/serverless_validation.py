import podman
from podman.errors.exceptions import ContainerError
import logging
import uuid
import os

serverless_image = "quay.io/parodos-dev/kogito-validator"

class ServerlessValidation(object):

    def __init__(self, workflow):
        self.uuid = uuid.uuid4()
        self.temp_file = f"/tmp/workflow_{self.uuid}"
        if not os.path.exists(self.temp_file):
            os.makedirs(self.temp_file)

        logging.info(f"Create a temp file: {self.temp_file}")
        self.workflow = workflow
        self.client = podman.PodmanClient()
        self.client.images.pull(serverless_image)
        self._create_sample_workflow()

    @property
    def workflow_path(self):
        return f"{self.temp_file}/workflow.sw.json"

    def _create_sample_workflow(self):
        with open(self.workflow_path, "w") as fp:
            fp.write(self.workflow)

    def run(self):
        try:
            container = self.client.containers.run(
                image=serverless_image,
                detach=False,
                remove=False,
                mounts= [
                    {
                        "type": "bind",
                        "source": self.workflow_path,
                        "target": "/workflow.sw.json",
                        "read_only": False,
                        "relabel": "Z"
                    },
                ]
            )
            result = container.decode()
            return (result, "[ERROR]" not in result)
        except ContainerError as e:
            return (b"".join(e.stderr).decode(), False)
