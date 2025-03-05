import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import csv
import pandas as pd
import os
import re
import requests
import time
from pathlib import Path
from PIL import Image, ImageTk  # Add PIL import for image handling

class CSVComparatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IMDB Werstreamt.es comparison tool")
        self.root.geometry("1200x700")
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), "tarpan.ico")
        if os.path.exists(icon_path):
            try:
                # Try to load icon using PIL
                icon = Image.open(icon_path)
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(icon)
                self.root.wm_iconphoto(True, photo)
            except Exception as e:
                print(f"Warning: Could not load icon: {e}")
        
        # Set theme - use the most modern looking theme available
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        
        # Configure styles
        style.configure('TButton', font=('Helvetica', 10), padding=6)
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('TLabelframe', font=('Helvetica', 10, 'bold'))
        style.configure('TLabelframe.Label', font=('Helvetica', 10, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Action.TButton', font=('Helvetica', 10, 'bold'))
        
        # Custom treeview styling
        style.configure("Treeview", 
                        background="#f8f8f8",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="#f8f8f8",
                        font=('Helvetica', 9))
        style.configure("Treeview.Heading", 
                        font=('Helvetica', 10, 'bold'),
                        background="#e0e0e0")
        style.map('Treeview', background=[('selected', '#3c7fb1')])
        
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.comparison_column = tk.StringVar()
        self.file1_data = None
        self.file2_data = None
        self.common_columns = []
        self.missing_entries = None
        
        # Set default file paths for the example files
        imdb_csv = os.path.join(os.getcwd(), "IMDB.csv")
        werstreamtes_csv = os.path.join(os.getcwd(), "Werstreamtes.csv")
        
        if os.path.exists(imdb_csv):
            self.file1_path.set(imdb_csv)
        
        if os.path.exists(werstreamtes_csv):
            self.file2_path.set(werstreamtes_csv)
        
        # Create main container with padding
        self.main_frame = ttk.Frame(root, padding="20 20 20 10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        # App title/header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="IMDB Werstreamt.es comparison tool", 
                  style='Header.TLabel', font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)
        
        # File selection frame
        file_frame = ttk.LabelFrame(self.main_frame, text="Select Files", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # File selection grid with better spacing
        file_frame.columnconfigure(1, weight=1)
        
        # File 1 selection (IMDB)
        ttk.Label(file_frame, text="IMDB Database:").grid(row=0, column=0, padx=(5, 10), pady=10, sticky=tk.W)
        entry1 = ttk.Entry(file_frame, textvariable=self.file1_path, width=70)
        entry1.grid(row=0, column=1, padx=5, pady=10, sticky=tk.EW)
        browse1_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_file1)
        browse1_btn.grid(row=0, column=2, padx=(5, 10), pady=10)
        
        # File 2 selection (Werstreamtes)
        ttk.Label(file_frame, text="Werstreamt.es Database:").grid(row=1, column=0, padx=(5, 10), pady=10, sticky=tk.W)
        entry2 = ttk.Entry(file_frame, textvariable=self.file2_path, width=70)
        entry2.grid(row=1, column=1, padx=5, pady=10, sticky=tk.EW)
        browse2_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_file2)
        browse2_btn.grid(row=1, column=2, padx=(5, 10), pady=10)
        
        # Action buttons in a card-like frame
        self.action_frame = ttk.Frame(self.main_frame, padding="10")
        self.action_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button container with centered alignment
        button_container = ttk.Frame(self.action_frame)
        button_container.pack(pady=5)
        
        load_btn = ttk.Button(button_container, text="Load & Compare Files", 
                              command=self.load_and_compare, style='Action.TButton', width=20)
        load_btn.pack(side=tk.LEFT, padx=10)
        
        export_btn = ttk.Button(button_container, text="Export Results", 
                                command=self.export_results, style='Action.TButton', width=15)
        export_btn.pack(side=tk.LEFT, padx=10)
        
        # Progress bar (hidden by default)
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', length=300)
        self.progress_bar.pack(fill=tk.X, padx=5)
        
        # Hide progress frame initially
        self.progress_frame.pack_forget()
        
        # Results section with a cleaner title and frame
        results_frame = ttk.LabelFrame(self.main_frame, text="Missing Movies", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create frame for the treeview and scrollbar
        treeview_frame = ttk.Frame(results_frame)
        treeview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for results with fixed columns
        self.results_treeview = ttk.Treeview(treeview_frame)
        self.results_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind click event for copying cell content
        self.results_treeview.bind('<Button-1>', self.copy_cell_content)
        
        # Create tooltip label for copy feedback
        self.tooltip = tk.Label(self.root, text="Copied!", 
                              background='#2e2e2e', foreground='white',
                              padx=10, pady=5, borderwidth=1, relief='solid')
        self.tooltip.place_forget()  # Hide initially
        
        # Create vertical scrollbar
        scrollbar_y = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.results_treeview.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create horizontal scrollbar
        scrollbar_x = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_treeview.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure treeview scrollbars
        self.results_treeview.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Status bar with modern styling
        status_frame = ttk.Frame(self.main_frame, padding=(0, 5, 0, 0))
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Status icon and text
        status_icon = ttk.Label(status_frame, text="•", font=('Helvetica', 16))
        status_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                              anchor=tk.W, padding=(0, 5))
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Load and compare files automatically if default files exist
        # Removed automatic comparison on startup
    
    def browse_file1(self):
        file_path = filedialog.askopenfilename(
            title="Select IMDB CSV File",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.file1_path.set(file_path)
    
    def browse_file2(self):
        file_path = filedialog.askopenfilename(
            title="Select Werstreamt.es CSV File",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.file2_path.set(file_path)
    
    def load_and_compare(self):
        """Load files and perform comparison."""
        if self.load_files():  # Only compare if files are loaded successfully
            self.compare_files()
    
    def load_files(self):
        """Load the CSV files and return True if successful."""
        # Check if both files are selected
        if not self.file1_path.get() or not self.file2_path.get():
            messagebox.showerror("Error", "Please select both CSV files.")
            return False
        
        try:
            # Load files using pandas
            self.file1_data = pd.read_csv(self.file1_path.get())
            self.file2_data = pd.read_csv(self.file2_path.get())
            
            # Update status
            f1_rows = len(self.file1_data)
            f2_rows = len(self.file2_data)
            self.status_var.set(f"Loaded IMDB.csv: {f1_rows} rows, Werstreamtes.csv: {f2_rows} rows")
            
            # Check if the required columns exist
            if 'Original Title' not in self.file1_data.columns or 'Title' not in self.file1_data.columns:
                messagebox.showerror("Error", "IMDB.csv must have 'Original Title' and 'Title' columns.")
                return False
                
            if 'OriginalTitle' not in self.file2_data.columns or 'Title' not in self.file2_data.columns:
                messagebox.showerror("Error", "Werstreamtes.csv must have 'OriginalTitle' and 'Title' columns.")
                return False
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading files: {str(e)}")
            return False
    
    def compare_files(self):
        if self.file1_data is None or self.file2_data is None:
            messagebox.showerror("Error", "Please load both files first.")
            return
        
        try:
            # Convert titles to lowercase for case-insensitive comparison
            imdb_original_titles = self.file1_data['Original Title'].str.lower()
            imdb_titles = self.file1_data['Title'].str.lower()
            werstreamtes_original_titles = self.file2_data['OriginalTitle'].str.lower()
            werstreamtes_titles = self.file2_data['Title'].str.lower()
            
            # Create a mask for entries that don't exist in werstreamtes
            missing_mask = ~(
                (imdb_original_titles.isin(werstreamtes_original_titles)) | 
                (imdb_original_titles.isin(werstreamtes_titles)) |
                (imdb_titles.isin(werstreamtes_original_titles)) | 
                (imdb_titles.isin(werstreamtes_titles))
            )
            
            # Get the missing entries
            self.missing_entries = self.file1_data[missing_mask].copy()
            
            # Update status with initial comparison results
            initial_missing_count = len(self.missing_entries)
            self.status_var.set(f"Found {initial_missing_count} potentially missing entries. Starting web verification...")
            
            # Extract IMDB ID from URL and verify only if we have missing entries
            if len(self.missing_entries) > 0 and 'URL' in self.missing_entries.columns:
                # Extract IMDB IDs first
                self.missing_entries['IMDB ID'] = self.missing_entries['URL'].apply(self.extract_imdb_id)
                
                # Only verify entries that have a valid IMDB ID
                entries_to_verify = self.missing_entries[self.missing_entries['IMDB ID'].str.len() > 0].copy()
                if len(entries_to_verify) > 0:
                    self.verify_missing_entries(entries_to_verify)
                else:
                    messagebox.showwarning("Warning", "No valid IMDB IDs found in the missing entries.")
            
            # Display results
            self.display_results(self.missing_entries)
            
            # Update final status
            missing_count = len(self.missing_entries)
            self.status_var.set(f"Found {missing_count} confirmed missing entries in IMDB.csv")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error comparing files: {str(e)}")
    
    def verify_missing_entries(self, entries_to_verify):
        """Verify missing entries by making web calls to Werstreamt.es."""
        try:
            total_entries = len(entries_to_verify)
            
            # Show progress bar and ensure it's visible
            self.progress_frame.pack(fill=tk.X, pady=(0, 15), after=self.action_frame)
            self.progress_bar['maximum'] = total_entries
            self.progress_bar['value'] = 0
            self.progress_label['text'] = f"Starting verification of {total_entries} entries..."
            self.root.update()
            
            # Create a mask for entries that are actually missing
            verified_missing_mask = pd.Series(False, index=self.missing_entries.index)
            
            for idx, row in entries_to_verify.iterrows():
                imdb_id = row['IMDB ID']
                is_missing = self.verify_entry(imdb_id)
                if is_missing:
                    verified_missing_mask[idx] = True
                
                # Update progress safely
                current_progress = entries_to_verify.index.get_loc(idx) + 1
                self.progress_bar['value'] = current_progress
                self.progress_label['text'] = f"Verifying entries... ({current_progress}/{total_entries})"
                self.root.update()
                
                # Add a small delay to avoid overwhelming the server
                time.sleep(0.05)
            
            # Filter out entries that were found on Werstreamt.es
            self.missing_entries = self.missing_entries[verified_missing_mask].copy()
            
            # Hide progress bar
            self.progress_frame.pack_forget()
            self.root.update()
            
        except Exception as e:
            print(f"Error verifying entries: {str(e)}")  # Debug print
            messagebox.showerror("Error", f"Error verifying entries: {str(e)}")
            self.progress_frame.pack_forget()
            self.root.update()
    
    def verify_entry(self, imdb_id):
        """Verify if an entry is missing from Werstreamt.es. Returns True if confirmed missing."""
        try:
            url = f"https://www.werstreamt.es/filme-serien/?q={imdb_id}"
            response = requests.get(url)
            print(f"Verifying entry {imdb_id}...")
            # Check for "no results" text
            return "Deine Suche lieferte leider keine Ergebnisse" in response.text
            
        except Exception as e:
            print(f"Error verifying entry {imdb_id}: {str(e)}")
            return False  # Consider it not missing if we can't verify
    
    def extract_imdb_id(self, url):
        """Extract the IMDB ID (format: tt followed by digits) from the URL."""
        if pd.isna(url):
            return ""
        
        # Use regex to find the pattern "tt" followed by digits
        match = re.search(r'(tt\d+)', url)
        if match:
            return match.group(1)
        return ""
    
    def display_results(self, data):
        # Clear previous data
        for i in self.results_treeview.get_children():
            self.results_treeview.delete(i)
        
        # If no data, show a message
        if len(data) == 0:
            self.status_var.set("No missing entries found")
            return
        
        # Select columns to display
        display_columns = ['IMDB ID', 'Title', 'Original Title', 'Year', 'IMDb Rating', 'Genres', 'URL']
        
        # Filter columns that exist in the data
        valid_columns = [col for col in display_columns if col in data.columns]
        
        # Configure columns
        self.results_treeview['columns'] = valid_columns
        self.results_treeview.column('#0', width=0, stretch=tk.NO)  # Hide the first column
        
        # Configure column headings
        for col in valid_columns:
            if col in ['Title', 'Original Title']:
                width = 200
            elif col == 'URL':
                width = 300
            elif col == 'IMDB ID':
                width = 100
            else:
                width = 100
            self.results_treeview.column(col, anchor="w", width=width)
            self.results_treeview.heading(col, text=col, anchor="w")
        
        # Alternating row colors
        for i, row in data.iterrows():
            # Format the values
            values = []
            for col in valid_columns:
                if pd.notna(row[col]):
                    # Format Year column as integer (no decimal places)
                    if col == 'Year':
                        values.append(int(row[col]))
                    else:
                        values.append(row[col])
                else:
                    values.append("")
            
            # Add alternating colors
            tag = 'even' if i % 2 == 0 else 'odd'
            self.results_treeview.insert('', 'end', values=values, tags=(tag,))
        
        # Configure row colors
        self.results_treeview.tag_configure('odd', background='#f5f5f5')
        self.results_treeview.tag_configure('even', background='#ffffff')
    
    def copy_cell_content(self, event):
        """Copy the content of the clicked cell to clipboard."""
        try:
            # Get the clicked item and column
            item_id = self.results_treeview.identify_row(event.y)
            column = self.results_treeview.identify_column(event.x)
            
            if not item_id or not column:
                return
            
            # Get column name from column number (e.g., '#1', '#2', etc.)
            column_num = int(column.replace('#', '')) - 1
            if column_num < 0:  # Clicked on the first hidden column
                return
                
            column_names = self.results_treeview['columns']
            if column_num >= len(column_names):
                return
                
            # Get the value from the cell
            value = self.results_treeview.item(item_id)['values'][column_num]
            if value:  # Only copy if there's content
                # Convert to string if it's not already
                value_str = str(value)
                
                # Copy to clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(value_str)
                self.root.update()  # Required for clipboard
                
                # Show tooltip near mouse cursor
                self.show_copy_tooltip(event.x_root, event.y_root, column_names[column_num])
        except Exception as e:
            print(f"Error copying cell content: {str(e)}")
    
    def show_copy_tooltip(self, x, y, column_name):
        """Show a tooltip indicating the content was copied."""
        # Hide any existing tooltip
        self.tooltip.place_forget()
        
        # Update tooltip text
        self.tooltip['text'] = f"{column_name} copied!"
        
        # Position tooltip near mouse cursor but slightly offset
        self.tooltip.place(x=x + 15, y=y - 30)
        
        # Schedule tooltip to disappear
        self.root.after(1500, self.tooltip.place_forget)
    
    def export_results(self):
        # Check if there's data to export
        if self.missing_entries is None or len(self.missing_entries) == 0:
            messagebox.showinfo("No Data", "There is no data to export.")
            return
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="missing_movies.csv",
            title="Export Missing Movies"
        )
        
        if not file_path:
            return
        
        try:
            # Export data to CSV
            self.missing_entries.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    # Set application icon (if available)
    try:
        root.iconbitmap("appicon.ico")
    except:
        pass
    app = CSVComparatorApp(root)
    root.mainloop()