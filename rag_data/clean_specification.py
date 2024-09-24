import re

def html_to_markdown(content):
    content = re.sub(r'<details>.*?<summary>.*?</summary>', '', content, flags=re.DOTALL)
    content = content.replace('</details>', '')

    content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)

    def table_to_list(match):
        table = match.group(0)
        rows = re.findall(r'<tr>(.*?)</tr>', table, re.DOTALL)
        markdown_list = []
        for row in rows[1:]:
            cell = re.search(r'<td.*?>(.*?)</td>', row, re.DOTALL)
            if cell:
                content = cell.group(1).strip()
                content = re.sub(r'```.*?\n(.*?)```', r'\1', content, flags=re.DOTALL)
                markdown_list.append(f"```json\n{content}\n```")
        return "\n".join(markdown_list)

    content = re.sub(r'<table>.*?</table>', table_to_list, content, flags=re.DOTALL)
    content = re.sub(r'<.*?>', '', content)
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content.strip()

file_path = 'specification.md'  # Replace with your file path
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

simplified_content = html_to_markdown(content)

output_file_path = 'specification_output.md'  # Replace with your desired output file path
with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write(simplified_content)

print(f"Processed file saved as {output_file_path}")
