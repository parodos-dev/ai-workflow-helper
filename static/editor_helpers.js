sample_data = {
  "id": "hello_world",
  "version": "1.0",
  "specVersion": "0.8",
  "name": "Hello World Workflow",
  "description": "JSON based hello world workflow",
  "start": "Inject Hello World",
  "states": [
    {
      "name": "Inject Hello World",
      "type": "inject",
      "data": {
        "greeting": "Hello World"
      },
      "transition": "Inject Mantra"
    },
    {
      "name": "Inject Mantra",
      "type": "inject",
      "data": {
        "mantra": "Serverless Workflow is awesome!"
      },
      "end": true
    }
  ]
};


const editor = SwfEditor.open({
  container: document.getElementById("editorWorkflow"),
  initialContent: Promise.resolve(JSON.stringify({})),
  readOnly: false,
  languageType: "json",
  swfPreviewOptions: { editorMode: "diagram", defaultWidth: "100%" }
});


function waitForPreview(maxAttempts = 20, interval = 500) {
    return new Promise((resolve, reject) => {
        let attempts = 0;
        const checkPreview = async () => {
            try {
                const preview = await editor.getPreview();
                if (preview) {
                    resolve(preview);
                } else if (attempts >= maxAttempts) {
                    reject(new Error("Preview not available after maximum attempts"));
                } else {
                    attempts++;
                    setTimeout(checkPreview, interval);
                }
            } catch (error) {
                attempts++;
                setTimeout(checkPreview, interval);
            }
        };
        checkPreview();
    });
}

function render_workflow(container, data) {
    // @TODO data should be an string
    editor.setContent('workflow.sw.json', data)
        .then(async function() {
            try {
                preview = await waitForPreview()
                container.innerHTML = preview;
            } catch(error){
                console.log("Cannot render the preview");
            }
        });
}

function sample_workflow_rendering() {
    render_workflow(
        document.getElementById("renderWorkflow"),
        JSON.stringify(sample_data));
}
