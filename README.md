# COVID-19 Global Data Tracker

A desktop application built with Python and Tkinter that visualizes and analyzes COVID-19 data from around the world. This interactive tool allows users to explore trends, compare countries, and monitor key metrics related to the pandemic.

![COVID-19 Tracker Screenshot]![Screenshot 2025-05-11 132339](https://github.com/user-attachments/assets/7c078dc8-41b1-4c28-a545-cca240d61b63)


## Features

- **Global & Country-Level Tracking**: Monitor COVID-19 cases, deaths, hospitalizations, testing, and vaccinations worldwide or for specific countries
- **Interactive Visualizations**: View time series plots, bar charts, and comparative analyses
- **Multiple Metrics**: Analyze various indicators including:
  - Total and new cases/deaths
  - Cases/deaths per million population
  - ICU and hospital patients
  - Testing rates and positivity rates
  - Vaccination progress
  - Reproduction rate (R value)
- **Country Comparison**: Compare metrics across top countries
- **Detailed Statistics**: Access in-depth data for any country
- **Population Data**: View demographic information and its relation to pandemic metrics
- **Vaccination Progress**: Track global vaccination campaigns

## Installation

### Prerequisites
- Python 3.6 or higher
- Basic understanding of Python and pip

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Danielkague/covid-data-tracker.git
   cd covid-data-tracker
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the dataset**
   
   The application requires the "Our World in Data" COVID-19 dataset, which is too large to include in the repository. Download it using one of these methods:

   **Option 1**: Use the provided download script
   ```bash
   python download_data.py
   ```

   **Option 2**: Download manually from the source
   ```bash
   wget https://covid.ourworldindata.org/data/owid-covid-data.csv
   ```
   
   Or visit [Our World in Data](https://covid.ourworldindata.org/data/owid-covid-data.csv) to download directly.

4. **Run the application**
   ```bash
   python covid_tracker.py
   ```

## Usage Guide

### Main Interface
- **Country Selection**: Choose a country from the dropdown menu
- **Metric Selection**: Select which COVID-19 metric to visualize
- **Compare Top Countries**: Toggle this option to see how different countries compare
- **Update Graph**: Refresh the visualization with new selections

### Additional Analysis Tools
- **Global Stats**: View comprehensive global statistics
- **Country Stats**: Access detailed metrics for a specific country
- **Vaccination Progress**: Analyze vaccination rates across countries

### Data Exploration
- Time series data shows trends over the course of the pandemic
- Bar charts allow for easy comparison between countries
- Tabbed interfaces provide organized access to different categories of information

## Data Source

This application uses the "Our World in Data" COVID-19 dataset, which is compiled from official sources including:
- World Health Organization (WHO)
- European Centre for Disease Prevention and Control (ECDC)
- Johns Hopkins University CSSE COVID-19 Data
- National government reports

The dataset is updated daily and includes data on confirmed cases, deaths, hospitalizations, testing, and vaccinations.

## Requirements

- pandas
- matplotlib
- seaborn
- numpy
- tkinter (included in standard Python distribution)

## Contributing

Contributions to improve the application are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Our World in Data](https://ourworldindata.org/) for providing the comprehensive COVID-19 dataset
- The global scientific community for their work in tracking and analyzing pandemic data
