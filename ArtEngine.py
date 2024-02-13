import os
import sys
import base64
import requests
from dotenv import load_dotenv
from openai import OpenAI

from PresentationEngine import make_presentation

os.system('cls')

# TODO: use config settings in script
config = dict(
    always_generate_bear = False, # always add an angry, ferocious bear in the prompt, even when there was no bear detected in the input image
    max_image_generation_retries = 3, # number of retries after the first error
    default_image_path = 'input.jpg', # the default input image filename including path
)

print("""
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│    Welcome to ArtEngine by Wilrik De Loose                     │
│    The automatic artbook generator powered by AI               │
│                                                                │
│    Unleashing creativity with the power of artificial          │
│    intelligence to transform your visions into art.            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
""")

cmd_string = "ArtEngine > "
user_input = {
    "track_name" : input(cmd_string + "Track name: "),
    "image_path" : input(cmd_string + "Input path filename (jpg), leave empty for default (input.jpg): "),
    "output_dir" : input(cmd_string + "Output directory, leave empty to use track name: "),
    "variations" : input(cmd_string + "Number of image variations to generate, leave empty for 1: "),
}

track_name = " ".join(user_input["track_name"].split())
user_input["track_name"] = track_name
if not track_name:
    sys.exit("ERROR! User did not specify a track name for the artwork.")

if not user_input["image_path"]:
    user_input["image_path"] = config["default_image_path"]

if not user_input["output_dir"]:
    user_input["output_dir"] = track_name.lower().replace(" ", "_") + "_output"

if not user_input["variations"]:
    user_input["variations"] = 1
else:
    user_input["variations"] = abs(int(user_input["variations"]))

if user_input["variations"] > 5:
    user_input["variations"] = 1

load_dotenv()
client = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url=os.environ["BASE_URL"]
)

def download_image(input_url, output_url):
    """
    Downloads an image from a given URL and saves it to a specified location.

    This method fetches the content of an image from the `input_url`, and writes the image data
    to a file at `output_url`. It uses the `requests` library to make a GET request to the input URL
    and retrieves the image content. The image is then saved in binary write mode to the path specified
    by `output_url`.

    Parameters:
    - input_url (str): The URL from where the image is to be downloaded.
    - output_url (str): The file path where the downloaded image is to be saved.

    Returns:
    - None: The function does not return any value.

    Note:
    - The function assumes that the provided `input_url` is valid and accessible.
    - It also assumes that the `output_url` directory exists and is writable.
    - Ensure that the `requests` library is installed and imported before using this function.

    Example Usage:
    >>> download_image("http://example.com/image.jpg", "/path/to/save/image.jpg")
    """
    img_data = requests.get(input_url).content
    with open(output_url, 'wb') as handler:
        handler.write(img_data)

def encode_image(image_path):
    """
    Encodes an image to a Base64 string.

    This function opens an image file from the specified `image_path`, reads its content in binary mode,
    and then encodes this content into a Base64 string. The Base64 encoding is widely used when there is a
    need to encode binary data, especially when that data needs to be stored and transferred over media that
    are designed to deal with text. This encoding helps to ensure that the data remains intact without
    modification during transport.

    Parameters:
    - image_path (str): The file path of the image to be encoded.

    Returns:
    - str: A Base64-encoded string representation of the image.

    Note:
    - The function assumes that the provided `image_path` is valid and points to an accessible image file.
    - The encoded string is returned in UTF-8 encoding to ensure compatibility with different text processors
      and systems.

    Example Usage:
    >>> encoded_string = encode_image("/path/to/image.jpg")
    >>> print(encoded_string)
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# TODO: shrink input.jpg to 1024x1024 resolution

# Getting the base64 string
base64_image = encode_image(user_input["image_path"])

print(cmd_string + "Analyzing image and generating prompt...\n")

generate_bear = " Create an image of a bear if none was detected in the previously analyzed imagery. The bear should appear angry and ferocious, with its mouth open in a roar. The style should be consistent with the prior analysis." if config["always_generate_bear"] else ""
    
prompt = "Carefully examine the provided image, focusing on its composition, including the setting, central objects, characters, and distinguishing attributes. Pay special attention to the central subject in the image, noting its posture, form, and any unique characteristics that stand out. Observe its stance—whether it's standing, sitting, or in motion—and the expression it conveys, capturing the essence of its demeanor and physicality. Also, take note of the color palette used in the image, particularly the hues and shades defining the bear, the background, and other significant elements. Your task is to formulate a detailed prompt that encapsulates the core aspects of the image. This prompt should guide the creation of an artwork that closely resembles the original, with a strong focus on replicating the central subject's distinct posture, form, and coloration, as well as the overall mood and setting. Specify the art style to ensure that the central subject and other key components are depicted with accuracy and fidelity to the original image, maintaining the integrity of the composition and the atmosphere conveyed.%s Ignore any text in the image. Only output the prompt in natural English language, nothing else." % generate_bear

completion = client.chat.completions.create(
    model="gpt-4-vision-preview",
    max_tokens=2048,
    temperature=0.1,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        ]}
    ],
)
image_prompt = completion.choices[0].message.content
print("Resulting prompt: \n" + image_prompt + "\n")
print(cmd_string + "Generating artbook imagery...")

artstages = [
    # { "type" : "moodboard", "definition" : 'Mood boards are visual collections designed to express the core essence, style, and atmosphere of a specific creative concept. They are composed of an array of carefully selected images, text snippets, color swatches, and various inspirational materials. Each element within a mood board is thoughtfully placed to complement and interact with the others, crafting a unified narrative that encapsulates the theme, mood, and aesthetic vision of the project it embodies. The arrangement of these elements is key, as it should guide the viewer through the mood board in a way that tells a coherent and compelling story about the underlying concept, effectively communicating the intended emotional and visual experience.' },
    # { "type" : "charcoal",  "definition" : 'Charcoal Impressions are defined as: Extremely rough, gestural artworks that prioritize emotion and atmosphere, with no fine detail whatsoever. Just enough to recognize the subject. Utilizing the stark contrast of black and white, they capture the essence of subjects with broad, sweeping strokes and a textural quality that conveys a strong, visceral sense of form and space. Don\'t use color, only black and white.' },
    # { "type" : "concept", "definition" : 'Concept Sketches: Begin with loose, exploratory pen and pencil drawings or sketches that capture the initial ideas, themes, and compositions. These are often rough and not very detailed, focusing on capturing the essence or a fleeting thought. The sketch is not finished and one half of the image doesn\'t have coloring applied yet. Make sure to add sketch details to the image. Only draw the image and not pens, pencils or whatsoever.' },
    # { "type" : "drawing", "definition" : 'Detailed Drawings are defined as: Moving from rough sketches to detailed drawings involves refining the shapes, textures, and details of each element in the composition. This stage is about finalizing the design and layout before moving on to the final medium. It has lots of detail and closely resembles the final artwork, both visually as in quality.' },
    { "type" : "masterpiece", "definition" : 'Exact Copies are defined as: The creation of an exact copy entails producing a work that is an identical replication of the original subject or artwork. This process requires meticulous attention to every aspect of the original, including color, form, texture, and scale. An exact copy is indistinguishable from the original, matching it in every detail and quality, serving as a precise duplicate without deviation.' },
]

output_folder = user_input["output_dir"] + "/"
if (not os.path.isdir(output_folder)):
    os.mkdir(output_folder)

# create empty array for presentation
presentation = []

max_image_generation_retries = 0
for artstage in artstages:
    artstage_object = {
        "title": artstage["type"],
        "image_url": "input.jpg",
        "description": "Test test test",
        "images": []
    }
    for i in range(user_input["variations"]):
        prompt = artstage['definition'] + " Generate a " + artstage["type"] + ", following the definition from before, for the folowing image description: " + image_prompt + ". Make sure that all central subjects are in frame. Don't generate the image from the description, but make sure to generate a " + artstage["type"] + ", based on that description. Don't generate any text, logos or other attributes outside of the " + artstage["type"]

        image_generated = False
        while (not image_generated) and (max_image_generation_retries < config["max_image_generation_retries"]):
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt, # + ", Sigma 24mm f/8",
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )

                # image url parameters
                image_url = response.data[0].url
                output_image = artstage['type']
                iterator = 1
                output_ext = 'jpg'

                output_url = __file__
                while os.path.isfile(output_url):
                    output_url = "%s%s%s.%s" % (output_folder, output_image, str(iterator), output_ext)
                    iterator = iterator + 1

                local_image_url = download_image(image_url, output_url)
                artstage_object["images"].append(output_url)
                print(cmd_string + artstage['type'].capitalize() + " image saved as " + output_url)
                image_generated = True

            except Exception as e:
                print(e)
                print(cmd_string + 'ERROR! Generated prompt not accepted by DALL·E. Rephrasing...\n')
                client.chat.completions.create(
                    model="gpt-4",
                    max_tokens=2048,
                    temperature=0.1,
                    messages=[
                        { "role": "user", "content": "The following prompt was denied by DALL-E: " + image_prompt + " with this error: " + e + ". Change it so that it is accepted in the next try." },
                    ],
                )
                image_prompt = completion.choices[0].message.content
                print(cmd_string + "New prompt: " + image_prompt + "\n")
                max_image_generation_retries += 1

        if max_image_generation_retries == config["max_image_generation_retries"]:
            sys.exit("ERROR! Maximum number or generation retries exceeded (%s)" % config["max_image_generation_retries"])
    
    presentation.append(artstage_object)
            
    # TODO (if openai improves): generate 2 or 3 alternatives to the original artwork
    
# TODO: generate powerpoint
make_presentation(user_input["track_name"], presentation)
print(cmd_string + "Artbook generation complete!\n")