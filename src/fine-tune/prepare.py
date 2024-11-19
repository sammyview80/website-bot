import json
import os
def convert_to_message_array(input_data, output_file):
    with open(output_file, 'w') as file:
        system_message = {
            "role": "system",
            "content": "You generate a script for mac os."
        }
        
        for entry in input_data:
            message_block = {
                "messages": [
                    system_message,
                    {"role": "user", "content": entry["prompt"]},
                    {"role": "assistant", "content": entry["completion"]}
                ]
            }
            # Write each message block as a single JSON line
            file.write(json.dumps(message_block) + '\n')


# Input data in JSON format (replace this with your actual JSON data)
def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

__dir = os.path.join(os.getcwd(), "src","fine-tune","mac-command-ds.jsonl")
# Convert the input data to the required JSON format
output_data =  convert_to_message_array(load_jsonl(__dir), 'file.jsonl')

# Print the output JSON
print(output_data)