# main.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import PromptHistory
from extensions import db
from forms import PromptForm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

main = Blueprint('main', __name__)

# Define the CanopusModel class
class CanopusModel:
    def __init__(self, t5_model_path, codet5_model_path):
        self.t5_model = AutoModelForSeq2SeqLM.from_pretrained(t5_model_path)
        self.t5_tokenizer = AutoTokenizer.from_pretrained(t5_model_path)
        self.codet5_model = AutoModelForSeq2SeqLM.from_pretrained(codet5_model_path)
        self.codet5_tokenizer = AutoTokenizer.from_pretrained(codet5_model_path)

    def process_prompt(self, prompt_text, model_type='codet5'):
        if model_type == 't5':
            tokenizer = self.t5_tokenizer
            model = self.t5_model
        elif model_type == 'codet5':
            tokenizer = self.codet5_tokenizer
            model = self.codet5_model
        else:
            raise ValueError("Invalid model_type. Please choose 't5' or 'codet5'.")

        inputs = tokenizer(prompt_text, return_tensors="pt", padding=True, truncation=True)
        outputs = model.generate(inputs.input_ids)
        output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return output_text

# Create an instance of the CanopusModel
canopus_model = CanopusModel(t5_model_path="google-t5/t5-base", codet5_model_path="Salesforce/codet5-small")

@main.route('/')
@login_required
def home():
    form = PromptForm()
    return render_template('home.html', form=form)

@main.route('/prompt', methods=['POST'])
@login_required
def prompt():
    form = PromptForm()
    if form.validate_on_submit():
        # Handle prompt processing here
        prompt_text = form.prompt.data
        output_text = canopus_model.process_prompt(prompt_text, model_type='codet5')
        # Save prompt history
        prompt_history = PromptHistory(user_id=current_user.id, prompt=prompt_text, output=output_text)
        db.session.add(prompt_history)
        db.session.commit()
        flash('Prompt processed successfully!', 'success')
    return redirect(url_for('main.home'))

@main.route('/copy_output/<int:prompt_id>')
@login_required
def copy_output(prompt_id):
    prompt_history = PromptHistory.query.get_or_404(prompt_id)
    # Copy output logic
    copied_output = prompt_history.output
    flash('Output copied successfully!', 'success')
    return render_template('home.html', form=PromptForm(), copied_output=copied_output)
