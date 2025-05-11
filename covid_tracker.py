import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import seaborn as sns
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")

class CovidDataTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("COVID-19 Global Data Tracker")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        # Load data
        try:
            self.df = pd.read_csv("owid_covid_data.csv")
            # Convert date column to datetime
            self.df['date'] = pd.to_datetime(self.df['date'])
            # Get list of countries (excluding continents and income groups)
            self.countries = sorted(self.df[~self.df['iso_code'].str.contains('OWID_', na=False)]['location'].unique())
            self.setup_ui()
        except FileNotFoundError:
            tk.Label(
                root, 
                text="Error: 'owid_covid_data.csv' file not found.\nPlease download it from https://covid.ourworldindata.org/data/owid-covid-data.csv",
                fg="red",
                bg="#f0f0f0",
                font=("Arial", 14)
            ).pack(pady=50)
        except Exception as e:
            tk.Label(
                root, 
                text=f"Error loading data: {str(e)}",
                fg="red",
                bg="#f0f0f0",
                font=("Arial", 14)
            ).pack(pady=50)

    def setup_ui(self):
        # Create frame for controls
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # Title
        title_label = tk.Label(
            control_frame, 
            text="COVID-19 Global Data Tracker",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0"
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=10, sticky="w")
        
        # Country selection
        country_label = tk.Label(control_frame, text="Country:", bg="#f0f0f0", font=("Arial", 12))
        country_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.country_var = tk.StringVar(value="World")
        self.country_dropdown = ttk.Combobox(
            control_frame, 
            textvariable=self.country_var,
            values=["World"] + self.countries,
            width=30,
            font=("Arial", 12)
        )
        self.country_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Metric selection
        metric_label = tk.Label(control_frame, text="Metric:", bg="#f0f0f0", font=("Arial", 12))
        metric_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        self.metrics = [
            "total_cases", "new_cases", 
            "total_deaths", "new_deaths",
            "total_cases_per_million", "new_cases_per_million",
            "total_deaths_per_million", "new_deaths_per_million",
            "icu_patients", "hosp_patients", 
            "total_vaccinations", "people_vaccinated",
            "people_fully_vaccinated", "total_boosters",
            "reproduction_rate"
        ]
        
        self.metric_var = tk.StringVar(value="total_cases")
        self.metric_dropdown = ttk.Combobox(
            control_frame, 
            textvariable=self.metric_var,
            values=self.metrics,
            width=30,
            font=("Arial", 12)
        )
        self.metric_dropdown.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Compare countries checkbox
        self.compare_var = tk.BooleanVar(value=False)
        compare_check = tk.Checkbutton(
            control_frame, 
            text="Compare Top Countries", 
            variable=self.compare_var,
            bg="#f0f0f0",
            font=("Arial", 12)
        )
        compare_check.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        # Add buttons for different analyses
        button_frame = tk.Frame(control_frame, bg="#f0f0f0")
        button_frame.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        
        update_button = tk.Button(button_frame, text="Update Graph", command=self.update_graph, font=("Arial", 12))
        update_button.pack(side=tk.LEFT, padx=5)
        
        global_stats_button = tk.Button(button_frame, text="Global Stats", command=self.show_global_stats, font=("Arial", 12))
        global_stats_button.pack(side=tk.LEFT, padx=5)
        
        country_stats_button = tk.Button(button_frame, text="Country Stats", command=self.show_country_stats, font=("Arial", 12))
        country_stats_button.pack(side=tk.LEFT, padx=5)
        
        vaccination_button = tk.Button(button_frame, text="Vaccination Progress", command=self.show_vaccination_data, font=("Arial", 12))
        vaccination_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the plot
        self.plot_frame = tk.Frame(self.root, bg="white")
        self.plot_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Bind events
        self.country_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_graph())
        self.metric_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_graph())
        self.compare_var.trace("w", lambda *args: self.update_graph())
        
        # Initialize with default graph
        self.fig = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            font=("Arial", 10)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load initial graph
        self.update_graph()

    def get_country_data(self, country, metric):
        """Get data for a specific country and metric."""
        if country == "World":
            data = self.df[self.df['iso_code'] == 'OWID_WRL'].copy()
        else:
            data = self.df[self.df['location'] == country].copy()
        
        # Filter out rows where the metric is NaN
        data = data[['date', metric]].dropna(subset=[metric])
        
        # Replace metric name for better display
        readable_metric = metric.replace('_', ' ').title()
        
        return data, readable_metric

    def update_graph(self):
        """Update the graph based on current selections."""
        try:
            self.status_var.set("Loading data...")
            self.root.update_idletasks()
            
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            
            country = self.country_var.get()
            metric = self.metric_var.get()
            
            if self.compare_var.get():
                # Compare top countries
                self.plot_top_countries(ax, metric)
            else:
                # Plot single country data
                country_data, readable_metric = self.get_country_data(country, metric)
                
                if not country_data.empty:
                    ax.plot(country_data['date'], country_data[metric], linewidth=2, marker='', color='#3498db')
                    ax.set_title(f"{readable_metric} in {country}", fontsize=16)
                    ax.set_xlabel("Date", fontsize=12)
                    ax.set_ylabel(readable_metric, fontsize=12)
                    
                    # Format the date axis
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
                    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                    
                    # Add grid
                    ax.grid(True, linestyle='--', alpha=0.7)
                    
                    # Add a slight smoothing for visual appeal
                    if len(country_data) > 30:
                        window_size = min(7, len(country_data) // 10)
                        rolling_avg = country_data[metric].rolling(window=window_size).mean()
                        ax.plot(country_data['date'], rolling_avg, linewidth=3, color='#e74c3c', 
                                label=f"{window_size}-day Moving Average")
                        ax.legend()
                else:
                    ax.text(0.5, 0.5, f"No data available for {metric} in {country}", 
                            ha='center', va='center', transform=ax.transAxes, fontsize=14)
            
            self.fig.tight_layout()
            self.canvas.draw()
            self.status_var.set(f"Displaying data for: {country} - {metric.replace('_', ' ').title()}")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def plot_top_countries(self, ax, metric):
        """Plot comparison of top countries for the given metric."""
        try:
            # Get the latest date with good data coverage
            latest_dates = self.df.groupby('location')['date'].max().reset_index()
            common_date = latest_dates['date'].value_counts().idxmax()
            
            # Get data for the latest date
            latest_data = self.df[self.df['date'] == common_date].copy()
            
            # Filter out continents and World
            latest_data = latest_data[~latest_data['iso_code'].str.contains('OWID_', na=False)]
            
            # Sort by the metric and get top 10 countries
            latest_data = latest_data.sort_values(by=metric, ascending=False).head(10)
            
            if not latest_data.empty:
                # Create bar plot
                bars = ax.barh(latest_data['location'], latest_data[metric], color=sns.color_palette("viridis", 10))
                
                # Add values at the end of bars
                for bar in bars:
                    width = bar.get_width()
                    label_x_pos = width if width > 0 else 0
                    ax.text(label_x_pos + (max(latest_data[metric]) * 0.01), 
                            bar.get_y() + bar.get_height()/2, 
                            f'{width:,.0f}', 
                            va='center')
                
                ax.set_title(f"Top 10 Countries by {metric.replace('_', ' ').title()}", fontsize=16)
                ax.set_xlabel(metric.replace('_', ' ').title(), fontsize=12)
                ax.invert_yaxis()  # To have highest value at the top
                ax.grid(True, linestyle='--', alpha=0.7, axis='x')
            else:
                ax.text(0.5, 0.5, f"No data available for {metric}", 
                        ha='center', va='center', transform=ax.transAxes, fontsize=14)
                
        except Exception as e:
            ax.text(0.5, 0.5, f"Error creating comparison: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes, fontsize=14)

    def show_global_stats(self):
        """Show global statistics window."""
        try:
            # Get the latest global data
            world_data = self.df[self.df['iso_code'] == 'OWID_WRL'].sort_values('date').tail(1)
            
            if world_data.empty:
                messagebox.showinfo("Info", "No global data available")
                return
                
            # Create a new window
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Global COVID-19 Statistics")
            stats_window.geometry("600x500")
            stats_window.configure(bg="#f0f0f0")
            
            # Title
            tk.Label(
                stats_window, 
                text="Global COVID-19 Statistics",
                font=("Arial", 16, "bold"),
                bg="#f0f0f0"
            ).pack(pady=10)
            
            # Date info
            latest_date = world_data['date'].iloc[0].strftime("%B %d, %Y")
            tk.Label(
                stats_window, 
                text=f"Latest data as of: {latest_date}",
                font=("Arial", 12),
                bg="#f0f0f0"
            ).pack(pady=5)
            
            # Create a frame for stats
            stats_frame = tk.Frame(stats_window, bg="#f0f0f0")
            stats_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Define key metrics to display
            key_metrics = [
                ("Total Cases", "total_cases"),
                ("Total Deaths", "total_deaths"),
                ("Cases per Million", "total_cases_per_million"),
                ("Deaths per Million", "total_deaths_per_million"),
                ("Total Vaccinations", "total_vaccinations"),
                ("People Fully Vaccinated", "people_fully_vaccinated"),
                ("Current Reproduction Rate", "reproduction_rate")
            ]
            
            # Display metrics
            for i, (label, column) in enumerate(key_metrics):
                try:
                    value = world_data[column].iloc[0]
                    if pd.isna(value):
                        formatted_value = "Data not available"
                    elif column.endswith("_rate"):
                        formatted_value = f"{value:.2f}"
                    elif "total" in column or "people" in column:
                        formatted_value = f"{value:,.0f}"
                    else:
                        formatted_value = f"{value:,.2f}"
                except:
                    formatted_value = "Data not available"
                
                frame = tk.Frame(stats_frame, bg="#f0f0f0")
                frame.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="nsew")
                
                tk.Label(
                    frame, 
                    text=label,
                    font=("Arial", 12, "bold"),
                    bg="#f0f0f0"
                ).pack(anchor="w")
                
                tk.Label(
                    frame, 
                    text=formatted_value,
                    font=("Arial", 14),
                    fg="#2980b9",
                    bg="#f0f0f0"
                ).pack(anchor="w", pady=5)
            
            # Configure grid
            stats_frame.grid_columnconfigure(0, weight=1)
            stats_frame.grid_columnconfigure(1, weight=1)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_country_stats(self):
        """Show detailed statistics for selected country."""
        try:
            country = self.country_var.get()
            
            if country == "World":
                country_data = self.df[self.df['iso_code'] == 'OWID_WRL'].copy()
            else:
                country_data = self.df[self.df['location'] == country].copy()
                
            if country_data.empty:
                messagebox.showinfo("Info", f"No data available for {country}")
                return
                
            # Get latest data
            latest_data = country_data.sort_values('date').tail(1)
            
            # Create a new window
            stats_window = tk.Toplevel(self.root)
            stats_window.title(f"COVID-19 Statistics for {country}")
            stats_window.geometry("700x600")
            stats_window.configure(bg="#f0f0f0")
            
            # Title
            tk.Label(
                stats_window, 
                text=f"COVID-19 Statistics for {country}",
                font=("Arial", 16, "bold"),
                bg="#f0f0f0"
            ).pack(pady=10)
            
            # Date info
            latest_date = latest_data['date'].iloc[0].strftime("%B %d, %Y")
            tk.Label(
                stats_window, 
                text=f"Latest data as of: {latest_date}",
                font=("Arial", 12),
                bg="#f0f0f0"
            ).pack(pady=5)
            
            # Create notebook (tabbed interface)
            notebook = ttk.Notebook(stats_window)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Current stats tab
            current_tab = tk.Frame(notebook, bg="#f0f0f0")
            notebook.add(current_tab, text="Current Stats")
            
            # Trends tab
            trends_tab = tk.Frame(notebook, bg="#f0f0f0")
            notebook.add(trends_tab, text="Trends")
            
            # Population tab (if data available)
            if not pd.isna(latest_data['population'].iloc[0]):
                population_tab = tk.Frame(notebook, bg="#f0f0f0")
                notebook.add(population_tab, text="Population Data")
                
                # Add population info
                self.add_population_info(population_tab, latest_data)
            
            # Fill current stats tab
            self.fill_current_stats(current_tab, latest_data)
            
            # Fill trends tab
            self.fill_trends_tab(trends_tab, country_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def fill_current_stats(self, tab, data):
        """Fill the current stats tab with data."""
        # Create scrollable frame
        canvas = tk.Canvas(tab, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Define sections and metrics
        sections = [
            ("Cases", ["total_cases", "new_cases", "total_cases_per_million", "new_cases_per_million"]),
            ("Deaths", ["total_deaths", "new_deaths", "total_deaths_per_million", "new_deaths_per_million"]),
            ("Hospitalizations", ["icu_patients", "hosp_patients", "icu_patients_per_million", "hosp_patients_per_million"]),
            ("Testing", ["total_tests", "new_tests", "positive_rate", "tests_per_case"]),
            ("Vaccinations", ["total_vaccinations", "people_vaccinated", "people_fully_vaccinated", "total_boosters"])
        ]
        
        # Add metrics by section
        row = 0
        for section_name, metrics in sections:
            # Section header
            tk.Label(
                scrollable_frame,
                text=section_name,
                font=("Arial", 14, "bold"),
                bg="#f0f0f0"
            ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
            row += 1
            
            # Metrics
            has_data = False
            for metric in metrics:
                if metric in data.columns:
                    value = data[metric].iloc[0]
                    if not pd.isna(value):
                        has_data = True
                        if "per_" in metric or "_rate" in metric or "_per_" in metric:
                            formatted_value = f"{value:.2f}"
                        else:
                            formatted_value = f"{value:,.0f}"
                            
                        # Label
                        tk.Label(
                            scrollable_frame,
                            text=metric.replace('_', ' ').title() + ":",
                            font=("Arial", 12),
                            bg="#f0f0f0"
                        ).grid(row=row, column=0, sticky="w", padx=20, pady=2)
                        
                        # Value
                        tk.Label(
                            scrollable_frame,
                            text=formatted_value,
                            font=("Arial", 12),
                            fg="#2980b9",
                            bg="#f0f0f0"
                        ).grid(row=row, column=1, sticky="e", padx=20, pady=2)
                        
                        row += 1
            
            # If no data available for this section
            if not has_data:
                tk.Label(
                    scrollable_frame,
                    text="No data available",
                    font=("Arial", 12, "italic"),
                    fg="gray",
                    bg="#f0f0f0"
                ).grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=2)
                row += 1

    def fill_trends_tab(self, tab, data):
        """Fill the trends tab with graphs."""
        # Create figure and canvas
        fig = plt.Figure(figsize=(10, 8), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Create subplots
        ax1 = fig.add_subplot(221)  # Cases
        ax2 = fig.add_subplot(222)  # Deaths
        ax3 = fig.add_subplot(223)  # Tests
        ax4 = fig.add_subplot(224)  # Vaccinations
        
        # Plot cases
        if 'new_cases_smoothed' in data.columns and not data['new_cases_smoothed'].isna().all():
            ax1.plot(data['date'], data['new_cases_smoothed'], color='#3498db')
            ax1.set_title('New Cases (7-day avg)')
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            ax1.grid(True, linestyle='--', alpha=0.7)
        else:
            ax1.text(0.5, 0.5, 'No cases data available', ha='center', va='center', transform=ax1.transAxes)
        
        # Plot deaths
        if 'new_deaths_smoothed' in data.columns and not data['new_deaths_smoothed'].isna().all():
            ax2.plot(data['date'], data['new_deaths_smoothed'], color='#e74c3c')
            ax2.set_title('New Deaths (7-day avg)')
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
            ax2.grid(True, linestyle='--', alpha=0.7)
        else:
            ax2.text(0.5, 0.5, 'No deaths data available', ha='center', va='center', transform=ax2.transAxes)
        
        # Plot testing
        if 'positive_rate' in data.columns and not data['positive_rate'].isna().all():
            ax3.plot(data['date'], data['positive_rate'], color='#f39c12')
            ax3.set_title('Positive Test Rate')
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
            ax3.grid(True, linestyle='--', alpha=0.7)
        else:
            ax3.text(0.5, 0.5, 'No testing data available', ha='center', va='center', transform=ax3.transAxes)
        
        # Plot vaccinations
        if 'people_fully_vaccinated' in data.columns and not data['people_fully_vaccinated'].isna().all():
            # Get the population for percentage calculation
            if 'population' in data.columns and not pd.isna(data['population'].iloc[0]):
                population = data['population'].iloc[0]
                data['vaccination_percentage'] = (data['people_fully_vaccinated'] / population) * 100
                ax4.plot(data['date'], data['vaccination_percentage'], color='#2ecc71')
                ax4.set_title('Fully Vaccinated (%)')
                ax4.set_ylim([0, 100])
            else:
                ax4.plot(data['date'], data['people_fully_vaccinated'], color='#2ecc71')
                ax4.set_title('Fully Vaccinated (Count)')
            
            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
            ax4.grid(True, linestyle='--', alpha=0.7)
        else:
            ax4.text(0.5, 0.5, 'No vaccination data available', ha='center', va='center', transform=ax4.transAxes)
        
        fig.tight_layout()

    def add_population_info(self, tab, data):
        """Add population information to the tab."""
        # Create frame for population data
        frame = tk.Frame(tab, bg="#f0f0f0")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Define population metrics
        population_metrics = [
            ("Population", "population"),
            ("Population Density", "population_density"),
            ("Median Age", "median_age"),
            ("Aged 65 Older", "aged_65_older"),
            ("Aged 70 Older", "aged_70_older"),
            ("GDP Per Capita", "gdp_per_capita"),
            ("Life Expectancy", "life_expectancy"),
            ("Human Development Index", "human_development_index")
        ]
        
        # Add metrics
        for i, (label, column) in enumerate(population_metrics):
            if column in data.columns and not pd.isna(data[column].iloc[0]):
                value = data[column].iloc[0]
                
                # Format value
                if column == "population":
                    formatted_value = f"{value:,.0f}"
                elif column == "population_density":
                    formatted_value = f"{value:.1f} per km²"
                elif "aged" in column:
                    formatted_value = f"{value:.1f}%"
                elif column == "gdp_per_capita":
                    formatted_value = f"${value:,.0f}"
                elif column == "life_expectancy":
                    formatted_value = f"{value:.1f} years"
                elif column == "human_development_index":
                    formatted_value = f"{value:.3f}"
                else:
                    formatted_value = f"{value}"
                
                # Row frame
                row_frame = tk.Frame(frame, bg="#f0f0f0")
                row_frame.pack(fill="x", pady=5)
                
                # Label
                tk.Label(
                    row_frame,
                    text=label + ":",
                    font=("Arial", 12, "bold"),
                    width=20,
                    anchor="w",
                    bg="#f0f0f0"
                ).pack(side=tk.LEFT)
                
                # Value
                tk.Label(
                    row_frame,
                    text=formatted_value,
                    font=("Arial", 12),
                    fg="#2980b9",
                    bg="#f0f0f0"
                ).pack(side=tk.LEFT)

    def show_vaccination_data(self):
        """Show vaccination progress window."""
        try:
            # Create a new window
            vacc_window = tk.Toplevel(self.root)
            vacc_window.title("COVID-19 Vaccination Progress")
            vacc_window.geometry("900x700")
            vacc_window.configure(bg="#f0f0f0")
            
            # Title
            tk.Label(
                vacc_window, 
                text="COVID-19 Vaccination Progress",
                font=("Arial", 16, "bold"),
                bg="#f0f0f0"
            ).pack(pady=10)
            
            # Controls
            control_frame = tk.Frame(vacc_window, bg="#f0f0f0")
            control_frame.pack(fill="x", padx=20, pady=10)
            
            # Filter by continent
            continent_label = tk.Label(control_frame, text="Filter by Continent:", bg="#f0f0f0", font=("Arial", 12))
            continent_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            continents = ["All"] + sorted(self.df[self.df['iso_code'].str.contains('OWID_', na=False) & 
                                          ~self.df['iso_code'].isin(['OWID_WRL', 'OWID_HIC', 'OWID_UMC', 'OWID_LMC', 'OWID_LIC'])]['location'].unique().tolist())
            
            self.continent_var = tk.StringVar(value="All")
            continent_dropdown = ttk.Combobox(
                control_frame, 
                textvariable=self.continent_var,
                values=continents,
                width=20,
                font=("Arial", 12)
            )
            continent_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            # Metric selection
            metric_label = tk.Label(control_frame, text="Metric:", bg="#f0f0f0", font=("Arial", 12))
            metric_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
            
            vacc_metrics = [
                "people_vaccinated_per_hundred", 
                "people_fully_vaccinated_per_hundred",
                "total_boosters_per_hundred"
            ]
            
            self.vacc_metric_var = tk.StringVar(value="people_fully_vaccinated_per_hundred")
            metric_dropdown = ttk.Combobox(
                control_frame, 
                textvariable=self.vacc_metric_var,
                values=vacc_metrics,
                width=30,
                font=("Arial", 12)
            )
            metric_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky="w")
            
            # Update button
            update_btn = tk.Button(control_frame, text="Update", command=self.update_vaccination_graph, font=("Arial", 12))
            update_btn.grid(row=0, column=4, padx=5, pady=5, sticky="w")
            
            # Create a frame for the plot
            plot_frame = tk.Frame(vacc_window, bg="white")
            plot_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Create the figure and canvas
            self.vacc_fig = plt.Figure(figsize=(10, 8), dpi=100)
            self.vacc_canvas = FigureCanvasTkAgg(self.vacc_fig, master=plot_frame)
            self.vacc_canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Initial update
            self.update_vaccination_graph()
            
            # Bind events
            continent_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_vaccination_graph())
            metric_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_vaccination_graph())
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


    def update_vaccination_graph(self):
        """Update the vaccination progress graph."""
        try:
            self.vacc_fig.clear()
            
            # Add subplots
            ax1 = self.vacc_fig.add_subplot(211)  # Top countries
            ax2 = self.vacc_fig.add_subplot(212)  # Timeline
            
            metric = self.vacc_metric_var.get()
            continent = self.continent_var.get()
            
            # Format metric for display
            if metric == "people_vaccinated_per_hundred":
                metric_title = "At Least One Dose"
            elif metric == "people_fully_vaccinated_per_hundred":
                metric_title = "Fully Vaccinated"
            else:
                metric_title = "Boosters"
                
            # Get the latest date with good data coverage
            latest_dates = self.df.groupby('location')['date'].max().reset_index()
            recent_date = latest_dates['date'].value_counts().idxmax()
            
            # Filter data by continent if needed
            if continent != "All":
                # Get countries in the selected continent
                continent_data = self.df[self.df['location'] == continent]
                if not continent_data.empty and 'continent' in continent_data.columns:
                    continent_val = continent
                else:
                    # Extract continent from location
                    continent_val = continent
                    
                # Filter countries by the selected continent
                countries_in_continent = self.df[self.df['continent'] == continent_val]['location'].unique()
                filtered_data = self.df[self.df['location'].isin(countries_in_continent)]
            else:
                filtered_data = self.df.copy()
            
            # Filter out continents, world, and income groups for the bar chart
            country_data = filtered_data[~filtered_data['iso_code'].str.contains('OWID_', na=False)]
            
            # Get latest data for each country
            latest_data = []
            for location in country_data['location'].unique():
                country_latest = country_data[country_data['location'] == location].sort_values('date').tail(1)
                if not country_latest.empty and metric in country_latest.columns and not pd.isna(country_latest[metric].iloc[0]):
                    latest_data.append(country_latest)
            
            if latest_data:
                latest_df = pd.concat(latest_data)
                
                # Sort by the metric and get top countries
                top_countries = latest_df.sort_values(by=metric, ascending=False).head(15)
                
                # Create bar chart
                bars = ax1.barh(top_countries['location'], top_countries[metric], color=sns.color_palette("viridis", 15))
                ax1.set_title(f"Top Countries by Vaccination Rate ({metric_title})", fontsize=14)
                ax1.set_xlabel("Percentage of Population (%)", fontsize=12)
                ax1.invert_yaxis()  # To have highest value at the top
                ax1.grid(True, linestyle='--', alpha=0.7, axis='x')
                
                # Add percentages to bars
                for bar in bars:
                    width = bar.get_width()
                    ax1.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
                            va='center', fontsize=10)
            else:
                ax1.text(0.5, 0.5, "No vaccination data available", ha='center', va='center', 
                         transform=ax1.transAxes, fontsize=14)
            
            # Create timeline for selected countries or regions
            if continent == "All":
                # Show global and continent trends
                timeline_data = filtered_data[filtered_data['iso_code'].str.contains('OWID_')].copy()
                timeline_entities = ['OWID_WRL'] + [iso for iso in timeline_data['iso_code'].unique() 
                                                 if iso != 'OWID_WRL' and not any(x in iso for x in ['HIC', 'UMC', 'LMC', 'LIC'])]
                timeline_df = timeline_data[timeline_data['iso_code'].isin(timeline_entities)]
            else:
                # Show selected continent and its top countries
                if continent != "All" and top_countries is not None and not top_countries.empty:
                    top_5_countries = top_countries.head(5)['location'].tolist()
                    continent_code = filtered_data[filtered_data['location'] == continent]['iso_code'].iloc[0] \
                                    if not filtered_data[filtered_data['location'] == continent].empty else None
                    
                    timeline_entities = []
                    if continent_code:
                        timeline_entities.append(continent_code)
                    timeline_entities.extend(top_5_countries)
                    
                    timeline_df = filtered_data[filtered_data['location'].isin(timeline_entities)]
                else:
                    timeline_df = pd.DataFrame()  # Empty dataframe if no data
            
            # Plot timeline
            if not timeline_df.empty and metric in timeline_df.columns:
                # Get unique locations
                locations = timeline_df['location'].unique()
                colors = sns.color_palette("viridis", len(locations))
                
                # Plot each location
                for i, location in enumerate(locations):
                    loc_data = timeline_df[timeline_df['location'] == location].sort_values('date')
                    if not loc_data[metric].isna().all():
                        ax2.plot(loc_data['date'], loc_data[metric], 
                                label=location, color=colors[i], linewidth=2)
                
                ax2.set_title(f"Vaccination Progress Over Time ({metric_title})", fontsize=14)
                ax2.set_xlabel("Date", fontsize=12)
                ax2.set_ylabel("Percentage of Population (%)", fontsize=12)
                ax2.grid(True, linestyle='--', alpha=0.7)
                ax2.legend(loc='upper left')
                
                # Format x-axis
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
                ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
            else:
                ax2.text(0.5, 0.5, "No timeline data available", ha='center', va='center', 
                         transform=ax2.transAxes, fontsize=14)
            
            self.vacc_fig.tight_layout()
            self.vacc_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = CovidDataTracker(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        import traceback
        traceback.print_exc()