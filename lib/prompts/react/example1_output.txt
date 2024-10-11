I can see the problems in your workflow, this is the fixed version:
```json
{
  "id": "getTemperature",
  "name": "Get temperature by room",
  "version": "1.0",
  "specVersion": "0.8",
  "start": "getAllRoomTemperature",
  "functions": [
    {
      "name": "getRoomTemperature",
      "type": "custom",
      "operation": "rest:get:http://office-status.local/temperature/{room_name}"
    },
    {
      "name": "reportInfo",
      "type": "custom",
      "operation": "rest:post:http://erp.local/roomTemperatures"
    }
  ],
  "states": [
    {
      "name": "getAllRoomTemperature",
      "type": "foreach",
      "inputCollection": "${ .rooms }",
      "outputCollection": "${ .results }",
      "iterationParam": "roomName",
      "actions": [
        {
          "functionRef": {
            "refName": "getRoomTemperature",
            "arguments": {
              "room_name": "${ .roomName }"
            }
          },
          "actionDataFilter": {
            "results": "{room: .roomName, temperature:.temperature}"
          }
        }
      ],
      "transition": "reportInfo"
    },
    {
      "name": "reportInfo",
      "type": "operation",
      "actions": [
        {
          "functionRef": {
            "refName": "reportInfo",
            "arguments": {
              "rooms": "${ .results }"
            }
          },
          "actionDataFilter": {
            "toStateData": ".reportInformation"
          }
        }
      ],
      "end": true
    }
  ]
}
```

The fixes are:

- User reported error in path `states.0` and the error message than transition field should have a minLength of 1. Based on serverless workflow should be pointed to the next state, in this case `reportInfo`
- The error in state.1 menas that the object should have some required values: name, type, actions, end or transition. Because the state is the last one, we set end field to true.
- The maven errors looks like that are related to the jsonschema output.
