from fpdf import FPDF

def generate_pdf_report(filename, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "CYBERDUDEBIVASH PORT SCAN REPORT", ln=1, align="C")
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, content)
    pdf.output(filename)