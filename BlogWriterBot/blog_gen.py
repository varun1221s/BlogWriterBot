import os
import datetime
import requests
from flask import Flask, render_template, request

app = Flask(__name__)
output_folder = "outputBlogs"

def generate_blog(blog_name, blog_prompt, stylistic_preferences, existing_content):
    # Read the content from the file or PDF
    with open(existing_content, 'r') as file:
        content = file.read()

    api_url = "https://api.openai.com/v1/engines/davinci-codex/completions"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": f"{blog_prompt}\n\n{stylistic_preferences}\n\n{content}",
        "max_tokens": 500,
        "temperature": 0.8
    }

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 200:
        generated_blog = response.json()["choices"][0]["text"]
        save_blog(blog_name, generated_blog)
        return generated_blog
    else:
        return None

def save_blog(blog_name, blog_content):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{blog_name}_{timestamp}.txt"
    filepath = os.path.join(output_folder, filename)
    with open(filepath, "w") as file:
        file.write(blog_content)

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/generate_blog', methods=['POST'])
def generate_blog_route():
    blog_name = request.form.get('blog_name')
    blog_prompt = request.form.get('blog_prompt')
    stylistic_preferences = request.form.get('stylistic_preferences')
    existing_content = request.files['existing_content']

    if existing_content:
        # Save the uploaded file
        existing_content.save(existing_content.filename)
        generated_blog = generate_blog(blog_name, blog_prompt, stylistic_preferences, existing_content.filename)

        if generated_blog:
            return render_template("result.html", blog=generated_blog)
        else:
            return render_template("error.html", message="Error occurred while generating the blog.")

    return render_template("error.html", message="No existing content provided.")


if __name__ == "__main__":
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    app.run(debug=True)
