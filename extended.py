import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import string
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import re
import numpy as np
import openpyxl
import xlrd
import sys


class TextAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text File Word Analyzer")
        try:
            icon_image = tk.PhotoImage(file="inf.png")
            self.root.iconphoto(True, icon_image)
        except:
            pass  # In case the icon isn't available
        self.root.geometry("1000x700")

        # Set of common connecting words to exclude
        self.connecting_words = {
            # English
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
            "by", "of", "from", "as", "if", "then", "than", "when", "where", "why", "how",
            "is", "are", "was", "were", "be", "been", "being", "this", "that", "these", "those",
            # Romanian
            "și", "sau", "dar", "în", "pe", "la", "cu", "de", "din", "ca", "dacă", "apoi",
            "decât", "când", "unde", "de ce", "cum", "este", "sunt", "a fost", "au fost",
            "fi", "fost", "fiind", "acest", "acel", "acești", "acei", "cel", "cea", "cei", "cele"
        }

        # Create the UI components
        self.create_widgets()

        # Adăugare gestiune pentru erorile de import excel
        self.excel_engine = None
        self.check_excel_support()

    def check_excel_support(self):
        """Verifică disponibilitatea modulelor pentru Excel și alege motorul potrivit"""
        try:
            import openpyxl
            self.excel_engine = 'openpyxl'
            self.status_bar.config(text="Suport Excel: openpyxl")
        except ImportError:
            try:
                import xlrd
                self.excel_engine = 'xlrd'
                self.status_bar.config(text="Suport Excel: xlrd (limitat la .xls)")
            except ImportError:
                self.excel_engine = None
                self.status_bar.config(
                    text="Avertisment: Nu s-a găsit suport pentru Excel. Instalați 'openpyxl' sau 'xlrd'.")

    def create_widgets(self):
        # Frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10, fill=tk.X)

        # Open file button
        self.open_button = tk.Button(
            button_frame,
            text="📂",  # Simbol Unicode pentru un folder
            command=self.open_file,
            width=2,  # Ajustează dimensiunile butonului
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12)
        )
        self.open_button.pack(side=tk.LEFT, padx=10)

        # Analyze button
        self.analyze_button = tk.Button(
            button_frame,
            text="🔍",
            command=self.analyze_content,
            width=2,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12),
            state=tk.DISABLED
        )
        self.analyze_button.pack(side=tk.LEFT, padx=10)

        # Generate graphs button
        self.graph_button = tk.Button(
            button_frame,
            text="📊",
            command=self.generate_graphs,
            width=2,
            height=2,
            bg="#FF9800",
            fg="white",
            font=("Arial", 12),
            state=tk.DISABLED
        )
        self.graph_button.pack(side=tk.LEFT, padx=10)

        # Clear button
        self.clear_button = tk.Button(
            button_frame,
            text="❌",
            command=self.clear_all,
            width=2,
            height=2,
            bg="#f44336",
            fg="white",
            font=("Arial", 12)
        )
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # Analysis Type Frame
        analysis_type_frame = tk.Frame(button_frame)
        analysis_type_frame.pack(side=tk.LEFT, padx=20)

        # Analysis Type Label
        analysis_type_label = tk.Label(
            analysis_type_frame,
            text="Tipul de Analiză:",
            font=("Arial", 10)
        )
        analysis_type_label.pack(side=tk.LEFT, padx=5)

        # Analysis Type Radio Buttons
        self.analysis_type = tk.StringVar(value="words")

        self.words_radio = tk.Radiobutton(
            analysis_type_frame,
            text="Cuvinte",
            variable=self.analysis_type,
            value="words",
            font=("Arial", 10)
        )
        self.words_radio.pack(side=tk.LEFT)

        self.numbers_radio = tk.Radiobutton(
            analysis_type_frame,
            text="Numere",
            variable=self.analysis_type,
            value="numbers",
            font=("Arial", 10)
        )
        self.numbers_radio.pack(side=tk.LEFT)

        self.letters_radio = tk.Radiobutton(
            analysis_type_frame,
            text="Litere",
            variable=self.analysis_type,
            value="letters",
            font=("Arial", 10)
        )
        self.letters_radio.pack(side=tk.LEFT)

        self.all_radio = tk.Radiobutton(
            analysis_type_frame,
            text="Toate",
            variable=self.analysis_type,
            value="all",
            font=("Arial", 10)
        )
        self.all_radio.pack(side=tk.LEFT)

        # Excel column frame - will be visible only for Excel files
        self.excel_frame = tk.Frame(self.root)

        # Excel column label
        excel_column_label = tk.Label(
            self.excel_frame,
            text="Selectați coloana Excel:",
            font=("Arial", 10)
        )
        excel_column_label.pack(side=tk.LEFT, padx=5)

        # Excel column combobox
        self.excel_column = tk.StringVar()
        self.excel_column_combo = ttk.Combobox(
            self.excel_frame,
            textvariable=self.excel_column,
            width=20
        )
        self.excel_column_combo.pack(side=tk.LEFT, padx=5)

        # Load columns button
        self.load_columns_button = tk.Button(
            self.excel_frame,
            text="Încarcă Coloanele",
            command=self.load_excel_columns,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10)
        )
        self.load_columns_button.pack(side=tk.LEFT, padx=5)

        # File info label
        self.file_label = tk.Label(self.root, text="Niciun fișier selectat", font=("Arial", 10))
        self.file_label.pack(pady=5, anchor=tk.W, padx=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab for content and statistics
        self.text_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.text_tab, text="Analiză Text")

        # Tab for graphs
        self.graph_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_tab, text="Grafice")

        # Middle frame for text content and statistics in text tab
        middle_frame = tk.Frame(self.text_tab)
        middle_frame.pack(fill=tk.BOTH, expand=True)

        # Frame for file content
        content_frame = tk.LabelFrame(middle_frame, text="Conținut Fișier", font=("Arial", 10, "bold"))
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Text area for file content
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for statistics
        stats_frame = tk.LabelFrame(middle_frame, text="Statistici", font=("Arial", 10, "bold"))
        stats_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Text area for statistics
        self.stats_text = scrolledtext.ScrolledText(stats_frame, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for charts in graph tab
        self.chart_frame = tk.Frame(self.graph_tab)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_bar = tk.Label(self.root, text="Gata", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Store the file content and analysis data
        self.file_content = ""
        self.file_path = ""
        self.sorted_items = []
        self.total_items = 0
        self.file_type = ""
        self.df = None  # For storing pandas DataFrame for CSV/Excel files

    def open_file(self):
        # Open file dialog
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All Supported Files", "*.txt *.csv *.xlsx *.xls"),
                ("Text Files", "*.txt"),
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx *.xls"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        self.file_path = file_path
        file_ext = os.path.splitext(file_path)[1].lower()

        try:
            if file_ext == '.txt':
                self.file_type = "text"
                with open(file_path, "r", encoding="utf-8") as file:
                    self.file_content = file.read()
                # Hide Excel column selection frame
                self.excel_frame.pack_forget()

            elif file_ext == '.csv':
                self.file_type = "csv"
                try:
                    self.df = pd.read_csv(file_path)
                    self.file_content = self.df.to_string()
                    # Hide Excel column selection frame
                    self.excel_frame.pack_forget()
                except Exception as e:
                    self.status_bar.config(text=f"Eroare la citirea CSV: {str(e)}")
                    messagebox.showwarning("Eroare CSV",
                                           f"Nu s-a putut citi fișierul CSV corect. Încerc să-l deschid ca text: {str(e)}")
                    # Încercăm să-l deschidem ca un fișier text normal
                    with open(file_path, "r", encoding="utf-8") as file:
                        self.file_content = file.read()

            elif file_ext in ['.xlsx', '.xls']:
                self.file_type = "excel"

                # Verificăm dacă avem suport pentru Excel
                if self.excel_engine is None:
                    messagebox.showerror("Lipsă Suport Excel",
                                         "Nu s-a găsit suport pentru fișierele Excel. Instalați bibliotecile 'openpyxl' sau 'xlrd'.")
                    self.status_bar.config(text="Eroare: Lipsă suport Excel.")
                    return

                # Verificăm compatibilitatea formatului cu motorul disponibil
                if file_ext == '.xlsx' and self.excel_engine == 'xlrd':
                    messagebox.showwarning("Incompatibilitate",
                                           "Fișierul .xlsx nu poate fi deschis cu motorul disponibil (xlrd). Instalați 'openpyxl'.")
                    self.status_bar.config(text="Eroare: Fișier .xlsx incompatibil cu xlrd.")
                    return

                try:
                    self.df = pd.read_excel(file_path, engine=self.excel_engine)
                    self.file_content = "Fișier Excel încărcat. Folosiți 'Încarcă Coloanele' pentru a selecta o coloană."

                    # Show Excel column selection frame
                    self.excel_frame.pack(pady=5, fill=tk.X, padx=10, before=self.file_label)

                    # Populate the column combobox
                    self.excel_column_combo['values'] = list(self.df.columns)
                    if len(self.df.columns) > 0:
                        self.excel_column.set(self.df.columns[0])

                except Exception as e:
                    error_msg = str(e)
                    messagebox.showerror("Eroare Excel", f"Nu s-a putut deschide fișierul Excel: {error_msg}")
                    self.status_bar.config(text=f"Eroare: {error_msg}")
                    return

            # Update UI
            self.file_label.config(text=f"Fișier: {os.path.basename(file_path)}")
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, self.file_content)
            self.analyze_button.config(state=tk.NORMAL)
            self.status_bar.config(text=f"Fișier încărcat: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-a putut deschide fișierul: {str(e)}")
            self.status_bar.config(text=f"Eroare: {str(e)}")

    def load_excel_columns(self):
        if self.file_type != "excel" or self.df is None:
            self.status_bar.config(text="Niciun fișier Excel încărcat")
            return

        selected_column = self.excel_column.get()
        if not selected_column:
            self.status_bar.config(text="Nicio coloană selectată")
            return

        try:
            column_data = self.df[selected_column].to_string()
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, column_data)
            self.file_content = column_data
            self.status_bar.config(text=f"Coloana '{selected_column}' încărcată")
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-a putut încărca coloana: {str(e)}")
            self.status_bar.config(text=f"Eroare: {str(e)}")

    def analyze_content(self):
        if not self.file_content:
            self.status_bar.config(text="Niciun conținut de analizat")
            return

        # Clear previous stats
        self.stats_text.delete(1.0, tk.END)

        # Process the text based on analysis type
        self.status_bar.config(text="Analizez conținutul...")

        analysis_type = self.analysis_type.get()

        if analysis_type == "words":
            self.analyze_words()
        elif analysis_type == "numbers":
            self.analyze_numbers()
        elif analysis_type == "letters":
            self.analyze_letters()
        elif analysis_type == "all":
            self.analyze_all()

        # Enable graph button
        self.graph_button.config(state=tk.NORMAL)

    def analyze_words(self):
        # Remove punctuation and convert to lowercase
        translator = str.maketrans('', '', string.punctuation)
        clean_text = self.file_content.translate(translator).lower()

        # Split into words
        words = clean_text.split()

        # Count words excluding connecting words
        word_count = {}
        self.total_items = 0

        for word in words:
            if word not in self.connecting_words and len(word) > 1:  # Exclude single letters too
                self.total_items += 1
                if word in word_count:
                    word_count[word] += 1
                else:
                    word_count[word] = 1

        # Sort by frequency (descending)
        self.sorted_items = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

        # Display the statistics
        self.stats_text.insert(tk.END, f"Total Cuvinte: {len(words)}\n")
        self.stats_text.insert(tk.END, f"Cuvinte Semnificative: {self.total_items}\n\n")
        self.stats_text.insert(tk.END, "Statistici Frecvență Cuvinte:\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")
        self.stats_text.insert(tk.END, "Cuvânt\t\tNumăr\t\tProcentaj\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")

        for word, count in self.sorted_items:
            percentage = (count / self.total_items) * 100
            self.stats_text.insert(tk.END, f"{word}\t\t{count}\t\t{percentage:.2f}%\n")

        self.status_bar.config(text="Analiză cuvinte completă")

    def analyze_numbers(self):
        # Extract numbers from text
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', self.file_content)

        # Count number occurrences
        number_count = {}
        self.total_items = len(numbers)

        for number in numbers:
            if number in number_count:
                number_count[number] += 1
            else:
                number_count[number] = 1

        # Sort by frequency
        self.sorted_items = sorted(number_count.items(), key=lambda x: x[1], reverse=True)

        # Display statistics
        self.stats_text.insert(tk.END, f"Total Numere: {self.total_items}\n\n")
        self.stats_text.insert(tk.END, "Statistici Frecvență Numere:\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")
        self.stats_text.insert(tk.END, "Număr\t\tApariții\t\tProcentaj\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")

        for number, count in self.sorted_items:
            percentage = (count / self.total_items) * 100
            self.stats_text.insert(tk.END, f"{number}\t\t{count}\t\t{percentage:.2f}%\n")

        self.status_bar.config(text="Analiză numere completă")

    def analyze_letters(self):
        # Extract only letters from text and convert to lowercase
        letters = re.findall(r'[a-zA-Z]', self.file_content.lower())

        # Count letter occurrences
        letter_count = {}
        self.total_items = len(letters)

        for letter in letters:
            if letter in letter_count:
                letter_count[letter] += 1
            else:
                letter_count[letter] = 1

        # Sort by frequency
        self.sorted_items = sorted(letter_count.items(), key=lambda x: x[1], reverse=True)

        # Display statistics
        self.stats_text.insert(tk.END, f"Total Litere: {self.total_items}\n\n")
        self.stats_text.insert(tk.END, "Statistici Frecvență Litere:\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")
        self.stats_text.insert(tk.END, "Literă\t\tApariții\t\tProcentaj\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")

        for letter, count in self.sorted_items:
            percentage = (count / self.total_items) * 100
            self.stats_text.insert(tk.END, f"{letter}\t\t{count}\t\t{percentage:.2f}%\n")

        self.status_bar.config(text="Analiză litere completă")

    def analyze_all(self):
        # Extract all characters from text
        chars = [c for c in self.file_content.lower() if c.isalnum()]

        # Count character occurrences
        char_count = {}
        self.total_items = len(chars)

        for char in chars:
            if char in char_count:
                char_count[char] += 1
            else:
                char_count[char] = 1

        # Sort by frequency
        self.sorted_items = sorted(char_count.items(), key=lambda x: x[1], reverse=True)

        # Display statistics
        self.stats_text.insert(tk.END, f"Total Caractere: {self.total_items}\n\n")
        self.stats_text.insert(tk.END, "Statistici Frecvență Caractere:\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")
        self.stats_text.insert(tk.END, "Caracter\t\tApariții\t\tProcentaj\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")

        for char, count in self.sorted_items:
            percentage = (count / self.total_items) * 100
            self.stats_text.insert(tk.END, f"{char}\t\t{count}\t\t{percentage:.2f}%\n")

        self.status_bar.config(text="Analiză completă a tuturor caracterelor")

    def generate_graphs(self):
        if not self.sorted_items:
            self.status_bar.config(text="Nu există date pentru generarea graficelor")
            return

        # Clear previous graphs
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Create a figure for both charts
        fig = plt.figure(figsize=(10, 8))

        # Get the type of item being analyzed
        analysis_type = self.analysis_type.get()
        if analysis_type == "words":
            item_type = "Cuvinte"
        elif analysis_type == "numbers":
            item_type = "Numere"
        elif analysis_type == "letters":
            item_type = "Litere"
        else:
            item_type = "Caractere"

        # Limit to top items for clarity (more for letters since there are fewer)
        top_limit = 10 if analysis_type != "letters" else 20
        top_items = self.sorted_items[:min(top_limit, len(self.sorted_items))]

        # Create pie chart
        ax1 = fig.add_subplot(211)

        # FIX pentru etichetele suprapuse
        labels = [item for item, _ in top_items]
        sizes = [count for _, count in top_items]

        # Adăugăm procente la etichete pentru identificare ușoară
        total = sum(sizes)
        labels_with_pct = [f"{labels[i]} ({sizes[i] / total * 100:.1f}%)" for i in range(len(labels))]

        # Create color map
        colors = plt.cm.Blues([(i + 1) / (len(labels) + 1) for i in range(len(labels))])

        # Prag minim pentru a grupa valorile foarte mici
        prag_minim = 0.02  # 2%

        # Grupăm valorile foarte mici într-o singură felie "Altele"
        sizes_noi = []
        labels_noi = []
        colors_noi = []
        suma_mici = 0

        for i, size in enumerate(sizes):
            if size / total >= prag_minim:
                sizes_noi.append(size)
                labels_noi.append(labels[i])
                colors_noi.append(colors[i])
            else:
                suma_mici += size

        # Adăugăm categoria "Altele" dacă există valori mici
        if suma_mici > 0:
            sizes_noi.append(suma_mici)
            labels_noi.append("Altele")
            colors_noi.append("gray")  # Culoare pentru "Altele"

        # Creăm graficul pie cu valorile ajustate
        wedges, texts = ax1.pie(
            sizes_noi,
            labels=None,  # Eliminăm etichetele directe
            startangle=90,
            colors=colors_noi,
            wedgeprops={'edgecolor': 'w', 'linewidth': 1},
            explode=[0.05] * len(sizes_noi)  # Dispersare ușoară
        )

        # Adăugăm o legendă în afara graficului
        ax1.legend(
            wedges,
            labels_with_pct,
            title=f"Top {min(top_limit, len(self.sorted_items))} {item_type}",
            loc="center left",
            bbox_to_anchor=(1, 0.5)  # Poziționăm legenda în dreapta graficului
        )

        # Ajustăm layout-ul pentru a face loc legendei și titlului
        plt.tight_layout()
        plt.subplots_adjust(top=0.9, right=0.75)  # Spațiu pentru titlu și legendă

        # Adăugăm procentele pentru fiecare felie, chiar și pentru cele foarte mici
        text_positions = []  # Listă pentru a stoca pozițiile textelor

        for i, wedge in enumerate(wedges):
            angle = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1  # Unghiul de mijloc al feliei
            x = 1.3 * np.cos(np.deg2rad(angle))  # Coordonata x în afara graficului
            y = 1.3 * np.sin(np.deg2rad(angle))  # Coordonata y în afara graficului

            # Verificăm dacă textul se suprapune cu alte texte
            overlap = False
            for pos in text_positions:
                if np.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2) < 0.2:  # Distanță minimă între texte
                    overlap = True
                    break

            if overlap:
                # Dacă se suprapune, ajustăm poziția
                x = 1.5 * np.cos(np.deg2rad(angle))  # Mărim distanța
                y = 1.5 * np.sin(np.deg2rad(angle))

            # Adăugăm textul procentului
            ax1.annotate(
                f"{sizes[i] / total * 100:.1f}%",
                xy=(np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))),  # Punctul de conectare pe felie
                xytext=(x, y),  # Poziția textului în afara graficului
                arrowprops=dict(
                    arrowstyle="->",
                    connectionstyle="arc3,rad=0.1",
                    color=colors[i]  # Săgeata are culoarea feliei respective
                ),
                ha='center',  # Aliniere orizontală
                va='center'  # Aliniere verticală
            )

            # Adăugăm poziția textului în listă
            text_positions.append((x, y))

        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        ax1.set_title(f'Top {min(top_limit, len(self.sorted_items))} {item_type} - Distribuție',
                      y=1.25)  # Mutăm titlul mai sus

        # Create bar chart
        ax2 = fig.add_subplot(212)

        # Limitarea numărului de bare pentru claritate
        display_limit = min(10, len(top_items))
        items = [item for item, _ in top_items[:display_limit]]
        frequencies = [count / self.total_items for _, count in top_items[:display_limit]]

        # Create bar chart
        bars = ax2.bar(items, frequencies, color=plt.cm.Blues(0.6))

        # Add values on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.2f}', ha='center', va='bottom')

        ax2.set_title(f'Frecvențe {item_type}')
        ax2.set_xlabel(f'{item_type}')
        ax2.set_ylabel('Frecvență')

        # Rotate x-axis labels for better readability if needed
        plt.xticks(rotation=45, ha='right')

        # Adjust layout - mai multă atenție la spațiul pentru legendă
        plt.tight_layout()
        plt.subplots_adjust(right=0.75)  # Spațiu pentru legendă

        # Embed the graphs in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Switch to the graph tab
        self.notebook.select(self.graph_tab)

        self.status_bar.config(text="Grafice generate")
    def clear_all(self):
        self.content_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        self.file_label.config(text="Niciun fișier selectat")
        self.file_content = ""
        self.file_path = ""
        self.sorted_items = []
        self.total_items = 0
        self.analyze_button.config(state=tk.DISABLED)
        self.graph_button.config(state=tk.DISABLED)
        self.file_type = ""
        self.df = None

        # Hide Excel column selection frame
        self.excel_frame.pack_forget()

        # Clear graphs
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        self.status_bar.config(text="Gata")


if __name__ == "__main__":
    root = tk.Tk()
    app = TextAnalyzerApp(root)
    root.mainloop()


