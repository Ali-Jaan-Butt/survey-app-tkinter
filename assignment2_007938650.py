import tkinter as tk  # Importing tkinter module as 'tk' to create GUI applications
from tkinter import Tk, Canvas, Button, BOTH, Toplevel, Label, messagebox, ttk  # Importing specific tkinter classes for GUI components
from tkinter import *  # Importing all tkinter functions and classes
from PIL import Image, ImageTk  # Importing PIL's Image and ImageTk for handling images in GUI
import json  # Importing JSON module for reading and writing JSON files
import os  # Importing OS module for file and directory operations


def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):  # Function to draw a rounded rectangle
    """Draw a rounded rectangle on a canvas."""  # Function docstring explaining its purpose
    points = [  # Define the points that form the rounded rectangle
        (x1 + radius, y1),  # Start point of the top-left rounded corner
        (x2 - radius, y1),  # End point of the top edge before the top-right rounded corner
        (x2 - radius, y1),  # Control point for top-right corner curve
        (x2, y1),           # Anchor point for top-right corner curve
        (x2, y1 + radius),  # Start of the right edge after the top-right rounded corner
        (x2, y2 - radius),  # End of the right edge before the bottom-right rounded corner
        (x2, y2 - radius),  # Control point for bottom-right corner curve
        (x2 - radius, y2),  # Anchor point for bottom-right corner curve
        (x2 - radius, y2),  # End point of the bottom edge before the bottom-left rounded corner
        (x1 + radius, y2),  # Start point of the bottom-left rounded corner
        (x1 + radius, y2),  # Control point for bottom-left corner curve
        (x1, y2 - radius),  # Anchor point for bottom-left corner curve
        (x1, y2 - radius),  # Start of the left edge after the bottom-left rounded corner
        (x1, y1 + radius),  # End of the left edge before the top-left rounded corner
        (x1, y1 + radius),  # Control point for top-left corner curve
        (x1 + radius, y1),  # Anchor point for top-left corner curve, completing the shape
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)  # Create a smooth polygon and return its reference


def create_rounded_button(canvas, x, y, width, height, text, bg, fg, command):
    """Creates a rounded button on the canvas."""
    radius = height // 2
    x1, y1, x2, y2 = x - width // 2, y - height // 2, x + width // 2, y + height // 2

    # Draw rounded rectangle
    canvas.create_oval(x1, y1, x1 + height, y1 + height, fill=bg, outline=bg)  # Left circle
    canvas.create_oval(x2 - height, y1, x2, y1 + height, fill=bg, outline=bg)  # Right circle
    canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=bg, outline=bg)  # Center rectangle

    # Add button text
    button_text = canvas.create_text(x, y, text=text, font=("Helvetica", 14, "bold"), fill=fg)

    # Bind click event
    def on_click(event):
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            command()

    canvas.tag_bind(button_text, "<Button-1>", on_click)


def open_admin_dashboard():
    """Open the admin dashboard to display survey data."""
    dashboard_window = Toplevel()
    dashboard_window.title("Admin Dashboard")
    dashboard_window.geometry("900x600")
    dashboard_window.configure(bg="#EDF2F4")

    # Canvas for design
    dashboard_canvas = Canvas(dashboard_window, width=900, height=600, bg="#A0E1F5", highlightthickness=0)
    dashboard_canvas.place(x=0, y=0)

    # Add rounded rectangle (white card)
    create_rounded_rectangle(dashboard_canvas, 50, 50, 850, 550, radius=40, fill="#FFFFFF", outline="#FFFFFF")

    # Add title
    dashboard_canvas.create_text(450, 90, text="Admin Dashboard", font=("Arial", 26, "bold"), fill="#2B2D42")

    # Create a table to display survey data
    tree = ttk.Treeview(dashboard_window, columns=("Name", "Question", "Answer"), show="headings")
    tree.heading("Name", text="Name")
    tree.heading("Question", text="Question")
    tree.heading("Answer", text="Answer")
    tree.column("Name", width=200, anchor="center")
    tree.column("Question", width=400, anchor="center")
    tree.column("Answer", width=200, anchor="center")
    tree.place(x=70, y=150, width=760, height=340)

    # Add a vertical scrollbar for the Treeview
    scrollbar = ttk.Scrollbar(dashboard_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.place(x=830, y=150, height=340)

    # Load survey data
    filename = "survey_data.json"
    if os.path.exists(filename):
        try:
            with open(filename, "r") as file:
                # Attempt to load all JSON arrays
                all_data = []
                for chunk in file.read().split("]["):  # Split at ][
                    if not chunk.startswith("["):
                        chunk = "[" + chunk
                    if not chunk.endswith("]"):
                        chunk = chunk + "]"
                    all_data.extend(json.loads(chunk))

                # Insert data into the Treeview
                for entry in all_data:
                    name = entry.get("name", "Unknown")
                    answers = entry.get("answers", {})
                    if isinstance(answers, dict):  # Ensure answers are in the correct format
                        for question, answer in answers.items():
                            tree.insert("", "end", values=(name, question, answer))
                    else:
                        messagebox.showwarning("Invalid Data", f"Answers for {name} are not properly formatted.")
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Error reading JSON file: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    else:
        messagebox.showinfo("No Data", "No survey data available.")

    def view_analysis():
        """Display statistical analysis of viewers data."""
        # Load viewers data from the JSON file
        filename = "viewers_data.json"
        if not os.path.exists(filename):
            messagebox.showinfo("No Data", "No viewers data available.")
            return

        try:
            with open(filename, "r") as file:
                data = json.load(file)

            if not data:
                messagebox.showinfo("No Data", "No viewers data available.")
                return

            # Calculate statistics
            ages = [entry.get("age", 0) for entry in data if isinstance(entry.get("age"), (int, float))]
            total_viewers = len(data)
            avg_age = sum(ages) / total_viewers if total_viewers > 0 else 0

            # Calculate standard deviation of age
            variance = sum((age - avg_age) ** 2 for age in ages) / total_viewers if total_viewers > 0 else 0
            std_dev = variance ** 0.5

            num_females = sum(1 for entry in data if entry.get("sex") == "Female")

        except json.JSONDecodeError:
            messagebox.showerror("Error", "The data file is corrupted.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            return

        # Create the analysis window
        analysis_window = Toplevel()
        analysis_window.title("Statistical Analysis")
        analysis_window.geometry("600x400")
        analysis_window.configure(bg="#EDF2F4")

        # Canvas for design
        analysis_canvas = Canvas(analysis_window, width=600, height=400, bg="#A0E1F5", highlightthickness=0)
        analysis_canvas.place(x=0, y=0)

        # Add rounded rectangle (white card)
        create_rounded_rectangle(analysis_canvas, 50, 50, 550, 350, radius=40, fill="#FFFFFF", outline="#FFFFFF")

        # Add title
        analysis_canvas.create_text(300, 100, text="Statistical Analysis", font=("Arial", 24, "bold"), fill="#2B2D42")

        # Display statistics
        analysis_canvas.create_text(300, 180, text=f"Average Age: {avg_age:.2f}", font=("Arial", 16), fill="#555555")
        analysis_canvas.create_text(300, 220, text=f"Standard Deviation: {std_dev:.2f}", font=("Arial", 16), fill="#555555")
        analysis_canvas.create_text(300, 260, text=f"Number of Females: {num_females}", font=("Arial", 16), fill="#555555")

        # Add rounded button for close
        create_rounded_button(
            analysis_canvas,
            x=300,
            y=320,
            width=120,
            height=40,
            text="Close",
            bg="#118AB2",
            fg="#FFFFFF",
            command=analysis_window.destroy,
        )

    # Add "View Analysis" button
    create_rounded_button(
        dashboard_canvas,
        x=400,
        y=520,
        width=150,
        height=50,
        text="View Analysis",
        bg="#EF476F",
        fg="#FFFFFF",
        command=view_analysis,
    )

    # Add "Close" button
    create_rounded_button(
        dashboard_canvas,
        x=600,
        y=520,
        width=150,
        height=50,
        text="Close",
        bg="#118AB2",
        fg="#FFFFFF",
        command=dashboard_window.destroy,
    )


def open_login_page():
    """Open the login page window."""

    def validate_login():
        """Validate username and password."""
        username = username_entry.get()
        password = password_entry.get()
        if username == "admin" and password == "password123":
            messagebox.showinfo("Login Successful", "Welcome, Admin!")
            login_window.destroy()
            open_admin_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")

    # Create a new window for login
    login_window = Toplevel()
    login_window.title("Admin Login")
    login_window.geometry("500x400")
    login_window.configure(bg="#E8F5FD")

    # Canvas for styling
    login_canvas = Canvas(login_window, bg="#A0E1F5", highlightthickness=0)
    login_canvas.pack(fill=BOTH, expand=True)

    # Add a white card in the center
    card_x1, card_y1, card_x2, card_y2 = 50, 80, 450, 350
    radius = 20

    # Draw the rounded rectangle (white card)
    login_canvas.create_oval(card_x1, card_y1, card_x1 + 2 * radius, card_y1 + 2 * radius, fill="white",
                             outline="white")
    login_canvas.create_oval(card_x2 - 2 * radius, card_y1, card_x2, card_y1 + 2 * radius, fill="white",
                             outline="white")
    login_canvas.create_rectangle(card_x1 + radius, card_y1, card_x2 - radius, card_y1 + 2 * radius, fill="white",
                                  outline="white")
    login_canvas.create_rectangle(card_x1, card_y1 + radius, card_x2, card_y2 - radius, fill="white", outline="white")
    login_canvas.create_oval(card_x1, card_y2 - 2 * radius, card_x1 + 2 * radius, card_y2, fill="white",
                             outline="white")
    login_canvas.create_oval(card_x2 - 2 * radius, card_y2 - 2 * radius, card_x2, card_y2, fill="white",
                             outline="white")
    login_canvas.create_rectangle(card_x1 + radius, card_y2 - radius, card_x2 - radius, card_y2, fill="white",
                                  outline="white")

    # Add title
    login_canvas.create_text(250, 110, text="Admin Login", font=("Helvetica", 20, "bold"), fill="#333333")

    # Add username and password fields
    login_canvas.create_text(80, 160, text="Username", font=("Helvetica", 14), fill="#555555", anchor="w")
    username_entry = Entry(login_window, font=("Helvetica", 12), bd=0, relief="solid", bg="#2e2c2c",
                           highlightthickness=1)
    username_entry.place(x=80, y=180, width=250, height=30)

    login_canvas.create_text(80, 220, text="Password", font=("Helvetica", 14), fill="#555555", anchor="w")
    password_entry = Entry(login_window, font=("Helvetica", 12), bd=0, relief="solid", bg="#2e2c2c",
                           highlightthickness=1, show="*")
    password_entry.place(x=80, y=240, width=250, height=30)

    # Add login button
    def draw_button(canvas, x, y, width, height, text, command):
        radius = height // 2
        x1, y1, x2, y2 = x - width // 2, y - height // 2, x + width // 2, y + height // 2

        canvas.create_oval(x1, y1, x1 + height, y1 + height, fill="#1976D2", outline="#1976D2")
        canvas.create_oval(x2 - height, y1, x2, y1 + height, fill="#1976D2", outline="#1976D2")
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill="#1976D2", outline="#1976D2")

        button_text = canvas.create_text(x, y, text=text, font=("Helvetica", 14, "bold"), fill="white")

        def on_click(event):
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                command()

        canvas.tag_bind(button_text, "<Button-1>", on_click)

    draw_button(login_canvas, 250, 300, 200, 50, "Login", validate_login)

    # Footer
    login_canvas.create_text(
        250, 380, text="\u00A9 2024 Singing Sculpture - All Rights Reserved", font=("Helvetica", 10), fill="#555555"
    )


def create_survey_page():
    """Create the survey page with the modern theme."""
    survey_window = Toplevel()
    survey_window.title("Survey Page")
    survey_window.geometry("900x600")
    survey_window.configure(bg="#E8F5FD")

    # Canvas for styling
    survey_canvas = Canvas(survey_window, bg="#A0E1F5", highlightthickness=0)
    survey_canvas.pack(fill=BOTH, expand=True)

    # Add a white card in the center
    card_x1, card_y1, card_x2, card_y2 = 50, 50, 850, 550
    radius = 40

    # Draw the rounded rectangle (white card)
    survey_canvas.create_oval(card_x1, card_y1, card_x1 + 2 * radius, card_y1 + 2 * radius, fill="white", outline="white")
    survey_canvas.create_oval(card_x2 - 2 * radius, card_y1, card_x2, card_y1 + 2 * radius, fill="white", outline="white")
    survey_canvas.create_rectangle(card_x1 + radius, card_y1, card_x2 - radius, card_y1 + 2 * radius, fill="white", outline="white")
    survey_canvas.create_rectangle(card_x1, card_y1 + radius, card_x2, card_y2 - radius, fill="white", outline="white")
    survey_canvas.create_oval(card_x1, card_y2 - 2 * radius, card_x1 + 2 * radius, card_y2, fill="white", outline="white")
    survey_canvas.create_oval(card_x2 - 2 * radius, card_y2 - 2 * radius, card_x2, card_y2, fill="white", outline="white")
    survey_canvas.create_rectangle(card_x1 + radius, card_y2 - radius, card_x2 - radius, card_y2, fill="white", outline="white")

    # Add title
    survey_canvas.create_text(450, 100, text="Survey Form", font=("Helvetica", 24, "bold"), fill="#333333")

    # Form fields
    tk.Label(survey_window, text="Name:", font=("Helvetica", 12), bg="#E8F5FD", fg="#555555").place(x=70, y=140)
    global name_entry
    name_entry = tk.Entry(survey_window, font=("Helvetica", 12), bd=2, relief="solid")
    name_entry.place(x=150, y=140, width=250)

    tk.Label(survey_window, text="Age:", font=("Helvetica", 12), bg="#E8F5FD", fg="#555555").place(x=70, y=180)
    global age_entry
    age_entry = tk.Entry(survey_window, font=("Helvetica", 12), bd=2, relief="solid")
    age_entry.place(x=150, y=180, width=250)

    tk.Label(survey_window, text="Sex:", font=("Helvetica", 12), bg="#E8F5FD", fg="#555555").place(x=70, y=220)
    global sex_var
    sex_var = tk.StringVar(value="")
    sex_frame = tk.Frame(survey_window, bg="#E8F5FD")
    tk.Radiobutton(sex_frame, text="Male", variable=sex_var, value="Male", bg="#050708", font=("Helvetica", 10)).pack(side=tk.LEFT)
    tk.Radiobutton(sex_frame, text="Female", variable=sex_var, value="Female", bg="#050708", font=("Helvetica", 10)).pack(side=tk.LEFT)
    tk.Radiobutton(sex_frame, text="Other", variable=sex_var, value="Other", bg="#050708", font=("Helvetica", 10)).pack(side=tk.LEFT)
    sex_frame.place(x=150, y=220)

    tk.Label(survey_window, text="Ethnicity:", font=("Helvetica", 12), bg="#E8F5FD", fg="#555555").place(x=70, y=260)
    global ethnicity_var
    ethnicity_var = tk.StringVar(value="")
    ethnicity_menu = tk.OptionMenu(survey_window, ethnicity_var, "White", "Black", "Chinese", "Asian", "Others")
    ethnicity_menu.config(font=("Helvetica", 10), bg="#FFFFFF", fg="#555555", bd=2)
    ethnicity_menu.place(x=150, y=260)

    tk.Label(survey_window, text="Disabled Status:", font=("Helvetica", 12), bg="#E8F5FD", fg="#555555").place(x=70, y=300)
    global disabled_var
    disabled_var = tk.StringVar(value="")
    disabled_frame = tk.Frame(survey_window, bg="#E8F5FD")
    tk.Radiobutton(disabled_frame, text="Yes", variable=disabled_var, value="Yes", bg="#050708", font=("Helvetica", 10)).pack(side=tk.LEFT)
    tk.Radiobutton(disabled_frame, text="No", variable=disabled_var, value="No", bg="#050708", font=("Helvetica", 10)).pack(side=tk.LEFT)
    disabled_frame.place(x=150, y=300)

    def submit_survey():
        """Handle the submission of the survey form."""
        name = name_entry.get()
        age = age_entry.get()
        sex = sex_var.get()
        ethnicity = ethnicity_var.get()
        disabled = disabled_var.get()
        try:
            age = float(age)
        except:
            age = None
            messagebox.showerror("Error", "Please enter the age in integers.")

        if not name or not age or not sex or not ethnicity or not disabled:
            messagebox.showerror("Error", "Please fill out all fields.")
            return

        messagebox.showinfo("Survey Submitted", "Thank you for completing the survey!")
        print(f"Name: {name}, Age: {age}, Sex: {sex}, Ethnicity: {ethnicity}, Disabled: {disabled}")
        store_data(name, age, sex, ethnicity, disabled)
        survey_window.destroy()
        create_questionnaire_page()

    # Add submit button (with rounded corners)
    def draw_button(canvas, x, y, width, height, text, command):
        """Draw a rounded button on the canvas."""
        radius = height // 2
        x1, y1, x2, y2 = x - width // 2, y - height // 2, x + width // 2, y + height // 2

        canvas.create_oval(x1, y1, x1 + height, y1 + height, fill="#1976D2", outline="#1976D2")
        canvas.create_oval(x2 - height, y1, x2, y1 + height, fill="#1976D2", outline="#1976D2")
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill="#1976D2", outline="#1976D2")

        button_text = canvas.create_text(x, y, text=text, font=("Helvetica", 14, "bold"), fill="white")

        def on_click(event):
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                command()

        canvas.tag_bind(button_text, "<Button-1>", on_click)

    draw_button(survey_canvas, 450, 400, 200, 50, "Next", submit_survey)

    # Footer
    survey_canvas.create_text(450, 570, text="© 2024 Singing Sculpture - All Rights Reserved", font=("Helvetica", 10), fill="#555555")


def create_questionnaire_page():
    """Create the questionnaire page."""
    questionnaire_window = Toplevel()
    questionnaire_window.title("Questionnaire Page")
    questionnaire_window.geometry("900x600")
    questionnaire_window.configure(bg="#E8F5FD")

    # Canvas for design
    questionnaire_canvas = Canvas(questionnaire_window, width=900, height=600, bg="#E8F5FD", highlightthickness=0)
    questionnaire_canvas.place(x=0, y=0)

    # Add rounded rectangle (white card)
    create_rounded_rectangle(questionnaire_canvas, 50, 50, 850, 550, radius=40, fill="#FFFFFF", outline="#FFFFFF")

    # Add title
    questionnaire_canvas.create_text(450, 100, text="Questionnaire", font=("Helvetica", 24, "bold"), fill="#333333")

    # Question data
    questions = [
        "Enjoyed the sculpture?",
        "Were curious as to how it worked?",
        "Wanted to know more about science as a result?",
    ]
    options = ["1. Strongly Agree", "2. Agree", "3. Neither Agree", "4. Disagree", "5. Strongly Disagree"]

    # Dictionary to store answers
    answers = {}

    # Render questions and options
    for i, question in enumerate(questions, start=1):
        tk.Label(
            questionnaire_window, text=f"{i}. {question}", font=("Helvetica", 12), bg="#FFFFFF", fg="#555555"
        ).place(x=70, y=140 + i * 60)

        var = tk.StringVar(value="")
        answers[f"q{i}"] = var
        for j, option in enumerate(options):
            tk.Radiobutton(
                questionnaire_window,
                text=option,
                variable=var,
                value=option,
                bg="#050708",
                font=("Helvetica", 10),
                anchor="w",
            ).place(x=150 + j * 120, y=140 + i * 60 + 30)

    def submit_questionnaire():
        """Handle submission of the questionnaire."""
        if any(not answer.get() for answer in answers.values()):
            messagebox.showerror("Error", "Please answer all questions before submitting.")
        else:
            messagebox.showinfo("Thank You!", "Your feedback has been submitted.")
            print("Survey Answers:")
            for question, answer in answers.items():
                print(f"{question}: {answer.get()}")
            store_survey_answers(answers)
            questionnaire_window.destroy()

    # Submit button (rounded style)
    def draw_button(canvas, x, y, width, height, text, command):
        """Draw a rounded button on the canvas."""
        radius = height // 2
        x1, y1, x2, y2 = x - width // 2, y - height // 2, x + width // 2, y + height // 2

        canvas.create_oval(x1, y1, x1 + height, y1 + height, fill="#1976D2", outline="#1976D2")
        canvas.create_oval(x2 - height, y1, x2, y1 + height, fill="#1976D2", outline="#1976D2")
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill="#1976D2", outline="#1976D2")

        button_text = canvas.create_text(x, y, text=text, font=("Helvetica", 14, "bold"), fill="white")

        def on_click(event):
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                command()

        canvas.tag_bind(button_text, "<Button-1>", on_click)

    draw_button(questionnaire_canvas, 450, 500, 200, 50, "Submit", submit_questionnaire)

    # Footer
    questionnaire_canvas.create_text(450, 570, text="© 2024 Singing Sculpture - All Rights Reserved", font=("Helvetica", 10), fill="#555555")


def open_survey_page():
    """Open the survey page window."""
    create_survey_page()


def store_data(name, age, sex, ethnicity, disabled, filename="viewers_data.json"):
    # Data to store
    new_entry = {
        "name": name,
        "age": age,
        "sex": sex,
        "ethnicity": ethnicity,
        "disabled": disabled,
    }

    # Check if the JSON file already exists
    if os.path.exists(filename):
        # If the file exists, load existing data
        with open(filename, "r") as file:
            data = json.load(file)
    else:
        # If the file doesn't exist, start with an empty list
        data = []

    # Append the new entry to the data
    data.append(new_entry)

    # Write the updated data back to the file
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Data stored successfully in {filename}")


# Function to load the last name from the data file
def get_last_name(filename="viewers_data.json"):
    # Check if the JSON file exists
    if os.path.exists(filename):
        with open(filename, "r") as file:
            data = json.load(file)
            # If data exists, return the last entry's name
            if data:
                return data[-1]["name"]
    return None


def store_survey_answers(answers, filename="survey_data.json"):
    # Get the last name from the data file
    last_name = get_last_name()

    if last_name:
        # Prepare the survey data with the last name
        survey_entry = {
            "name": last_name,
            "answers": {question: answer.get() for question, answer in answers.items()}  # Extract values
        }

        # Append the new survey entry directly to the JSON file
        try:
            # Open the file in append mode
            with open(filename, "a+") as file:
                # First, read any existing data
                file.seek(0)
                data = json.load(file) if file.tell() > 0 else []  # Handle empty file

                # Append the new survey entry
                data.append(survey_entry)

                # Write the updated data back to the file
                file.seek(0)
                json.dump(data, file, indent=4)

            print(f"Survey responses stored successfully in {filename}")
        except Exception as e:
            print(f"Error while storing survey responses: {e}")
    else:
        print("Error: Could not find the last entered name in the data.json file.")


def create_modern_landing_page():
    """Create a landing page similar to the reference image."""
    root = Tk()
    root.title("Software for Survey")
    root.geometry("1000x700")
    root.configure(bg="#E8F5FD")

    # Canvas for layout
    canvas = Canvas(root, bg="#E8F5FD", highlightthickness=0)
    canvas.pack(fill=BOTH, expand=True)

    def create_rounded_button(canvas, x, y, width, height, text, bg, fg, command):
        """Creates a rounded button on the canvas."""
        radius = height // 2
        x1, y1, x2, y2 = x - width // 2, y - height // 2, x + width // 2, y + height // 2

        # Draw rounded rectangle
        canvas.create_oval(x1, y1, x1 + height, y1 + height, fill=bg, outline=bg)  # Left circle
        canvas.create_oval(x2 - height, y1, x2, y1 + height, fill=bg, outline=bg)  # Right circle
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=bg, outline=bg)  # Center rectangle

        # Add button text
        button_text = canvas.create_text(
            x, y, text=text, font=("Helvetica", 14, "bold"), fill=fg
        )

        # Bind click event
        def on_click(event):
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                command()

        canvas.tag_bind(button_text, "<Button-1>", on_click)

    def resize_elements(event):
        canvas.delete("all")
        width, height = event.width, event.height

        # Background Shapes
        canvas.create_oval(-200, -200, 400, 400, fill="#A0E1F5", outline="")
        canvas.create_oval(width - 400, height - 300, width + 200, height + 200, fill="#A0E1F5", outline="")

        # Navigation Bar
        canvas.create_rectangle(0, 0, width, 70, fill="#1976D2", outline="")
        canvas.create_text(
            70, 35, text="Singing sculpture", font=("Helvetica", 20, "bold"), fill="white", anchor="w"
        )

        # Main Content Section
        canvas.create_text(
            30,
            height // 3 - 100,
            text="Survey for Sculpture",
            font=("Helvetica", 36, "bold"),
            fill="#333333",
            anchor="w",
        )
        canvas.create_text(
            30,
            height // 3 + 280,
            text=(
                "Discover the art of expression through our exclusive Sculpture Survey!"
                " Share your thoughts, preferences, and opinions on a diverse range of sculptures."
                " Your valuable insights will help us understand what captivates and inspires viewers like you."
                " Join us in shaping the future of art appreciation!"
            ),
            font=("Helvetica", 20),
            fill="#555555",
            anchor="w",
            width=400,
        )

        # Rounded Buttons
        create_rounded_button(
            canvas,
            x=120,
            y=height // 3 + 100,
            width=200,
            height=50,
            text="Start Survey",
            bg="#1976D2",
            fg="white",
            command=open_survey_page,
        )
        create_rounded_button(
            canvas,
            x=850,
            y=height // 3 - 200,
            width=200,
            height=50,
            text="Admin Login",
            bg="#E53935",
            fg="white",
            command=open_login_page,
        )

        # Illustration/Graphic
        try:
            illustration_path = "sculpture-removebg-preview.png"  # Replace with your image path
            illustration_image = Image.open(illustration_path)
            illustration_image = illustration_image.resize((400, 300), Image.ANTIALIAS)
            illustration_photo = ImageTk.PhotoImage(illustration_image)
            canvas.illustration_photo = illustration_photo  # Prevent garbage collection
            canvas.create_image(width - 250, height // 3, image=illustration_photo, anchor="center")
        except Exception:
            canvas.create_text(
                width - 350,
                height // 3,
                text="Illustration Placeholder",
                font=("Helvetica", 20, "bold"),
                fill="#CCCCCC",
            )

        # Footer
        canvas.create_text(
            width // 2,
            height - 20,
            text="© 2024 Singing Sculpture - All Rights Reserved",
            font=("Helvetica", 10),
            fill="#555555",
        )

    # Bind resize event
    canvas.bind("<Configure>", resize_elements)

    root.mainloop()


create_modern_landing_page()
