# flake8: noqa E501
import os

SAMPLE_QUERY = '''
    Please create a serverless wofklow which make a request to https://httpbin.org/headers. if the reuqest is 200 OK, please get the response.headers.host from the json, and make another request to https://acalustra.com/provider/post.
'''

class ExamplesIterator:
    def __init__(self, directory):
        self.directory = directory
        self.examples = self._load_examples()
        self.index = 0

    def _load_examples(self):
        examples = []
        files = os.listdir(self.directory)
        input_files = sorted([f for f in files if f.endswith('_input.txt')])

        for input_file in input_files:
            example_num = input_file.split('_')[0]
            output_file = f"{example_num}_output.txt"

            if output_file in files:
                with open(os.path.join(self.directory, input_file), 'r') as f:
                    input_text = f.read()
                with open(os.path.join(self.directory, output_file), 'r') as f:
                    output_text = f.read()
                examples.append({
                    "input": input_text,
                    "output": output_text
                })
        return examples

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.examples):
            result = self.examples[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration

EXAMPLES=list(ExamplesIterator("./lib/prompts/examples/"))

SYSTEM_MESSAGE = '''
You're a agent which help users to write Serverless workflows.

## Schema

```json
{schema}
```

### Well formatted instance

```json
{{
 "id": "fillglassofwater",
 "name": "Fill glass of water workflow",
 "version": "1.0",
 "specVersion": "0.8",
 "start": "Check if full",
 "functions": [
  {{
   "name": "Increment Current Count Function",
   "type": "expression",
   "operation": ".counts.current += 1 | .counts.current"
  }}
 ],
 "states": [
  {{
   "name": "Check if full",
   "type": "switch",
   "dataConditions": [
    {{
     "name": "Need to fill more",
     "condition": "${{ .counts.current < .counts.max }}",
     "transition": "Add Water"
    }},
    {{
     "name": "Glass full",
     "condition": ".counts.current >= .counts.max",
     "end": true
    }}
   ],
   "defaultCondition": {{
    "end": true
   }}
  }},
  {{
   "name": "Add Water",
   "type": "operation",
   "actions": [
    {{
     "functionRef": "Increment Current Count Function",
     "actionDataFilter": {{
      "toStateData": ".counts.current"
     }}
    }}
   ],
   "transition": "Check if full"
  }}
 ]
}}
```

# INSTRUCTIONS:

1) Plan how to create a workflow, including the initial state, end state, loops, and functions.
2) Define the name, description, and ID for the workflow.
3) Complete the states array in the workflow JSON based on the user's input.

# RULES:
- Specversion is always 0.8 and it's a required field.
- Version is always 1.0 and it's a required field.
- You follow the format Instructions, and keep data acording to the jsonschema.
- Do not use any previous information related to serverless workflow schemas. You can look in context and in the examples for references.
- Functions must be utilized in the states.
- Ensure that the ID, name, description, and start state are always present.
- All required fields must be included in your output.
- Write all tasks in the states section.
- The output should be formatted as a JSON instance that adheres to the given JSON schema below.
```json
{{
   "id": "myworkflowid",
   "version": "1.0",
   "specVersion": "0.8",
   "name": "User example workflow",
   "description": "And empty workflow",
   "start": "CheckApplication",
   "functions": [ ],
   "states":[]
}}
```

CONTEXT:
{context}
'''
