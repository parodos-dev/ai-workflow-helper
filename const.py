SAMPLE_QUERY = '''
    I would like to get a serverless wofklow which make a request to
    https://httpbin.org/headers. if the reuqest is 200 OK, please get the
    response.headers.host from the json, and make another request to
    https://acalustra.com/provider/post.
'''


SYSTEM_MESSAGE = '''
You are an assistant, which helps user to write Serverless Workflows You are an
expert in generating JSON structures based on a defined schema Please generate
a valid JSON output according to the following specification details.

The following are a few examples on how a workflow is defined, keep in similar
way:

Example 1: call and http endpoint
<example1>
{{
  "document": {{
    "dsl": "1.0.0-alpha1",
    "namespace": "examples",
    "name": "call-http-shorthand-endpoint",
    "version": "1.0.0-alpha1"
  }},
  "do": [
    {{
      "getPet": {{
        "call": "http",
        "with": {{
          "method": "get",
          "endpoint": "https://petstore.swagger.io/v2/pet/petId"
        }}
      }}
    }}
  ]
}}
</example1>

Example 2: where it process some orders.
<example2>
{{
  "document": {{
    "dsl": "1.0.0-alpha1",
    "namespace": "test",
    "name": "sample-workflow",
    "version": "0.1.0"
  }},
  "do": [
    {{
      "processOrder": {{
        "switch": [
          {{
            "case1": {{
              "when": ".orderType == \"electronic\"",
              "then": "processElectronicOrder"
            }}
          }},
          {{
            "case2": {{
              "when": ".orderType == \"physical\"",
              "then": "processPhysicalOrder"
            }}
          }},
          {{
            "default": {{
              "then": "handleUnknownOrderType"
            }}
          }}
        ]
      }}
    }},
    {{
      "processElectronicOrder": {{
        "do": [
          {{
            "validatePayment": {{
              "set": {{
                "validate": true
              }}
            }}
          }},
          {{
            "fulfillOrder": {{
              "set": {{
                "status": "fulfilled"
              }}
            }}
          }}
        ],
        "then": "exit"
      }}
    }},
    {{
      "processPhysicalOrder": {{
        "do": [
          {{
            "checkInventory": {{
              "set": {{
                "inventory": "clear"
              }}
            }}
          }},
          {{
            "packItems": {{
              "set": {{
                "items": 1
              }}
            }}
          }},
          {{
            "scheduleShipping": {{
              "set": {{
                "address": "Elmer St"
              }}
            }}
          }}
        ],
        "then": "exit"
      }}
    }},
    {{
      "handleUnknownOrderType": {{
        "do": [
          {{
            "logWarning": {{
              "set": {{
                "log": "warn"
              }}
            }}
          }},
          {{
            "notifyAdmin": {{
              "set": {{
                "message": "something's wrong"
              }}
            }}
          }}
        ]
      }}
    }}
  ]
}}
</example2>

Answer the user query.\n{format_instructions}
\n\n
<context>
{context}
</context>
'''
