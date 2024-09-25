import json

fp = open("examples.json", "r")
data = json.loads(fp.read())
fp.close()
print(data)

output = []
for i,v in enumerate(data):
    print(i)
    output.append("# Example {0}\n\n{1}\n```json\n{2}\n```\n\n".format(i, v.get("input"), v.get("output")))

fp = open("examples.md", "w")
fp.write("\n".join(output))
fp.close()
