"""
FinSight AI - Data & Environment Initialization Script (Day 1)
Generates:
1. Structured Data: SQLite database (sales_data.db) + CSV files for:
   - regions
   - customers
   - products
   - orders
   - order_items
2. Unstructured Data: 4 realistic, multi-page corporate PDFs in data/pdfs/ using ReportLab.
"""

import os
import sys
import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

# Set utf-8 encoding for stdout on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas

# Base Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
CSV_DIR = os.path.join(DATA_DIR, "csvs")
DB_PATH = os.path.join(DATA_DIR, "sales_data.db")


def create_directories():
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(CSV_DIR, exist_ok=True)
    print(f"✅ Created directories:\n   - {PDF_DIR}\n   - {CSV_DIR}")


def generate_structured_data():
    print("\n📊 Generating Structured Sales Data (SQLite & CSVs)...")
    
    # 1. Regions
    regions_data = [
        {"region_id": 1, "region_name": "North America - East", "country": "United States", "manager": "Sarah Jenkins", "headquarters": "New York, NY"},
        {"region_id": 2, "region_name": "North America - West", "country": "United States", "manager": "Marcus Chen", "headquarters": "San Francisco, CA"},
        {"region_id": 3, "region_name": "EMEA - North", "country": "United Kingdom", "manager": "Oliver Smith", "headquarters": "London, UK"},
        {"region_id": 4, "region_name": "EMEA - Central", "country": "Germany", "manager": "Hanna Schmidt", "headquarters": "Frankfurt, Germany"},
        {"region_id": 5, "region_name": "APAC - East", "country": "Japan", "manager": "Kenji Sato", "headquarters": "Tokyo, Japan"},
        {"region_id": 6, "region_name": "APAC - South", "country": "Singapore", "manager": "Priya Sharma", "headquarters": "Singapore"},
    ]
    df_regions = pd.DataFrame(regions_data)

    # 2. Customers
    industries = ["Technology", "Healthcare", "Financial Services", "Manufacturing", "Retail", "Energy"]
    tiers = ["Enterprise", "Mid-Market", "Strategic", "SMB"]
    companies = [
        "NovaTech Global", "Aegis Health Group", "Vanguard Financial", "Apex Dynamics", "Pinnacle Retail",
        "Aura Energy Corp", "Zenith Logistics", "Vertex Biotech", "Quantum Capital", "Meridian Media",
        "Beacon Software", "Crestview Capital", "Starlight Pharma", "OmniCorp Industries", "BlueWave Solutions",
        "Titan Industrial", "Solstice Media", "Hyperion Analytics", "Pacific Cloudworks", "Nexus Health Systems",
        "Ironclad Defense", "Terra Systems", "Optima Banking", "Stratus Infotech", "Synergy Retailers"
    ]
    
    random.seed(42)
    customers_data = []
    for i, company in enumerate(companies, start=101):
        reg = random.choice(regions_data)
        customers_data.append({
            "customer_id": i,
            "company_name": company,
            "industry": random.choice(industries),
            "region_id": reg["region_id"],
            "tier": random.choice(tiers),
            "contact_email": f"contact@{company.lower().replace(' ', '')}.com",
            "joined_date": (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 900))).strftime("%Y-%m-%d"),
            "credit_limit": random.choice([50000, 100000, 250000, 500000, 1000000])
        })
    df_customers = pd.DataFrame(customers_data)

    # 3. Products
    products_data = [
        {"product_id": 201, "product_name": "FinSight Enterprise Analytics Platform", "category": "Software", "unit_price": 45000.0, "unit_cost": 9000.0, "billing_cycle": "Annual"},
        {"product_id": 202, "product_name": "ApexCloud Core License (Per Seat)", "category": "Cloud Services", "unit_price": 1200.0, "unit_cost": 250.0, "billing_cycle": "Annual"},
        {"product_id": 203, "product_name": "Real-time Fraud Detection Engine", "category": "Security", "unit_price": 28000.0, "unit_cost": 5500.0, "billing_cycle": "Annual"},
        {"product_id": 204, "product_name": "AI Predictive Forecasting Module", "category": "AI/ML", "unit_price": 35000.0, "unit_cost": 7000.0, "billing_cycle": "Annual"},
        {"product_id": 205, "product_name": "Enterprise Dataform ETL Connector", "category": "Data Engineering", "unit_price": 15000.0, "unit_cost": 3000.0, "billing_cycle": "Annual"},
        {"product_id": 206, "product_name": "SOC2 Automated Audit Gateway", "category": "Compliance", "unit_price": 22000.0, "unit_cost": 4500.0, "billing_cycle": "Annual"},
        {"product_id": 207, "product_name": "Executive Intelligence Dashboard Suite", "category": "Visualization", "unit_price": 18000.0, "unit_cost": 3200.0, "billing_cycle": "Annual"},
        {"product_id": 208, "product_name": "24/7 Dedicated TAM & Priority SLA Support", "category": "Professional Services", "unit_price": 20000.0, "unit_cost": 12000.0, "billing_cycle": "Annual"},
        {"product_id": 209, "product_name": "Custom ML Model Fine-Tuning Package", "category": "Professional Services", "unit_price": 40000.0, "unit_cost": 18000.0, "billing_cycle": "One-Time"},
        {"product_id": 210, "product_name": "Hybrid Cloud Migration Accelerator", "category": "Professional Services", "unit_price": 50000.0, "unit_cost": 22000.0, "billing_cycle": "One-Time"}
    ]
    df_products = pd.DataFrame(products_data)

    # 4. Orders & Order Items
    orders_data = []
    order_items_data = []
    
    order_statuses = ["Completed", "Completed", "Completed", "Pending", "Processing"]
    payment_methods = ["Wire Transfer", "Corporate Credit Card", "ACH", "Invoice Net-30"]
    
    item_counter = 1
    for order_id in range(1001, 1076):
        cust = random.choice(customers_data)
        order_date = (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 360))).strftime("%Y-%m-%d")
        status = random.choice(order_statuses)
        payment_method = random.choice(payment_methods)
        
        num_items = random.randint(1, 3)
        selected_prods = random.sample(products_data, num_items)
        order_total = 0.0
        
        for prod in selected_prods:
            qty = random.randint(1, 5) if prod["category"] != "Cloud Services" else random.randint(10, 50)
            discount = random.choice([0.0, 0.05, 0.10, 0.15])
            line_total = (prod["unit_price"] * qty) * (1.0 - discount)
            order_total += line_total
            
            order_items_data.append({
                "item_id": item_counter,
                "order_id": order_id,
                "product_id": prod["product_id"],
                "quantity": qty,
                "unit_price": prod["unit_price"],
                "discount_pct": discount,
                "line_total": round(line_total, 2)
            })
            item_counter += 1
            
        orders_data.append({
            "order_id": order_id,
            "customer_id": cust["customer_id"],
            "order_date": order_date,
            "status": status,
            "payment_method": payment_method,
            "total_amount": round(order_total, 2)
        })
        
    df_orders = pd.DataFrame(orders_data)
    df_order_items = pd.DataFrame(order_items_data)

    # Save to CSV files
    df_regions.to_csv(os.path.join(CSV_DIR, "regions.csv"), index=False)
    df_customers.to_csv(os.path.join(CSV_DIR, "customers.csv"), index=False)
    df_products.to_csv(os.path.join(CSV_DIR, "products.csv"), index=False)
    df_orders.to_csv(os.path.join(CSV_DIR, "orders.csv"), index=False)
    df_order_items.to_csv(os.path.join(CSV_DIR, "order_items.csv"), index=False)
    print("   ✓ Saved 5 CSV files to data/csvs/")

    # Save to SQLite
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables with explicit schemas & foreign keys
    cursor.execute("""
    CREATE TABLE regions (
        region_id INTEGER PRIMARY KEY,
        region_name TEXT NOT NULL,
        country TEXT NOT NULL,
        manager TEXT NOT NULL,
        headquarters TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        company_name TEXT NOT NULL,
        industry TEXT NOT NULL,
        region_id INTEGER NOT NULL,
        tier TEXT NOT NULL,
        contact_email TEXT NOT NULL,
        joined_date TEXT NOT NULL,
        credit_limit REAL NOT NULL,
        FOREIGN KEY (region_id) REFERENCES regions(region_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit_price REAL NOT NULL,
        unit_cost REAL NOT NULL,
        billing_cycle TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        status TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        total_amount REAL NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        discount_pct REAL NOT NULL,
        line_total REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

    # Populate SQLite tables
    df_regions.to_sql("regions", conn, if_exists="append", index=False)
    df_customers.to_sql("customers", conn, if_exists="append", index=False)
    df_products.to_sql("products", conn, if_exists="append", index=False)
    df_orders.to_sql("orders", conn, if_exists="append", index=False)
    df_order_items.to_sql("order_items", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print(f"   ✓ Created and populated SQLite database: {DB_PATH}")


class NumberedCanvas(canvas.Canvas):
    """Adds Page X of Y and a professional running footer/header."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#555555"))
        # Top Rule
        self.setStrokeColor(colors.HexColor("#DDDDDD"))
        self.setLineWidth(0.5)
        self.line(54, 750, 558, 750)
        self.drawString(54, 755, "FinSight AI Corporate Repository — Confidential")
        
        # Bottom Rule & Page Number
        self.line(54, 50, 558, 50)
        self.drawRightString(558, 38, f"Page {self._pageNumber} of {page_count}")
        self.drawString(54, 38, "For Internal Authorized Use Only")
        self.restoreState()


def generate_unstructured_pdfs():
    print("\n📄 Generating 4 Realistic Sample PDFs (Unstructured Corporate Docs)...")
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=12
    )
    
    heading2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=14,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=8
    )

    # -------------------------------------------------------------
    # PDF 1: Annual Report 2025 (Acme Corp)
    # -------------------------------------------------------------
    doc1_path = os.path.join(PDF_DIR, "AcmeCorp_Annual_Report_2025.pdf")
    doc1 = SimpleDocTemplate(doc1_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=60, bottomMargin=60)
    story1 = []
    
    story1.append(Paragraph("Acme Corp & FinSight Group — Annual Performance Report 2025", title_style))
    story1.append(Paragraph("<b>Reporting Period:</b> Fiscal Year Ended December 31, 2025 | <b>Published:</b> January 2026", body_style))
    story1.append(Spacer(1, 10))
    
    story1.append(Paragraph("1. Executive Summary & CEO Letter", heading2_style))
    story1.append(Paragraph(
        "Fiscal Year 2025 marked a transformative milestone for Acme Corp and the FinSight platform. "
        "Consolidated total revenue reached <b>$148.5 Million</b>, reflecting a year-over-year growth of <b>28.4%</b>. "
        "Our core investments in Agentic AI and safe enterprise retrieval pipelines unlocked over $32M in net new Annual Recurring Revenue (ARR).",
        body_style
    ))
    story1.append(Paragraph(
        "Our flagship FinSight Enterprise Analytics Platform expanded its customer base across North America and EMEA, achieving a customer retention rate of 96.2% with a Net Promoter Score (NPS) of 72.",
        body_style
    ))
    
    story1.append(Paragraph("2. Consolidated Financial Highlights", heading2_style))
    fin_table_data = [
        ["Financial Metric", "FY 2024 (USD)", "FY 2025 (USD)", "YoY Growth (%)"],
        ["Total Revenue", "$115.6 M", "$148.5 M", "+28.4%"],
        ["Subscription ARR", "$84.2 M", "$116.4 M", "+38.2%"],
        ["Gross Profit Margin", "74.5%", "78.2%", "+370 bps"],
        ["R&D Expenditure", "$24.1 M", "$34.8 M", "+44.4%"],
        ["Operating Income (EBITDA)", "$21.3 M", "$31.5 M", "+47.8%"],
        ["Net Cash from Operations", "$28.0 M", "$39.2 M", "+40.0%"]
    ]
    t1 = Table(fin_table_data, colWidths=[160, 110, 110, 100])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('FONTSIZE', (0,1), (-1,-1), 9),
    ]))
    story1.append(t1)
    
    story1.append(PageBreak())
    
    story1.append(Paragraph("3. Segment & Regional Revenue Analysis", heading2_style))
    story1.append(Paragraph(
        "North America accounted for 58% of total revenue ($86.1M), followed by EMEA at 26% ($38.6M) and APAC at 16% ($23.8M). "
        "The fastest accelerating segment was AI/ML Modules, which surged 112% YoY following the release of our Safe Text-to-SQL copilot.",
        body_style
    ))
    story1.append(Paragraph("4. Strategic Outlook for 2026", heading2_style))
    story1.append(Paragraph(
        "For FY 2026, the company targets $195M in revenue with sustained R&D focus on LangGraph multi-agent systems, automated evaluation frameworks (RAGAS), and zero-trust hybrid database integrations.",
        body_style
    ))
    doc1.build(story1, canvasmaker=NumberedCanvas)
    print("   ✓ Generated: AcmeCorp_Annual_Report_2025.pdf")

    # -------------------------------------------------------------
    # PDF 2: Enterprise HR Policy Handbook
    # -------------------------------------------------------------
    doc2_path = os.path.join(PDF_DIR, "Enterprise_HR_Policy_Handbook.pdf")
    doc2 = SimpleDocTemplate(doc2_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=60, bottomMargin=60)
    story2 = []
    
    story2.append(Paragraph("Enterprise HR Policy Handbook & Employee Guidelines", title_style))
    story2.append(Paragraph("<b>Version:</b> 4.2 | <b>Effective Date:</b> January 1, 2025 | <b>Scope:</b> All Full-Time & Contract Employees", body_style))
    story2.append(Spacer(1, 10))
    
    story2.append(Paragraph("1. Paid Time Off (PTO) & Leave Entitlements", heading2_style))
    story2.append(Paragraph(
        "All standard full-time employees accrue <b>20 days of Paid Annual Leave</b> per calendar year, accrued at 1.66 days per month. "
        "In addition, employees are allocated <b>10 days of Paid Sick and Personal Well-being Leave</b> annually.",
        body_style
    ))
    story2.append(Paragraph(
        "A maximum of <b>5 unused Annual Leave days</b> may be carried over into the following calendar year, provided they are utilized before March 31st. Any leave exceeding this cap will lapse unless granted an exception by VP of HR.",
        body_style
    ))

    story2.append(Paragraph("2. Remote and Hybrid Workplace Policy", heading2_style))
    story2.append(Paragraph(
        "Engineering, Product, and Data teams operate under a designated <b>Flexible Hybrid Model</b>: 2 mandatory in-office collaboration days (Tuesdays & Thursdays) and 3 optional remote work days. "
        "Employees wishing to work 100% remotely must maintain a performance rating of 'Exceeds Expectations' (Level 4+) and have direct manager and VP sign-off.",
        body_style
    ))
    
    story2.append(PageBreak())
    
    story2.append(Paragraph("3. Expense Reimbursement and Equipment Allowances", heading2_style))
    hr_table_data = [
        ["Expense Category", "Annual / Monthly Cap", "Approval Requirement", "Receipt Policy"],
        ["Home Office Setup", "$1,000 (One-Time)", "Manager Approval", "Itemized receipt required"],
        ["Monthly Internet Stipend", "$75 / Month", "Automatic in payroll", "Proof of utility bill"],
        ["Learning & Conference Budget", "$2,500 / Year", "Director Approval", "Certificate of completion"],
        ["Wellness & Gym Allowance", "$600 / Year", "Manager Approval", "Monthly receipt"]
    ]
    t2 = Table(hr_table_data, colWidths=[150, 110, 110, 110])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
    ]))
    story2.append(t2)
    
    story2.append(Paragraph("4. Performance Reviews and Promotion Cycles", heading2_style))
    story2.append(Paragraph(
        "Formal performance reviews occur biannually: <b>Mid-Year Review (July)</b> and <b>End-of-Year Review (December)</b>. Merit increases and promotions take effect on March 1st following end-of-year calibration.",
        body_style
    ))
    doc2.build(story2, canvasmaker=NumberedCanvas)
    print("   ✓ Generated: Enterprise_HR_Policy_Handbook.pdf")

    # -------------------------------------------------------------
    # PDF 3: ApexCloud Enterprise Product Manual
    # -------------------------------------------------------------
    doc3_path = os.path.join(PDF_DIR, "ApexCloud_Enterprise_Product_Manual.pdf")
    doc3 = SimpleDocTemplate(doc3_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=60, bottomMargin=60)
    story3 = []
    
    story3.append(Paragraph("ApexCloud & FinSight AI Technical Product Manual", title_style))
    story3.append(Paragraph("<b>Product Version:</b> v3.4 Enterprise | <b>Architecture Specification & SLA</b>", body_style))
    story3.append(Spacer(1, 10))
    
    story3.append(Paragraph("1. System Architecture Overview", heading2_style))
    story3.append(Paragraph(
        "ApexCloud Enterprise provides distributed data integration and intelligent agent runtime services. "
        "The system leverages a dual-engine architecture combining dense vector retrieval (ChromaDB with BAAI/bge-small-en-v1.5) "
        "and sparse inverted index matching (BM25) routed through an ensemble weighting formula (0.6 Dense / 0.4 Sparse).",
        body_style
    ))
    story3.append(Paragraph(
        "The agentic runtime is managed by LangGraph with Groq's high-speed Llama-3.3-70B inference engine, maintaining an average token generation latency of less than 1.5 seconds per multi-tool hop.",
        body_style
    ))

    story3.append(Paragraph("2. Service Level Agreements (SLA) & Uptime Guarantees", heading2_style))
    sla_data = [
        ["Tier", "Availability Guarantee", "Target Response Time (P1)", "Monthly Credit on Breach"],
        ["Standard Tier", "99.5% Uptime", "< 4 Hours", "10% of monthly bill"],
        ["Enterprise Tier", "99.9% Uptime", "< 1 Hour", "25% of monthly bill"],
        ["Mission-Critical Tier", "99.99% Uptime", "< 15 Minutes (24/7/365)", "50% of monthly bill"]
    ]
    t3 = Table(sla_data, colWidths=[110, 120, 130, 120])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C5282")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
    ]))
    story3.append(t3)

    story3.append(PageBreak())

    story3.append(Paragraph("3. API Rate Limits & Authentication", heading2_style))
    story3.append(Paragraph(
        "Authentication requires an enterprise Bearer token in the <code>Authorization</code> header. "
        "Rate limits are enforced at the API Gateway: <b>Enterprise Tier</b> accounts are permitted up to <b>1,200 requests/minute</b> with bursting up to 2,000 requests. Exceeding thresholds triggers HTTP 429 (Too Many Requests).",
        body_style
    ))
    story3.append(Paragraph("4. Text-to-SQL Security Guardrails", heading2_style))
    story3.append(Paragraph(
        "The SQL tool strictly executes in SQLite Read-Only mode (<code>?mode=ro</code>). "
        "Any SQL statement containing mutating keywords (e.g. <code>DROP</code>, <code>DELETE</code>, <code>INSERT</code>, <code>UPDATE</code>, <code>ALTER</code>) is blocked by the parser before hitting the execution engine.",
        body_style
    ))
    doc3.build(story3, canvasmaker=NumberedCanvas)
    print("   ✓ Generated: ApexCloud_Enterprise_Product_Manual.pdf")

    # -------------------------------------------------------------
    # PDF 4: Cybersecurity & Compliance Standards
    # -------------------------------------------------------------
    doc4_path = os.path.join(PDF_DIR, "Cybersecurity_Compliance_Standards_2025.pdf")
    doc4 = SimpleDocTemplate(doc4_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=60, bottomMargin=60)
    story4 = []
    
    story4.append(Paragraph("Cybersecurity, SOC2 & ISO 27001 Compliance Standards", title_style))
    story4.append(Paragraph("<b>Security Classification:</b> Restricted | <b>Compliance Officer:</b> Chief Information Security Officer (CISO)", body_style))
    story4.append(Spacer(1, 10))
    
    story4.append(Paragraph("1. Data Encryption and Key Management", heading2_style))
    story4.append(Paragraph(
        "All customer data in transit must be encrypted using <b>TLS 1.3</b> (minimum fallback TLS 1.2). "
        "Data at rest across all SQLite shards, ChromaDB vector stores, and object buckets is encrypted using <b>AES-256</b> encryption keys managed via Google Cloud KMS with annual automatic key rotation.",
        body_style
    ))

    story4.append(Paragraph("2. Access Control and Multi-Factor Authentication (MFA)", heading2_style))
    story4.append(Paragraph(
        "Access to production environments and databases requires Hardware-backed FIDO2 MFA keys or Okta Verify with biometric verification. "
        "Role-Based Access Control (RBAC) follows the Principle of Least Privilege (PoLP) and is audited quarterly by the internal security team.",
        body_style
    ))
    
    story4.append(PageBreak())

    story4.append(Paragraph("3. Incident Response Protocol & Escalation SLA", heading2_style))
    sec_table_data = [
        ["Severity Level", "Description", "Escalation Target", "Customer Notice SLA"],
        ["Severity 1 (Critical)", "Data breach or complete outage", "Immediate (CISO & On-Call)", "< 2 Hours"],
        ["Severity 2 (High)", "Partial service disruption", "< 15 Minutes", "< 6 Hours"],
        ["Severity 3 (Medium)", "Isolated non-critical bug", "< 1 Hour", "Next Release Notes"],
        ["Severity 4 (Low)", "Cosmetic or minor documentation issue", "< 24 Hours", "Quarterly Patch"]
    ]
    t4 = Table(sec_table_data, colWidths=[120, 140, 110, 110])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#742A2A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#FFF5F5")]),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
    ]))
    story4.append(t4)
    
    story4.append(Paragraph("4. Data Retention and Deletion SLA", heading2_style))
    story4.append(Paragraph(
        "Upon enterprise contract termination, customer data and embedded vectors are securely erased within <b>30 calendar days</b> using cryptographic erasure (DoD 5220.22-M compliant).",
        body_style
    ))
    doc4.build(story4, canvasmaker=NumberedCanvas)
    print("   ✓ Generated: Cybersecurity_Compliance_Standards_2025.pdf")


if __name__ == "__main__":
    print("[*] Starting FinSight AI Day 1 Dataset & Environment Setup...")
    create_directories()
    generate_structured_data()
    generate_unstructured_pdfs()
    print("\n[SUCCESS] Day 1 Data Generation Completed Successfully!")
