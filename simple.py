import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import string
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TextAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text File Word Analyzer")
        icon_image = tk.PhotoImage(file="inf.png")
        self.root.iconphoto(True, icon_image)
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
            command=self.analyze_text,
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

        # File info label
        self.file_label = tk.Label(self.root, text="No file selected", font=("Arial", 10))
        self.file_label.pack(pady=5, anchor=tk.W, padx=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab for content and statistics
        self.text_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.text_tab, text="Text Analysis")

        # Tab for graphs
        self.graph_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_tab, text="Charts")

        # Middle frame for text content and statistics in text tab
        middle_frame = tk.Frame(self.text_tab)
        middle_frame.pack(fill=tk.BOTH, expand=True)

        # Frame for file content
        content_frame = tk.LabelFrame(middle_frame, text="File Content", font=("Arial", 10, "bold"))
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Text area for file content
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for statistics
        stats_frame = tk.LabelFrame(middle_frame, text="Word Statistics", font=("Arial", 10, "bold"))
        stats_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Text area for statistics
        self.stats_text = scrolledtext.ScrolledText(stats_frame, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for charts in graph tab
        self.chart_frame = tk.Frame(self.graph_tab)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Store the file content and analysis data
        self.file_content = ""
        self.file_path = ""
        self.sorted_words = []
        self.total_meaningful_words = 0

    def open_file(self):
        # Open file dialog
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.file_content = file.read()

                self.file_path = file_path
                self.file_label.config(text=f"File: {os.path.basename(file_path)}")
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, self.file_content)
                self.analyze_button.config(state=tk.NORMAL)
                self.status_bar.config(text=f"File loaded: {os.path.basename(file_path)}")
            except Exception as e:
                self.status_bar.config(text=f"Error: {str(e)}")

    def analyze_text(self):
        if not self.file_content:
            self.status_bar.config(text="No file content to analyze")
            return

        # Clear previous stats
        self.stats_text.delete(1.0, tk.END)

        # Process the text
        self.status_bar.config(text="Analyzing text...")

        # Remove punctuation and convert to lowercase
        translator = str.maketrans('', '', string.punctuation)
        clean_text = self.file_content.translate(translator).lower()

        # Split into words
        words = clean_text.split()

        # Count words excluding connecting words
        word_count = {}
        self.total_meaningful_words = 0

        for word in words:
            if word not in self.connecting_words and len(word) > 1:  # Exclude single letters too
                self.total_meaningful_words += 1
                if word in word_count:
                    word_count[word] += 1
                else:
                    word_count[word] = 1

        # Sort by frequency (descending)
        self.sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

        # Display the statistics
        self.stats_text.insert(tk.END, f"Total Words: {len(words)}\n")
        self.stats_text.insert(tk.END, f"Meaningful Words: {self.total_meaningful_words}\n\n")
        self.stats_text.insert(tk.END, "Word Frequency Statistics:\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")
        self.stats_text.insert(tk.END, "Word\t\tCount\t\tPercentage\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")

        for word, count in self.sorted_words:
            percentage = (count / self.total_meaningful_words) * 100
            self.stats_text.insert(tk.END, f"{word}\t\t{count}\t\t{percentage:.2f}%\n")

        self.status_bar.config(text="Analysis complete")

        # Enable graph button
        self.graph_button.config(state=tk.NORMAL)

    def generate_graphs(self):
        if not self.sorted_words:
            self.status_bar.config(text="No data to generate graphs")
            return

        # Clear previous graphs
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Create a figure for both charts
        fig = plt.figure(figsize=(10, 8))

        # Create pie chart - top 6 words
        ax1 = fig.add_subplot(211)

        # Get top 6 words for pie chart
        top_words = self.sorted_words[:6]
        labels = [word for word, _ in top_words]
        sizes = [count for _, count in top_words]

        # Create pie chart
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                colors=['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#FF6D01', '#46BDC6'])
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        ax1.set_title('Top 6 Words Distribution')

        # Create bar chart - top 6 words frequencies
        ax2 = fig.add_subplot(212)

        words = [word for word, _ in top_words]
        frequencies = [count / self.total_meaningful_words for _, count in top_words]

        # Create bar chart
        bars = ax2.bar(words, frequencies, color='#34A853')

        # Add some values on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.2f}', ha='center', va='bottom')

        ax2.set_title('Word Frequencies')
        ax2.set_xlabel('Words')
        ax2.set_ylabel('Frequency')

        # Adjust layout
        plt.tight_layout()

        # Embed the graphs in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Switch to the graph tab
        self.notebook.select(self.graph_tab)

        self.status_bar.config(text="Graphs generated")

    def clear_all(self):
        self.content_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        self.file_label.config(text="No file selected")
        self.file_content = ""
        self.file_path = ""
        self.sorted_words = []
        self.total_meaningful_words = 0
        self.analyze_button.config(state=tk.DISABLED)
        self.graph_button.config(state=tk.DISABLED)

        # Clear graphs
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        self.status_bar.config(text="Ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = TextAnalyzerApp(root)
    root.mainloop()
