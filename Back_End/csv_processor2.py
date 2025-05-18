import pandas as pd
import chardet
import io
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from datetime import datetime
from Back_End import process

# Additional enhancements for flexibility and optimization
pd.options.mode.copy_on_write = True

def detect_encoding(file):
    """Detects encoding of a file-like object or file path."""
    try:
        if isinstance(file, str):
            with open(file, "rb") as f:
                result = chardet.detect(f.read(100000))
        else:
            result = chardet.detect(file.read(100000))
            file.seek(0)
        return result["encoding"]
    except Exception as e:
        print(f"Encoding detection error: {e}")
        return None

def read_csv_with_encoding(file, sample_size=None):
    """Reads a CSV file with encoding detection and fallback, optionally sampling."""
    detected_encoding = detect_encoding(file)
    if detected_encoding is None:
        return None, "Encoding detection failed."

    try:
        # Sample the file if necessary
        if sample_size:
            df = pd.read_csv(file, encoding=detected_encoding, nrows=sample_size)
        else:
            df = pd.read_csv(file, encoding=detected_encoding)

    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file, encoding="ISO-8859-1")
        except Exception as e:
            return None, f"Encoding Error: {e}"

    if df.empty or len(df.columns) == 1:
        try:
            df = pd.read_csv(file, encoding=detected_encoding, header=None)
        except Exception as e:
            return None, f"Final Read Error: {e}"

    return df, None

def read_file(file, sample_size=None):
    """Reads the file, supporting only local files (CSV)."""
    return read_csv_with_encoding(file, sample_size)

def generate_histogram(df, p, y_position, bins=30, palette='blue'):
    """Generates and adds histograms to the PDF with customizable bins and palette."""
    for col in df.select_dtypes(include=[np.number]).columns:
        plt.figure(figsize=(12, 7))  # Larger figure size
        sns.histplot(df[col], kde=True, color=palette, bins=bins)
        plt.title(f"Histogram for {col}")
        plt.xlabel(col)
        plt.ylabel('Frequency')

        # Save plot to image buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100)
        img_buffer.seek(0)
        img = ImageReader(img_buffer)
        p.drawImage(img, 50, y_position - 350, width=550, height=350, preserveAspectRatio=True)  # Larger image size
        plt.close()
        y_position -= 370
        if y_position < 100:
            p.showPage()
            y_position = 750  # Reset for new page
    return y_position

def generate_correlation_heatmap(df, p, y_position):
    """Generates and adds a correlation heatmap to the PDF."""
    corr_matrix = df.corr(numeric_only=True)
    plt.figure(figsize=(12, 7))  # Adjusted figure size for larger heatmap
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', cbar=True)
    plt.title("Correlation Heatmap")

    # Save plot to image buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100)
    img_buffer.seek(0)
    img = ImageReader(img_buffer)
    p.drawImage(img, 50, y_position - 300, width=550, height=300, preserveAspectRatio=True)  # Larger image size
    plt.close()

    y_position -= 300
    if y_position < 100:
        p.showPage()
        y_position = 750  # Reset for new page

    return y_position

def process_file(file, target_col=None, sample_size=None, plot_bins=30, plot_palette='blue'):
    """Generates an enhanced PDF report with statistical and correlation analysis."""
    df, error = read_file(file, sample_size)
    if error:
        return None, error

    try:
        df = process.process_file(df)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y_position = height - 50  # Reduced top margin for better usage of space
        x_position = 50

        # Title Page
        p.setFont("Helvetica-Bold", 18)  # Larger title
        p.drawString(180, y_position, "CSV Analysis Report")
        y_position -= 30
        p.setFont("Helvetica", 10)  # Smaller font for subtitle
        p.drawString(180, y_position, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y_position -= 40
        p.showPage()

        # Summary Statistics
        summary = df.describe().T[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        p.setFont("Helvetica-Bold", 12)  # Section titles font size
        p.drawString(x_position, y_position, "Summary Statistics")
        y_position -= 20

        for index, row in summary.iterrows():
            p.setFont("Helvetica", 10)  # Content font size
            p.drawString(x_position, y_position, f"{index}: Mean={row['mean']:.2f}, Std={row['std']:.2f}, Min={row['min']:.2f}, Max={row['max']:.2f}")
            y_position -= 15  # Reduced space between lines
            if y_position < 100:
                p.showPage()
                y_position = height - 50

        # Top Correlated Pairs
        corr_matrix = df.corr(numeric_only=True).abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        correlated_pairs = [(index, col, upper.loc[index, col]) for col in upper.columns for index in upper.index if col != index and upper.loc[index, col] > 0.3]
        correlated_pairs = sorted(correlated_pairs, key=lambda x: -x[2])[:5]

        p.setFont("Helvetica-Bold", 12)
        p.drawString(x_position, y_position, "Top Correlated Pairs")
        y_position -= 20

        for col1, col2, correlation_value in correlated_pairs:
            p.setFont("Helvetica", 10)
            p.drawString(x_position, y_position, f"{col1} & {col2}: {correlation_value:.2f}")
            y_position -= 15
            if y_position < 100:
                p.showPage()
                y_position = height - 50

        # Add Correlation Heatmap to the same page
        y_position = generate_correlation_heatmap(df, p, y_position)

        # Start a new page for Histograms
        p.showPage()
        y_position = height - 50  # Reset y_position for new page

        # Add all the visualizations (histograms) after the heatmap on a new page
        y_position = generate_histogram(df, p, y_position, bins=plot_bins, palette=plot_palette)

        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, f"Processing error: {e}"
