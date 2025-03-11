import os
import hashlib
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox

def generate_key_components(key: str, length: int):
    seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2 ** 32)
    rng = np.random.default_rng(seed)  # Use a single RNG for both permutation and key stream
    permutation = rng.permutation(length)
    key_stream = rng.integers(0, 256, size=length, dtype=np.uint8)
    return permutation, key_stream

def encrypt_image(input_path: str, output_path: str, key: str):
    try:
        image = Image.open(input_path)
        image_array = np.array(image, dtype=np.uint8)
        original_shape = image_array.shape
        flat_data = image_array.flatten()
        length = flat_data.size

        permutation, key_stream = generate_key_components(key, length)
        permuted_data = flat_data[permutation]
        encrypted_data = np.bitwise_xor(permuted_data, key_stream)
        encrypted_array = encrypted_data.reshape(original_shape)
        encrypted_image = Image.fromarray(encrypted_array)
        encrypted_image.save(output_path)
    except Exception as e:
        raise Exception(f"Encryption failed: {e}")

def decrypt_image(input_path: str, output_path: str, key: str):
    try:
        image = Image.open(input_path)
        image_array = np.array(image, dtype=np.uint8)
        original_shape = image_array.shape
        flat_data = image_array.flatten()
        length = flat_data.size

        permutation, key_stream = generate_key_components(key, length)
        permuted_data = np.bitwise_xor(flat_data, key_stream)
        inverse_permutation = np.argsort(permutation)
        original_data = permuted_data[inverse_permutation]
        original_array = original_data.reshape(original_shape)
        original_image = Image.fromarray(original_array)
        original_image.save(output_path)
    except Exception as e:
        raise Exception(f"Decryption failed: {e}")

class ImageEncryptorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Encryption Tool")
        master.geometry("750x500")
        master.resizable(False, False)

        self.mode = tk.StringVar(value="encrypt")
        self.key = tk.StringVar()
        self.input_path = ""
        self.output_path = ""

        self.top_frame = tk.Frame(master)
        self.top_frame.pack(pady=10)
        self.middle_frame = tk.Frame(master)
        self.middle_frame.pack(pady=10)
        self.bottom_frame = tk.Frame(master)
        self.bottom_frame.pack(pady=10)

        tk.Button(self.top_frame, text="Select Image", command=self.browse_file).grid(row=0, column=0, padx=5)
        tk.Label(self.top_frame, text="Encryption Key:").grid(row=0, column=1, padx=5)
        tk.Entry(self.top_frame, textvariable=self.key, width=20).grid(row=0, column=2, padx=5)
        tk.Label(self.top_frame, text="Mode:").grid(row=0, column=3, padx=5)
        tk.Radiobutton(self.top_frame, text="Encrypt", variable=self.mode, value="encrypt").grid(row=0, column=4, padx=2)
        tk.Radiobutton(self.top_frame, text="Decrypt", variable=self.mode, value="decrypt").grid(row=0, column=5, padx=2)
        tk.Button(self.top_frame, text="Process", command=self.process_image).grid(row=0, column=6, padx=5)

        self.original_label = tk.Label(self.middle_frame, text="Original Image", bd=2, relief="groove")
        self.original_label.grid(row=0, column=0, padx=10)
        self.result_label = tk.Label(self.middle_frame, text="Processed Image", bd=2, relief="groove")
        self.result_label.grid(row=0, column=1, padx=10)

        self.file_info = tk.Label(self.bottom_frame, text="No file selected")
        self.file_info.pack()

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("All Image Files", "*.*"), ("All Files", "*.*")])
        if file_path:
            self.input_path = file_path
            self.file_info.config(text=os.path.basename(file_path))
            self.display_image(file_path, self.original_label)

    def display_image(self, image_path, widget):
        try:
            image = Image.open(image_path)
            max_width, max_height = 300, 300
            img_width, img_height = image.size
            scale_factor = min(max_width / img_width, max_height / img_height)
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)
            image_resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image_resized)
            widget.config(image=photo, text="")
            widget.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image:\n{e}")

    def process_image(self):
        if not self.input_path:
            messagebox.showwarning("Warning", "Please select an image file first.")
            return
        if not self.key.get():
            messagebox.showwarning("Warning", "Please enter an encryption key.")
            return

        base, ext = os.path.splitext(self.input_path)
        if self.mode.get() == "encrypt":
            self.output_path = base + "_encrypted" + ext
            try:
                encrypt_image(self.input_path, self.output_path, self.key.get())
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        else:
            self.output_path = base + "_decrypted" + ext
            try:
                decrypt_image(self.input_path, self.output_path, self.key.get())
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

        messagebox.showinfo("Success", f"Operation completed. Output saved as:\n{self.output_path}")
        self.display_image(self.output_path, self.result_label)

def launch_gui():
    root = tk.Tk()
    gui = ImageEncryptorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
