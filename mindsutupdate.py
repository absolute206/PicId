import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from openai import OpenAI
import base64
from PIL import Image, ImageTk
import pyttsx3

def read_image_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            encoded_image = base64.b64encode(image_data).decode("utf-8")
        return encoded_image
    except Exception as e:
        raise Exception(f"Error reading the image: {e}")

def process_image():
    # Clear the history
    clear_history()

    image_path = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image files", "*.jpg *.jpeg *.png")])

    if image_path:
        try:
            base64_image = read_image_base64(image_path)

            img = Image.open(image_path)
            img = img.resize((400, 300))  # Resize image for display
            img_tk = ImageTk.PhotoImage(img)

            image_label.config(image=img_tk)
            image_label.image = img_tk
            root.update_idletasks()  # Update the GUI to show the image immediately

            # Send the image to the language model
            completion = client.chat.completions.create(
                model="text-davinci-002",
                messages=[
                    {
                        "role": "system",
                        "content": "This is a chat between a user and an assistant. The assistant is helping the user to describe an image. anylyse your awnser check it for accuracy and descibe it in great detail. ",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What’s in this image?"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1000,
                stream=True
            )

            description = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    description += chunk.choices[0].delta.content

            # Insert the text into the reply_text widget
            reply_text.config(state=tk.NORMAL)
            reply_text.insert(tk.END, f"\n{description}")
            reply_text.config(state=tk.DISABLED)

            # Speak the generated text
            speak_text(description)

        except Exception as e:
            messagebox.showerror("Error", f"Error processing image: {e}")

            # Speak the generated text
            speak_text(description)

        except Exception as e:
            messagebox.showerror("Error", f"Error processing image: {e}")

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def clear_history():
    reply_text.config(state=tk.NORMAL)
    reply_text.delete(1.0, tk.END)
    reply_text.config(state=tk.DISABLED)

def change_endpoint():
    endpoint_url = endpoint_entry.get()
    client.base_url = endpoint_url

# Initialize OpenAI client
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

# Create the GUI
root = tk.Tk()
root.title("Image Description Tool")

# Dark theme
root.configure(bg='black')
root.option_add('*background', 'black')
root.option_add('*foreground', 'white')

# Center the GUI
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{int(screen_width/2)}x{int(screen_height/2)}+{int(screen_width/4)}+{int(screen_height/4)}")

# Left column for endpoint settings
left_frame = tk.Frame(root, bg='black')
left_frame.pack(side=tk.LEFT, fill=tk.Y, pady=20)

# Add a column for changing the OpenAI endpoint URL
endpoint_label = tk.Label(left_frame, text="OpenAI Endpoint URL:", bg='black', fg='white')
endpoint_label.pack()
endpoint_entry = tk.Entry(left_frame, width=30)
endpoint_entry.insert(0, client.base_url)
endpoint_entry.pack(pady=10)
change_endpoint_button = tk.Button(left_frame, text="Change Endpoint", command=change_endpoint)
change_endpoint_button.pack()

# Dropdown menu for selecting voices
voices = ["voice-1", "voice-2", "voice-3"]  # Replace with your available voices
voice_label = tk.Label(left_frame, text="Select Voice:", bg='black', fg='white')
voice_label.pack()
voice_combobox = ttk.Combobox(left_frame, values=voices, state="readonly")
voice_combobox.set(voices[0])  # Set the default voice
voice_combobox.pack()

# Main content on the right
main_frame = tk.Frame(root, bg='black')
main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Image display
image_label = tk.Label(main_frame)
image_label.pack(pady=20)

# Select Image Button
select_button = tk.Button(main_frame, text="Select Image", command=process_image)
select_button.pack()

# Chatbox
reply_text = tk.Text(main_frame, wrap=tk.WORD, height=10, width=80, state=tk.DISABLED)
reply_text.pack(pady=20)

# Clear History Button
clear_button = tk.Button(main_frame, text="Clear History", command=clear_history)
clear_button.pack(pady=10)

# Add a close button
close_button = tk.Button(main_frame, text="Close", command=root.destroy)
close_button.pack(pady=10)

root.mainloop()
