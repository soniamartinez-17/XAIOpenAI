import os
import prompts
# pip install --upgrade openai
import openai
from openai import OpenAI
# pip install python-dotenv
from dotenv import load_dotenv, find_dotenv
import time
from flask import Flask, render_template, request
from pathlib import Path
from datetime import datetime
import json

app = Flask(__name__)

# load the .env file where de API key is placed
_ = load_dotenv(find_dotenv())
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv('OPENAI_API_KEY'),
)


# ------------- FRONT-END INPUTS -------------------
#  warning not finding index, still works
@app.route("/")
def index():
    return render_template('index.html')


# ------------- FINE-TUNING -------------------
# we are going to use fine-tuning in order to take a large language
# model (LLM) as GPT-3.5, and we can tune it with a specific data set,
# so it can be more concise in a particular task  or behaves in a specific way

# upload training file
# when you upload a file with the training data into the API of openai,
# the server output is a json object that includes an id.
# this id is unique for that file, and it would reference the file in the fine-tuning

def upload_files_for_tuning():
    upload_response = client.files.create(
        file=Path("training_datasets/classification_training.jsonl").open("rb"),
        purpose='fine-tune'
    )
    training_file_id = upload_response.id
    print(f"File uploaded. ID: {training_file_id}")
    return training_file_id


def upload_file_responses(training, prompt, result):
    output_data = {
        "identifier": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # actual date and time
        "model": training,  # model that has been used
        "creative": temperature,  # how creative is the model
        "input": prompt,  # input prompt
        "response": result  # response
    }

    file_path = os.path.join("output_files", "actual_response.json")

    with open(file_path, 'w') as file:
        json.dump(output_data, file, indent=4)

    print(f"Data saved in file: {file_path}")


# use the ID of the upload file to start the fine-tuning of the CPT-3.5-turbo
def start_fine_tuning(training_file_id):
    try:
        fine_tune_response = client.fine_tuning.jobs.create(
            training_file=training_file_id,
            model="gpt-3.5-turbo",  # specify GPT-3.5-turbo model for fine-tuning
            hyperparameters={
                "n_epochs": 1
            }
        )
        fine_tune_id = fine_tune_response.id
        print(f"Fine tuning started. model ID: {fine_tune_id}")
        return fine_tune_id
    except openai.APIConnectionError as e:
        print(f"The server could not be reached: {e}")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        raise
    except openai.RateLimitError as e:
        print(f"A 429 status code was received; we should back off a bit: {e.status_code}; {e.response}")
        raise
    except openai.APIStatusError as e:
        print(f"Error in training fine-tuning: {e.status_code}; {e.response}")
        raise


def check_fine_tune_status(fine_tune_id):
    while True:
        try:
            status_response = client.fine_tuning.jobs.retrieve(fine_tune_id)
            status = status_response.status
            print(f"Current Fine-tuning Status: {status}")
            events = client.fine_tuning.jobs.list_events(fine_tune_id)
            for event in events:
                print(f"Event: {event.message} at {event.created_at}")
            if status == 'succeeded':
                fine_tuned_model = client.fine_tuning.jobs.retrieve(fine_tune_id).fine_tuned_model
                print(f"Fine tuning has been a success: model_name: {fine_tuned_model}")
                return fine_tuned_model
            elif status == 'failed':
                print(f"Fine tuning has been stopped due to an error: {status_response.error.message}")
                break
            else:
                print("Fine Tuning is training...")
                time.sleep(15)  # Wait 5 seconds before verifying the state again
        except openai.APIStatusError as e:
            print(f"Error in training monitoring: {e.status_code}; {e.response}")
            raise


# ------------- GLOBAL VARIABLES ABOUT MODEL -------------------
temperature = 0.7  # how deterministic the chat is going to be; 1 => random // 0 => deterministic
max_tokens = 500


@app.route('/api/get_explanation', methods=['POST'])
def get_explanation(equation, model, training):
    # Context for the machine
    system_message = {"role": "system", "content": prompts.get_system_message()}
    # {"role": "system", "content": prompts.get_system_message()}  # explainer context

    # Create the input prompt
    prompt = prompts.generate_prompt(equation, model)
    user_message = {"role": "user", "content": prompt}

    if training:
        try:
            # API request with training model id
            model_for_explanation = client.chat.completions.create(
                model=training,
                messages=[system_message, user_message],
                max_tokens=max_tokens,
                temperature=temperature
            )

            # Print API Response
            print("API response:")

            result = model_for_explanation.choices[0].message.content

            upload_file_responses(training, prompt, result)
            # Delete a fine-tuned model (must be an owner of the org the model was created in)
            # client.models.delete(fine_tune_id)

            return result
        except openai.APIStatusError as e:
            print(f"Error Connecting to API: {e.status_code}; {e.response}")
            raise

    else:
        # upload file in order to get id for fine-tuning
        file_id = upload_files_for_tuning()
        # fine-tuning process
        fine_tune_id = start_fine_tuning(file_id)
        # fine-tuning monitoring
        fine_tuned_model_id = check_fine_tune_status(fine_tune_id)

        try:
            # API request with training model id just created
            model_for_explanation = client.chat.completions.create(
                model=fine_tuned_model_id,
                messages=[system_message, user_message],
                max_tokens=max_tokens,
                temperature=temperature
            )

            # Print API Response
            print("API response:")

            result = model_for_explanation.choices[0].message.content
            upload_file_responses(fine_tuned_model_id, prompt, result)
            return result
        except openai.APIStatusError as e:
            print(f"Error Connecting to API: {e.status_code}; {e.response}")
            raise


@app.route('/output', methods=['POST'])
def output():
    # get equation from html inputs
    equation = request.form.get('equation')
    # get model type from html inputs
    model = request.form.get('model')
    # get if you want to train or use a trained_model
    training = request.form.get('trained_model_id')

    # getting response from API
    result = get_explanation(equation, model, training)

    # printing response into output html
    return render_template('response.html', result=result)


# Delete a fine-tuned model (must be an owner of the org the model was created in)
# client.models.delete(fine_tune_id)

if __name__ == '__main__':
    app.run(debug=True)
