# TODO:
# - deploy to huggingface spaces 
# - Add actual poem generators
# - Add a modal to show that it's a research preview and that their data will be added to the dataset
# - Add a footer to remind the user of the modal
# - Add calculation of ELO scores
# - Add a tab that shows the leadeboard
# - Add smarter model selection than random

import json
from datetime import datetime, timezone
from pathlib import Path

import gradio as gr
import random

from huggingface_hub import CommitScheduler


# Dummy poem generator functions
def poem_generator_1(topic):
    return f"Poem about {topic} from generator 1."


def poem_generator_2(topic):
    return f"Poem about {topic} from generator 2."


def poem_generator_3(topic):
    return f"Poem about {topic} from generator 3."


def poem_generator_4(topic):
    return f"Poem about {topic} from generator 4."


# List of poem generators
poem_generators = [
    poem_generator_1,
    poem_generator_2,
    poem_generator_3,
    poem_generator_4,
]

# Hugging Face dataset setup
# by fixing this path we might get into trouble of the dataset gets huge > 5MB
# but for now it's fine, I don't think we'll get to that size...famous last words
JSON_DATASET_DIR = Path("json_dataset")
JSON_DATASET_DIR.mkdir(parents=True, exist_ok=True)
JSON_DATASET_PATH = JSON_DATASET_DIR / "data.json"

scheduler = CommitScheduler(
    repo_id="r2d2/abba-eval-arena-dataset",
    repo_type="dataset",
    folder_path=JSON_DATASET_DIR,
    path_in_repo="data",
)

def hide_component(component):
    return gr.update(visible=False)


def show_component(component):
    return gr.update(visible=True)


# def activate_button(button):
#     return gr.update(interactive=True)


# def deactivate_button(button):
#     return gr.update(interactive=False)


def primary_button(button):
    return gr.update(variant="primary", interactive=True)


def secondary_button(button):
    return gr.update(variant="secondary", interactive=False)


# Function to run the poem generators and log the results
def generate_poems(topic):
    # first validate the input

    if not len(topic.split()) <= 5:
        print("ERROR!!")
        raise gr.Error("Inputs must be 5 words or less")

    model_a, model_b = random.sample(poem_generators, 2)
    output_a = model_a(topic)
    output_b = model_b(topic)
    return model_a.__name__, output_a, model_b.__name__, output_b, False, False, None


def log_results(
    topic, model_a_name, output_a, model_b_name, output_b, rhyme_a, rhyme_b, preferred
):
    new_entry = {
        "Topic": topic,
        "Model A": model_a_name,
        "Model B": model_b_name,
        "Output A": output_a,
        "Output B": output_b,
        "Correct Rhyme A": rhyme_a,
        "Correct Rhyme B": rhyme_b,
        "Preferred": preferred,
        "Datetime": datetime.now(tz=timezone.utc).isoformat(),
    }

    # Save the new entry to JSON file
    with scheduler.lock:
        with JSON_DATASET_PATH.open("a") as f:
            json.dump(new_entry, f)
            f.write("\n")


# def update_ui(topic):
#     model_a_name, output_a, model_b_name, output_b = generate_poems(topic)
#     log_btn.update(interactive=True)
#     return output_a, output_b, True, True, model_a_name, model_b_name, model_a_name, model_b_name


# Gradio interface
gr.HTML("<h2>🕺💃 Welcome to ABBA Rhyme Arena! 💃🕺</h2>")
with gr.Blocks() as demo:
    topic_input = gr.Textbox(label="Enter a topic (1-5 words)")
    generate_btn = gr.Button("Generate Poems", variant="primary")

    with gr.Row():
        with gr.Column():
            model_a_name_display = gr.Textbox(label="Model A", visible=False)
            poem_a_output = gr.Textbox(label="Poem A")

        with gr.Column():
            model_b_name_display = gr.Textbox(label="Model B", visible=False)
            poem_b_output = gr.Textbox(label="Poem B")

    gr.HTML("<h2>Please evaluate the generated poems:</h2>")
    with gr.Row():
        with gr.Column():
            rhyme_a_correct = gr.Checkbox(label="Correct Rhyme Scheme (A)")
        with gr.Column():
            rhyme_b_correct = gr.Checkbox(label="Correct Rhyme Scheme (B)")

    with gr.Row():
        preferred = gr.Radio(
            label="Which poem do you prefer?", choices=["A", "B", "Both", "Neither"]
        )

    log_btn = gr.Button("Log Results", interactive=False)

    generate_btn.click(
        fn=generate_poems,
        inputs=topic_input,
        outputs=[
            model_a_name_display,
            poem_a_output,
            model_b_name_display,
            poem_b_output,
            rhyme_a_correct,
            rhyme_b_correct,
            preferred
        ],
    ).success(
        hide_component, inputs=[model_a_name_display], outputs=[model_b_name_display]
    ).success(
        hide_component, inputs=[model_b_name_display], outputs=[model_a_name_display]
    ).success(
        primary_button, inputs=[log_btn], outputs=[log_btn]
    ).success(
        secondary_button, inputs=[generate_btn], outputs=[generate_btn]
    )

    log_btn.click(
        fn=log_results,
        inputs=[
            topic_input,
            model_a_name_display,
            poem_a_output,
            model_b_name_display,
            poem_b_output,
            rhyme_a_correct,
            rhyme_b_correct,
            preferred,
        ],
        outputs=None,
    ).then(
        show_component, inputs=[model_a_name_display], outputs=[model_b_name_display]
    ).then(
        show_component, inputs=[model_b_name_display], outputs=[model_a_name_display]
    ).then(
        secondary_button, inputs=[log_btn], outputs=[log_btn]
    ).then(
        primary_button, inputs=[generate_btn], outputs=[generate_btn]
    )

demo.launch()
