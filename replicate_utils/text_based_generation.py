from ollama import chat
from ollama import ChatResponse
import replicate
import os
import tempfile
from replicate_helper import send_to_replicate

def make_prompt(description: str):
    messages = [
        {
            "role": "system",
            "content": (
                "You convert a short keyword into a one-sentence prompt for the nano-banana image model.\n"
                "Constraints: one concise sentence (min 10 words, max 25 words); literal; concrete; neutral; simple colors and textures; "
                "plain object or scene; clarify that there should be no background; no brands; no text; output only the sentence. Dont specify size if user didnt."
            ),
        },
        {"role": "user", "content": "keyword: elephant\nprompt:"},
        {"role": "assistant", "content": "A simple toy elephant with no background and simple coloring and texture."},
        {"role": "user", "content": "keyword: spooky house\nprompt:"},
        {"role": "assistant", "content": "A small spooky wooden house with a crooked roof, minimal texture, simple colors, no background."},
        {"role": "user", "content": f"keyword: {description.strip()}\nprompt:"},
    ]

    response: ChatResponse = chat(
        model="gpt-oss:20b",
        messages=messages,
    )
    return response['message']['content']

def generate_model(image_data, name):
    # Save image to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_file.write(image_data.read())
        temp_path = temp_file.name
    
    try:
        # Use existing send_to_replicate function with glb_only=True
        sanitized_name = send_to_replicate(name, [temp_path], glb_only=True)
        return sanitized_name
    finally:
        # Clean up temporary file
        os.unlink(temp_path)

def generate_from_prompt(description):
    
    # Step 1: Convert description to proper prompt
    prompt = make_prompt(description)
    print(f"Generated prompt: {prompt}")
    
    # Step 2: Generate one image from the prompt
    input_data = {
        "prompt": prompt,
        "aspect_ratio": "1:1",
        "safety_filter_level": "block_medium_and_above"
    }
    
    output = replicate.run("google/imagen-3-fast", input=input_data)
    
    # Step 3: Generate 3D model directly from image data (no disk save)
    model_name = generate_model(output, description)
    
    # Return the final model path
    final_path = f"local_storage/assets/{model_name}.glb"
    return final_path

# example
if __name__ == "__main__":
    result = generate_from_prompt("disco ball")
    print(f"Generated model saved to: {result}")