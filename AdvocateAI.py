import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import json
import csv
from rapidfuzz import fuzz
import matplotlib.pyplot as plt
import numpy as np
import nltk
import webbrowser
import os

# Download nltk data silently
nltk.download('punkt', quiet=True)

# ------------------- Load Legal Data -------------------
try:
    with open("legal_terms.json", "r", encoding="utf-8") as f:
        legal_terms = json.load(f)
except FileNotFoundError:
    messagebox.showerror("Error", "Database file 'legal_terms.json' not found!")
    legal_terms = {}

# ------------------- Save Query Logs -------------------
def log_query(user_input, response):
    with open("logs.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([user_input, response])
    with open("chat_history.txt", "a", encoding="utf-8") as f:
        f.write(f"You: {user_input}\nLexiBot: {response}\n\n")

# ------------------- Add / Show Clients -------------------
def add_client():
    name = simpledialog.askstring("Add Client", "Enter client name:")
    if not name:
        return
    date = simpledialog.askstring("Add Client", "Enter hearing date (e.g., 1 Nov 2025):")
    if not date:
        return

    with open("clients.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, date])

    add_message(f"✅ Client '{name}' added for hearing on {date}.")

def show_clients():
    if not os.path.exists("clients.csv"):
        messagebox.showinfo("No Clients", "No clients added yet.")
        return

    with open("clients.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        clients = list(reader)

    if not clients:
        messagebox.showinfo("No Clients", "No clients added yet.")
        return

    add_message("📋 Here are your saved clients:")
    for i, (name, date) in enumerate(clients, 1):
        add_message(f"{i}. {name} — Hearing on {date}", prefix="")

# ------------------- Find Best Match -------------------
def find_best_match(query):
    best_match = None
    highest_score = 0

    for key in legal_terms.keys():
        score = fuzz.ratio(query.lower(), key.lower())
        if score > highest_score:
            highest_score = score
            best_match = key

    if highest_score > 60:
        return legal_terms[best_match]
    else:
        return "⚠️ Sorry, I couldn’t find relevant information for your query."

# ------------------- Handle User Query -------------------
def handle_query():
    user_input = query_entry.get().strip()
    if not user_input or user_input == "Type your query here...":
        messagebox.showwarning("Input Error", "Please enter a query.")
        return

    response = find_best_match(user_input)
    log_query(user_input, response)

    add_message(f"You: {user_input}", prefix="")
    add_message(f"LexiBot: {response}", prefix="")
    query_entry.delete(0, tk.END)

    last_query.set(user_input)
    learn_more_btn.config(state="normal")

# ------------------- Show Stats -------------------
def show_stats():
    try:
        data = []
        with open("logs.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    data.append(row[0].lower())

        if not data:
            messagebox.showinfo("No Data", "No queries logged yet.")
            return

        unique, counts = np.unique(data, return_counts=True)
        top_indices = np.argsort(counts)[-5:]
        top_queries = unique[top_indices]
        top_counts = counts[top_indices]

        plt.figure(figsize=(8, 4))
        plt.barh(top_queries, top_counts, color="#009688")
        plt.xlabel("Number of Searches")
        plt.ylabel("Legal Queries")
        plt.title("Top 5 Most Searched Legal Terms")
        plt.tight_layout()
        plt.show()
    except FileNotFoundError:
        messagebox.showinfo("No Data", "No logs found yet. Ask some questions first!")

# ------------------- Learn More -------------------
def learn_more():
    query = last_query.get()
    if query:
        webbrowser.open(f"https://www.google.com/search?q={query}+Indian+law")

# ------------------- Clear Chat -------------------
def clear_chat():
    confirm = messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat?")
    if confirm:
        chat_box.config(state="normal")
        chat_box.delete(1.0, tk.END)
        chat_box.config(state="disabled")
        learn_more_btn.config(state="disabled")

# ------------------- Helper for Chat -------------------
def add_message(text, prefix="\nLexiBot: "):
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"{prefix}{text}\n")
    chat_box.config(state="disabled")
    chat_box.see(tk.END)

# ------------------- Placeholder -------------------
def on_entry_click(event):
    if query_entry.get() == "Type your query here...":
        query_entry.delete(0, tk.END)
        query_entry.config(fg="white")

def on_focus_out(event):
    if query_entry.get() == "":
        query_entry.insert(0, "Type your query here...")
        query_entry.config(fg="#a0a0a0")

# ------------------- Tkinter GUI -------------------
root = tk.Tk()
root.title("⚖️ LexiBot - AI Legal Assistant")
root.geometry("750x650")
root.config(bg="#102027")

# Title Label
tk.Label(root, text="⚖️ LexiBot: AI-Powered Legal Assistant",
         font=("Segoe UI", 20, "bold"), bg="#102027", fg="#00acc1").pack(pady=12)

# Chat Display
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=85, height=22,
                                     font=("Consolas", 10), bg="#1c313a", fg="white",
                                     insertbackground="white", relief="flat", bd=3)
chat_box.pack(padx=12, pady=10)
chat_box.config(state="disabled")

# User Query Input
query_entry = tk.Entry(root, width=70, font=("Segoe UI", 12), bg="#263238",
                       fg="#a0a0a0", insertbackground="white", relief="flat")
query_entry.insert(0, "Type your query here...")
query_entry.bind("<FocusIn>", on_entry_click)
query_entry.bind("<FocusOut>", on_focus_out)
query_entry.pack(pady=8, ipady=6)

# Buttons Frame
button_frame = tk.Frame(root, bg="#102027")
button_frame.pack(pady=10)

style = {
    "font": ("Segoe UI", 10, "bold"),
    "fg": "white",
    "width": 12,
    "bd": 0,
    "relief": "flat",
    "pady": 6
}

tk.Button(button_frame, text="Ask", command=handle_query, bg="#00acc1", **style).grid(row=0, column=0, padx=6)
tk.Button(button_frame, text="Add Client", command=add_client, bg="#00695c", **style).grid(row=0, column=1, padx=6)
tk.Button(button_frame, text="Show Clients", command=show_clients, bg="#00897b", **style).grid(row=0, column=2, padx=6)
tk.Button(button_frame, text="Show Stats", command=show_stats, bg="#4caf50", **style).grid(row=0, column=3, padx=6)
tk.Button(button_frame, text="Clear Chat", command=clear_chat, bg="#ffa000", **style).grid(row=0, column=4, padx=6)
tk.Button(button_frame, text="Exit", command=root.destroy, bg="#d32f2f", **style).grid(row=0, column=5, padx=6)

# Learn More Button
last_query = tk.StringVar()
learn_more_btn = tk.Button(root, text="🔍 Learn More", command=learn_more, state="disabled",
                           bg="#3949ab", fg="white", font=("Segoe UI", 10, "bold"),
                           relief="flat", width=15, pady=6)
learn_more_btn.pack(pady=8)

# Footer
tk.Label(root, text="© 2025 LexiBot | Developed with ❤️ in Python",
         font=("Segoe UI", 9), bg="#102027", fg="#80cbc4").pack(side="bottom", pady=5)

root.mainloop()
