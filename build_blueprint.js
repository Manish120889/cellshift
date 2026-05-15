const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat, ExternalHyperlink,
        TabStopType, TabStopPosition } = require('docx');
const fs = require('fs');

const BRAND = "#1B2A4A";
const BLUE = "#2E75B6";
const ACCENT = "#E8792F";
const LIGHT_BG = "EBF2FA";
const ACCENT_BG = "FDF0E8";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function headerCell(text, width) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: "1B2A4A", type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
  });
}

function cell(text, width, opts = {}) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: opts.shade ? { fill: opts.shade, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 20, bold: opts.bold, color: opts.color })] })]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: BRAND.replace("#","") },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: BLUE.replace("#","") },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: BRAND.replace("#","") },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [
    // TITLE PAGE
    {
      properties: {
        page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
      },
      children: [
        new Paragraph({ spacing: { before: 3000 }, alignment: AlignmentType.CENTER, children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [
          new TextRun({ text: "CELLSHIFT", font: "Arial", size: 72, bold: true, color: "1B2A4A" })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [
          new TextRun({ text: "Company Blueprint", font: "Arial", size: 36, color: "2E75B6" })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [
          new TextRun({ text: "Smart Excel Transformations for Surrey Businesses", font: "Arial", size: 24, color: "64748B", italics: true })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, border: { top: { style: BorderStyle.SINGLE, size: 3, color: "2E75B6", space: 8 } },
          spacing: { before: 200 }, children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400, after: 100 }, children: [
          new TextRun({ text: "Confidential Business Document", font: "Arial", size: 20, bold: true, color: "1B2A4A" })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "Version 1.0 | May 2026", font: "Arial", size: 20, color: "64748B" })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100 }, children: [
          new TextRun({ text: "Prepared by: Cellshift AI Operations", font: "Arial", size: 20, color: "64748B" })
        ]}),
      ]
    },
    // MAIN CONTENT
    {
      properties: {
        page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
      },
      headers: {
        default: new Header({ children: [new Paragraph({
          children: [
            new TextRun({ text: "Cellshift — Company Blueprint", font: "Arial", size: 16, color: "94A3B8", italics: true }),
          ],
          tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
          border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: "E2E8F0", space: 4 } }
        })] })
      },
      footers: {
        default: new Footer({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Cellshift Confidential | Page ", font: "Arial", size: 16, color: "94A3B8" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "94A3B8" }),
          ]
        })] })
      },
      children: [
        // EXECUTIVE SUMMARY
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Executive Summary")] }),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("Cellshift is a zero-investment SaaS company delivering intelligent Excel transformation tools to small and medium businesses in Surrey, British Columbia. The product enables non-technical users to upload messy spreadsheets and receive clean, transformed data in under 60 seconds through a simple toggle-based interface.")
        ]}),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("The company operates on an AI-as-Team model where Claude Pro serves as the full operational team: developer, product manager, QA engineer, marketing lead, and support agent. This eliminates the need for traditional employees, keeping overhead at near-zero while maintaining professional-grade output.")
        ]}),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun({ text: "Target: $1M ARR within 12 months.", bold: true }),
          new TextRun(" Revenue model is freemium SaaS with tiers at $0, $29/month, $79/month, and custom enterprise pricing.")
        ]}),

        // PHASE 1: DETECT
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Phase 1: DETECT — Market Intelligence")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Surrey Market Overview")] }),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("Surrey is British Columbia's second-largest city with over 17,000 registered businesses. The municipal economy is diversified but construction-heavy, creating natural demand for data transformation tools.")
        ]}),

        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [4680, 4680],
          rows: [
            new TableRow({ children: [headerCell("Metric", 4680), headerCell("Value", 4680)] }),
            new TableRow({ children: [cell("Total Registered Businesses", 4680), cell("17,000+", 4680, { bold: true })] }),
            new TableRow({ children: [cell("Construction Sector Share", 4680, { shade: LIGHT_BG }), cell("21% (#1 sector)", 4680, { shade: LIGHT_BG, bold: true })] }),
            new TableRow({ children: [cell("Professional Services", 4680), cell("18%", 4680, { bold: true })] }),
            new TableRow({ children: [cell("Retail Trade", 4680, { shade: LIGHT_BG }), cell("14%", 4680, { shade: LIGHT_BG, bold: true })] }),
            new TableRow({ children: [cell("Healthcare & Social", 4680), cell("12%", 4680, { bold: true })] }),
            new TableRow({ children: [cell("Avg. Annual Growth Rate", 4680, { shade: LIGHT_BG }), cell("3.2%", 4680, { shade: LIGHT_BG, bold: true })] }),
          ]
        }),

        new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("Target Customer Profiles")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Profile 1: Construction Project Managers")] }),
        new Paragraph({ spacing: { after: 100 }, children: [
          new TextRun("Pain: Weekly PO reconciliation, subcontractor billing consolidation, and material allocation tracking all done in Excel. Typically 15+ hours/week in spreadsheet work. Most common transformations needed: unpivot allocation matrices, remove duplicate entries, VLOOKUP PO numbers to invoices.")
        ]}),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Profile 2: Retail Operations Managers")] }),
        new Paragraph({ spacing: { after: 100 }, children: [
          new TextRun("Pain: Multi-location inventory data arrives in different formats. SKU matching across suppliers, seasonal demand pivoting, and stock-level flagging require manual cleanup. Typical need: standardize dates, pivot by location, flag low-stock items.")
        ]}),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Profile 3: Professional Services Bookkeepers")] }),
        new Paragraph({ spacing: { after: 100 }, children: [
          new TextRun("Pain: Client data from multiple accounting systems (QuickBooks exports, bank CSVs, payroll reports) need consolidation. Mixed date formats, duplicate transaction entries, and type mismatches are weekly headaches.")
        ]}),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Competitive Landscape")] }),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2340, 1560, 1560, 1560, 2340],
          rows: [
            new TableRow({ children: [
              headerCell("Competitor", 2340), headerCell("Price", 1560), headerCell("Learning Curve", 1560),
              headerCell("Local Focus", 1560), headerCell("Cellshift Advantage", 2340)
            ]}),
            new TableRow({ children: [
              cell("Power BI", 2340), cell("$10/user/mo", 1560), cell("High", 1560), cell("None", 1560),
              cell("No training required", 2340, { shade: ACCENT_BG })
            ]}),
            new TableRow({ children: [
              cell("Tableau", 2340, { shade: LIGHT_BG }), cell("$75/user/mo", 1560, { shade: LIGHT_BG }),
              cell("Very High", 1560, { shade: LIGHT_BG }), cell("None", 1560, { shade: LIGHT_BG }),
              cell("10x cheaper at Pro tier", 2340, { shade: ACCENT_BG })
            ]}),
            new TableRow({ children: [
              cell("Google Sheets", 2340), cell("Free", 1560), cell("Medium", 1560), cell("None", 1560),
              cell("Auto-analysis, no formulas", 2340, { shade: ACCENT_BG })
            ]}),
            new TableRow({ children: [
              cell("Freelancer/VA", 2340, { shade: LIGHT_BG }), cell("$25-50/hr", 1560, { shade: LIGHT_BG }),
              cell("N/A", 1560, { shade: LIGHT_BG }), cell("Maybe", 1560, { shade: LIGHT_BG }),
              cell("Instant, 24/7, consistent", 2340, { shade: ACCENT_BG })
            ]}),
          ]
        }),

        // PHASE 2: DESIGN
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Phase 2: DESIGN — Product Architecture")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Technology Stack")] }),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2340, 3510, 3510],
          rows: [
            new TableRow({ children: [headerCell("Layer", 2340), headerCell("Technology", 3510), headerCell("Cost", 3510)] }),
            new TableRow({ children: [cell("Frontend", 2340), cell("Streamlit (Python)", 3510), cell("Free", 3510, { color: "16A34A", bold: true })] }),
            new TableRow({ children: [cell("Backend Engine", 2340, { shade: LIGHT_BG }), cell("Pandas + OpenPyXL", 3510, { shade: LIGHT_BG }), cell("Free", 3510, { shade: LIGHT_BG, color: "16A34A", bold: true })] }),
            new TableRow({ children: [cell("Hosting", 2340), cell("Streamlit Community Cloud", 3510), cell("Free", 3510, { color: "16A34A", bold: true })] }),
            new TableRow({ children: [cell("Source Control", 2340, { shade: LIGHT_BG }), cell("GitHub (public repo)", 3510, { shade: LIGHT_BG }), cell("Free", 3510, { shade: LIGHT_BG, color: "16A34A", bold: true })] }),
            new TableRow({ children: [cell("Analytics", 2340), cell("Plausible Analytics", 3510), cell("Free tier", 3510, { color: "16A34A", bold: true })] }),
            new TableRow({ children: [cell("Payments", 2340, { shade: LIGHT_BG }), cell("Stripe", 3510, { shade: LIGHT_BG }), cell("2.9% + $0.30/txn", 3510, { shade: LIGHT_BG })] }),
            new TableRow({ children: [cell("Domain", 2340), cell("cellshift.org (Namecheap)", 3510), cell("C$10.24/year", 3510)] }),
          ]
        }),

        new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("Product Features (MVP)")] }),
        new Paragraph({ spacing: { after: 80 }, children: [new TextRun("The MVP includes 10 core transformations, each accessible through a simple toggle interface:")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Remove Duplicates — detect and eliminate duplicate rows by any column combination")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Clean Blanks — remove empty rows/columns or fill with defaults")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Unpivot/Melt — convert wide matrices to analysis-ready long format")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Pivot & Aggregate — group by any column with sum, mean, count, min, max")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Standardize Dates — normalize mixed date formats across systems")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Split Columns — break combined fields by delimiter")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Fix Data Types — convert text-as-numbers to proper numeric format")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Conditional Flagging — flag rows matching custom business rules")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("VLOOKUP Merge — match and merge data from two files by key column")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 200 }, children: [new TextRun("Audit Trail — every download includes a log of what changed and when")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("User Flow")] }),
        new Paragraph({ spacing: { after: 100 }, children: [
          new TextRun("Upload file (.xlsx, .xls, .csv) "),
          new TextRun({ text: "→", bold: true, color: "2E75B6" }),
          new TextRun(" Auto-analysis with stats and recommendations "),
          new TextRun({ text: "→", bold: true, color: "2E75B6" }),
          new TextRun(" Toggle transformations via expanders "),
          new TextRun({ text: "→", bold: true, color: "2E75B6" }),
          new TextRun(" Before/After live preview "),
          new TextRun({ text: "→", bold: true, color: "2E75B6" }),
          new TextRun(" Download clean Excel with audit trail")
        ]}),

        // PHASE 3: APPROACH
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Phase 3: APPROACH — Go-to-Market Strategy")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Revenue Model")] }),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [1872, 1872, 1872, 1872, 1872],
          rows: [
            new TableRow({ children: [
              headerCell("", 1872), headerCell("Starter", 1872), headerCell("Pro", 1872),
              headerCell("Business", 1872), headerCell("Enterprise", 1872)
            ]}),
            new TableRow({ children: [
              cell("Price", 1872, { bold: true }), cell("$0", 1872), cell("$29/mo", 1872, { bold: true, shade: ACCENT_BG }),
              cell("$79/mo", 1872), cell("Custom", 1872)
            ]}),
            new TableRow({ children: [
              cell("Transforms/Day", 1872, { bold: true, shade: LIGHT_BG }), cell("5", 1872, { shade: LIGHT_BG }),
              cell("Unlimited", 1872, { shade: LIGHT_BG }), cell("Unlimited", 1872, { shade: LIGHT_BG }),
              cell("Unlimited", 1872, { shade: LIGHT_BG })
            ]}),
            new TableRow({ children: [
              cell("Max File Size", 1872, { bold: true }), cell("5 MB", 1872), cell("50 MB", 1872),
              cell("100 MB", 1872), cell("Unlimited", 1872)
            ]}),
            new TableRow({ children: [
              cell("VLOOKUP", 1872, { bold: true, shade: LIGHT_BG }), cell("No", 1872, { shade: LIGHT_BG, color: "DC2626" }),
              cell("Yes", 1872, { shade: LIGHT_BG, color: "16A34A" }), cell("Yes", 1872, { shade: LIGHT_BG, color: "16A34A" }),
              cell("Yes", 1872, { shade: LIGHT_BG, color: "16A34A" })
            ]}),
            new TableRow({ children: [
              cell("Audit Trail", 1872, { bold: true }), cell("No", 1872, { color: "DC2626" }),
              cell("Yes", 1872, { color: "16A34A" }), cell("Yes", 1872, { color: "16A34A" }),
              cell("Yes", 1872, { color: "16A34A" })
            ]}),
            new TableRow({ children: [
              cell("Team Seats", 1872, { bold: true, shade: LIGHT_BG }), cell("1", 1872, { shade: LIGHT_BG }),
              cell("1", 1872, { shade: LIGHT_BG }), cell("5", 1872, { shade: LIGHT_BG }),
              cell("Unlimited", 1872, { shade: LIGHT_BG })
            ]}),
          ]
        }),

        new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("Customer Acquisition Channels")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "Cold Email Outreach: ", bold: true }),
          new TextRun("Targeted sequences to Surrey construction, retail, and professional services firms sourced from Surrey Board of Trade, BC Registry, and Google Maps.")
        ]}),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "LinkedIn Content Marketing: ", bold: true }),
          new TextRun("30-day content calendar with value-first posts targeting local business owners and operations managers.")
        ]}),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "Strategic Partnerships: ", bold: true }),
          new TextRun("Bookkeepers, accountants, and IT consultants as channel partners with 20% recurring commission.")
        ]}),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "SEO & Content: ", bold: true }),
          new TextRun("Blog targeting long-tail keywords like 'clean Excel data Surrey', 'remove duplicates spreadsheet tool BC'.")
        ]}),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "Referral Program: ", bold: true }),
          new TextRun("Existing users get 1 month free Pro for each referral that converts. Simple viral loop.")
        ]}),

        new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("12-Month Launch Roadmap")] }),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2340, 3510, 3510],
          rows: [
            new TableRow({ children: [headerCell("Timeline", 2340), headerCell("Milestone", 3510), headerCell("Revenue Target", 3510)] }),
            new TableRow({ children: [cell("Month 1-2", 2340, { bold: true }), cell("MVP live, beta users, first 50 signups", 3510), cell("$0 (validation)", 3510)] }),
            new TableRow({ children: [cell("Month 3-4", 2340, { bold: true, shade: LIGHT_BG }), cell("Launch Pro tier, first 20 paying users", 3510, { shade: LIGHT_BG }), cell("$580-1,160/mo", 3510, { shade: LIGHT_BG })] }),
            new TableRow({ children: [cell("Month 5-6", 2340, { bold: true }), cell("100 paying users, Business tier launch", 3510), cell("$5,000/mo", 3510)] }),
            new TableRow({ children: [cell("Month 7-9", 2340, { bold: true, shade: LIGHT_BG }), cell("250 users, partner channel active", 3510, { shade: LIGHT_BG }), cell("$15,000/mo", 3510, { shade: LIGHT_BG })] }),
            new TableRow({ children: [cell("Month 10-12", 2340, { bold: true }), cell("500+ users, Enterprise deals, expand beyond Surrey", 3510), cell("$40,000-83,000/mo", 3510, { bold: true, color: "16A34A" })] }),
          ]
        }),

        // PHASE 4: DELIVERY
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Phase 4: DELIVERY — Operations & Infrastructure")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("AI-as-Team Operating Model")] }),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("Cellshift operates with zero traditional employees. Claude Pro ($20/month) fills every operational role:")
        ]}),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({ children: [headerCell("Role", 3120), headerCell("Responsibilities", 3120), headerCell("Traditional Cost", 3120)] }),
            new TableRow({ children: [cell("Full-Stack Developer", 3120, { bold: true }), cell("Product development, bug fixes, new features", 3120), cell("$120K/year", 3120)] }),
            new TableRow({ children: [cell("Product Manager", 3120, { bold: true, shade: LIGHT_BG }), cell("Roadmap, prioritization, user research", 3120, { shade: LIGHT_BG }), cell("$110K/year", 3120, { shade: LIGHT_BG })] }),
            new TableRow({ children: [cell("QA Engineer", 3120, { bold: true }), cell("Testing, validation, monitoring", 3120), cell("$85K/year", 3120)] }),
            new TableRow({ children: [cell("Marketing Lead", 3120, { bold: true, shade: LIGHT_BG }), cell("Content, outreach, SEO, campaigns", 3120, { shade: LIGHT_BG }), cell("$90K/year", 3120, { shade: LIGHT_BG })] }),
            new TableRow({ children: [cell("Support Agent", 3120, { bold: true }), cell("Customer inquiries, documentation", 3120), cell("$55K/year", 3120)] }),
            new TableRow({ children: [
              cell("TOTAL SAVINGS", 3120, { bold: true, shade: ACCENT_BG }),
              cell("All roles covered by Claude Pro", 3120, { shade: ACCENT_BG }),
              cell("$460K/year saved", 3120, { bold: true, shade: ACCENT_BG, color: "16A34A" })
            ] }),
          ]
        }),

        new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("Daily Monitoring Agent")] }),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("A scheduled Claude task runs every morning at 9:00 AM Pacific to check application uptime (pings the Streamlit deployment URL), review GitHub activity (recent commits, open issues), and generate a daily business health report. Any anomalies trigger immediate investigation.")
        ]}),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Financial Projections — Year 1")] }),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [4680, 4680],
          rows: [
            new TableRow({ children: [headerCell("Line Item", 4680), headerCell("Annual Amount", 4680)] }),
            new TableRow({ children: [cell("Revenue (target)", 4680, { bold: true }), cell("$500K - $1M", 4680, { bold: true, color: "16A34A" })] }),
            new TableRow({ children: [cell("Domain (cellshift.org)", 4680, { shade: LIGHT_BG }), cell("-C$10.24", 4680, { shade: LIGHT_BG })] }),
            new TableRow({ children: [cell("Claude Pro subscription", 4680), cell("-$240", 4680)] }),
            new TableRow({ children: [cell("Hosting (Streamlit Cloud)", 4680, { shade: LIGHT_BG }), cell("$0 (free tier)", 4680, { shade: LIGHT_BG, color: "16A34A" })] }),
            new TableRow({ children: [cell("Stripe fees (est. on $500K)", 4680), cell("-$14,500 + $3,600", 4680)] }),
            new TableRow({ children: [cell("Google Workspace (optional)", 4680, { shade: LIGHT_BG }), cell("-$84/year", 4680, { shade: LIGHT_BG })] }),
            new TableRow({ children: [
              cell("Total Fixed Overhead", 4680, { bold: true, shade: ACCENT_BG }),
              cell("< $500/year", 4680, { bold: true, shade: ACCENT_BG, color: "16A34A" })
            ]}),
          ]
        }),

        new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("Risk Mitigation")] }),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2340, 2340, 2340, 2340],
          rows: [
            new TableRow({ children: [headerCell("Risk", 2340), headerCell("Probability", 2340), headerCell("Impact", 2340), headerCell("Mitigation", 2340)] }),
            new TableRow({ children: [
              cell("Low initial adoption", 2340), cell("Medium", 2340, { color: "D97706" }),
              cell("High", 2340, { color: "DC2626" }), cell("Free tier removes friction; local outreach", 2340)
            ]}),
            new TableRow({ children: [
              cell("Competitor copies model", 2340, { shade: LIGHT_BG }), cell("Low", 2340, { shade: LIGHT_BG, color: "16A34A" }),
              cell("Medium", 2340, { shade: LIGHT_BG, color: "D97706" }), cell("Speed + local trust = moat", 2340, { shade: LIGHT_BG })
            ]}),
            new TableRow({ children: [
              cell("Streamlit scaling limits", 2340), cell("Medium", 2340, { color: "D97706" }),
              cell("Medium", 2340, { color: "D97706" }), cell("Migrate to cloud VM at scale", 2340)
            ]}),
            new TableRow({ children: [
              cell("Data privacy incident", 2340, { shade: LIGHT_BG }), cell("Low", 2340, { shade: LIGHT_BG, color: "16A34A" }),
              cell("Critical", 2340, { shade: LIGHT_BG, color: "DC2626" }), cell("In-memory only; PIPEDA compliant", 2340, { shade: LIGHT_BG })
            ]}),
          ]
        }),

        new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("Legal & Compliance")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "PIPEDA Compliance: ", bold: true }), new TextRun("All file processing is in-memory only. No user data is stored, logged, or transmitted to third parties.")
        ]}),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "Jurisdiction: ", bold: true }), new TextRun("British Columbia, Canada. Disputes resolved in Surrey courts.")
        ]}),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "Privacy Policy: ", bold: true }), new TextRun("Published at cellshift.org/privacy — cookie-free analytics via Plausible.")
        ]}),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "Terms of Service: ", bold: true }), new TextRun("Published at cellshift.org/terms — covers acceptable use, liability, and pricing terms.")
        ]}),

        // CLOSING
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Next Steps — Immediate Actions")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "Register domain: ", bold: true }), new TextRun("cellshift.org via Namecheap (C$10.24/year)")
        ]}),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "Create GitHub repository: ", bold: true }), new TextRun("Push app.py, requirements.txt, README.md")
        ]}),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "Deploy on Streamlit Cloud: ", bold: true }), new TextRun("Connect GitHub repo, configure deployment")
        ]}),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "Set up Google Workspace: ", bold: true }), new TextRun("hello@cellshift.org for professional email")
        ]}),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "Begin outreach: ", bold: true }), new TextRun("Send first 50 cold emails to Surrey construction firms")
        ]}),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "Launch LinkedIn: ", bold: true }), new TextRun("Post day 1 of 30-day content calendar")
        ]}),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
          new TextRun({ text: "Set up Stripe: ", bold: true }), new TextRun("Configure payment processing for Pro and Business tiers")
        ]}),

        new Paragraph({ spacing: { before: 400 }, border: { top: { style: BorderStyle.SINGLE, size: 3, color: "2E75B6", space: 8 } }, children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [
          new TextRun({ text: "Cellshift — Shift your data. Shift your business.", font: "Arial", size: 24, bold: true, color: "1B2A4A", italics: true })
        ]}),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/sessions/epic-determined-franklin/mnt/outputs/Company_Blueprint.docx", buffer);
  console.log("Company_Blueprint.docx created successfully");
});
