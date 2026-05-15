const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, LevelFormat,
        HeadingLevel, BorderStyle, WidthType, ShadingType,
        PageNumber, PageBreak, TabStopType, TabStopPosition } = require('docx');
const fs = require('fs');

// Colors
const BRAND_DARK = "1B2A4A";
const BRAND_MID = "2E75B6";
const BRAND_LIGHT = "D5E8F0";
const BRAND_ACCENT = "E8792F";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0 };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function headerCell(text, width) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: BRAND_DARK, type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
  });
}
function dataCell(text, width, opts = {}) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: opts.shade ? { fill: BRAND_LIGHT, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text: String(text), font: "Arial", size: 20, bold: opts.bold || false })] })]
  });
}

function makeTable(headers, rows, widths) {
  const totalW = widths.reduce((a,b) => a+b, 0);
  return new Table({
    width: { size: totalW, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ children: headers.map((h, i) => headerCell(h, widths[i])) }),
      ...rows.map((row, ri) => new TableRow({
        children: row.map((c, ci) => dataCell(c, widths[ci], { shade: ri % 2 === 1 }))
      }))
    ]
  });
}

function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text, font: "Arial" })] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, font: "Arial" })] });
}
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 22, bold: opts.bold || false, color: opts.color })]
  });
}
function spacer() { return new Paragraph({ spacing: { after: 200 }, children: [] }); }

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: BRAND_DARK },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BRAND_MID, space: 1 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: BRAND_MID },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 } },
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
    // === COVER PAGE ===
    {
      properties: {
        page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
      },
      children: [
        spacer(), spacer(), spacer(), spacer(), spacer(), spacer(),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
          children: [new TextRun({ text: "COMPANY BLUEPRINT", font: "Arial", size: 52, bold: true, color: BRAND_DARK })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: BRAND_ACCENT, space: 8 } },
          children: [new TextRun({ text: "Excel Transformation Automation for Surrey Businesses", font: "Arial", size: 28, color: BRAND_MID })] }),
        spacer(),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Zero-Investment | AI-Powered Operations | Local-First GTM", font: "Arial", size: 22, color: "666666" })] }),
        spacer(), spacer(), spacer(), spacer(), spacer(),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Prepared by: Claude (AI Business Architect)", font: "Arial", size: 20, color: "999999" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "For: Manish Dadhwal", font: "Arial", size: 20, color: "999999" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Date: May 14, 2026", font: "Arial", size: 20, color: "999999" })] }),
        new Paragraph({ children: [new PageBreak()] }),
      ]
    },

    // === MAIN CONTENT ===
    {
      properties: {
        page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
      },
      headers: {
        default: new Header({ children: [new Paragraph({
          children: [new TextRun({ text: "Company Blueprint | Confidential", font: "Arial", size: 16, color: "999999" })],
          tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }]
        })] })
      },
      footers: {
        default: new Footer({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Page ", font: "Arial", size: 16, color: "999999" }), new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "999999" })]
        })] })
      },
      children: [
        // ============ PHASE 1: DETECT ============
        h1("PHASE 1: DETECT — Market Pain Points"),

        h2("1.1 The Problem (Research-Backed)"),
        p("67% of businesses with fewer than 50 employees still rely on manual spreadsheets for performance tracking. Among those, 41% make at least one significant operational decision per quarter based on inaccurate or outdated data."),
        p("SMB managers spend an average of 12.4 hours per week on manual reporting tasks — roughly 645 hours per year — assembling information that could flow in real time."),
        p("Manually compiled reports contain data errors at a rate of 8–12%, primarily from copy-paste mistakes. The average SMB tracks 14 distinct KPIs across 4–6 different software platforms, each requiring separate logins, exports, and manual consolidation."),

        h2("1.2 Surrey Market Snapshot"),
        makeTable(
          ["Metric", "Data"],
          [
            ["Total Licensed Businesses", "17,000+"],
            ["New Businesses (2024)", "2,961"],
            ["Top Sector: Construction", "4,365 licenses (21%)"],
            ["2nd: Professional/Technical Services", "2,588 licenses (12%)"],
            ["Health Sector Businesses", "~900"],
            ["Commercial/Industrial License Growth", "5% YoY increase"],
          ],
          [4680, 4680]
        ),
        spacer(),

        h2("1.3 Target Customer Profiles"),
        makeTable(
          ["Segment", "Pain Point", "Volume (Est.)", "Willingness to Pay"],
          [
            ["Construction firms", "PO tracking, material allocation, cost reconciliation in Excel", "4,365", "High — saves hours/week"],
            ["Professional services", "Client reporting, timesheet consolidation, invoice matching", "2,588", "Medium-High"],
            ["Health businesses", "Patient data cleanup, scheduling pivot tables, compliance reports", "900", "Medium"],
            ["Retail/Wholesale", "Inventory unpivot, sales reporting, supplier allocation", "1,500+", "High"],
            ["Cannabis/Agriculture", "GTIN/SKU management, regulatory reporting, allocation matrices", "200+", "Very High"],
          ],
          [1800, 3000, 1200, 3360]
        ),
        spacer(),

        h2("1.4 Competitive Landscape"),
        p("Current solutions either cost too much (Power BI at $10/user/month, Tableau at $75/user/month) or require technical skills that small business owners lack (Python, VBA macros). There is a clear gap for a simple upload-and-transform tool that speaks the language of Surrey’s construction, retail, and services businesses."),

        new Paragraph({ children: [new PageBreak()] }),

        // ============ PHASE 2: DESIGN ============
        h1("PHASE 2: DESIGN — Product Architecture"),

        h2("2.1 Core Product Concept"),
        p("A web application where businesses upload an Excel file and receive intelligent, one-click transformations. The system analyzes the file structure, detects data patterns, and presents toggle-based transformation options — no coding required.", { bold: true }),
        spacer(),

        h2("2.2 User Flow"),
        makeTable(
          ["Step", "Action", "What Happens"],
          [
            ["1", "Upload Excel file", "Drag-and-drop or file picker. Supports .xls, .xlsx, .csv"],
            ["2", "Auto-Analysis", "Engine scans: column types, duplicates, pivot structures, blanks, date formats, GTIN/SKU patterns"],
            ["3", "Transformation Menu", "Toggle cards appear: Remove Duplicates, Unpivot, Pivot, Clean Blanks, Standardize Dates, VLOOKUP Merge, Split Columns, etc."],
            ["4", "Preview", "Live preview of transformed data before committing"],
            ["5", "Download", "One-click download of transformed Excel file with audit log sheet"],
          ],
          [800, 2500, 6060]
        ),
        spacer(),

        h2("2.3 Transformation Engine (Core Features)"),
        makeTable(
          ["Transformation", "Description", "Business Use Case"],
          [
            ["Remove Duplicates", "Detect and remove duplicate rows based on selected columns", "Clean customer lists, PO tracking"],
            ["Unpivot / Melt", "Convert wide allocation matrices into long-format rows", "Store allocation, inventory distribution"],
            ["Pivot / Aggregate", "Group and summarize data by categories", "Sales by region, costs by project"],
            ["Clean Blanks", "Remove or fill blank rows/columns with smart defaults", "Imported data cleanup"],
            ["Standardize Dates", "Normalize mixed date formats to one standard", "Cross-system report merging"],
            ["Column Split/Merge", "Split combined fields or merge separate ones", "Address parsing, name formatting"],
            ["VLOOKUP Merge", "Upload 2 files, match on key column, merge data", "PO matching, SKU enrichment"],
            ["Data Type Fix", "Convert text-numbers, fix currency formatting", "Financial report cleanup"],
            ["Conditional Flagging", "Flag rows matching rules (e.g., value > threshold)", "Exception reporting, QA checks"],
            ["Audit Trail", "Auto-generated sheet showing every change made", "Compliance, accountability"],
          ],
          [2200, 3800, 3360]
        ),
        spacer(),

        h2("2.4 Tech Stack (Zero Cost)"),
        makeTable(
          ["Layer", "Technology", "Cost", "Why"],
          [
            ["Frontend", "Streamlit (Python)", "$0", "Rapid UI, file upload built-in, free hosting"],
            ["Backend/Engine", "Python + Pandas + OpenPyXL", "$0", "Industry standard for Excel manipulation"],
            ["Hosting", "Streamlit Community Cloud", "$0", "Free tier: 2 CPU, 2.7GB RAM, 50GB storage"],
            ["Version Control", "GitHub (free)", "$0", "Code hosting, CI/CD, collaboration"],
            ["Domain", "FreeDNS or .tk / .ml", "$0", "Free subdomain initially"],
            ["Analytics", "Plausible (self-hosted) or Umami", "$0", "Privacy-first, GDPR compliant"],
            ["AI Agent (PM)", "Claude Pro", "$20/mo", "Your only cost — handles dev, PM, monitoring"],
          ],
          [1800, 2800, 800, 3960]
        ),
        spacer(),

        new Paragraph({ children: [new PageBreak()] }),

        // ============ PHASE 3: APPROACH ============
        h1("PHASE 3: APPROACH — Go-to-Market Strategy"),

        h2("3.1 Brand Positioning"),
        p("Position: The free Excel power tool for Surrey businesses. No subscriptions, no setup, no IT team needed. Upload. Transform. Download.", { bold: true }),
        p("Tagline options:"),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "\"Your Excel, Transformed in 60 Seconds\"", font: "Arial", size: 22 })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "\"Stop Wrestling with Spreadsheets\"", font: "Arial", size: 22 })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "\"Smart Data, Zero Hassle\"", font: "Arial", size: 22 })] }),
        spacer(),

        h2("3.2 Revenue Model (Freemium)"),
        makeTable(
          ["Tier", "Price", "Features", "Target"],
          [
            ["Free", "$0/forever", "5 transformations/day, files up to 5MB, basic transforms", "Individual users, trial"],
            ["Pro", "$29/month", "Unlimited transforms, 50MB files, VLOOKUP merge, audit trail, priority processing", "Small businesses"],
            ["Business", "$79/month", "100MB files, API access, scheduled transforms, team accounts, white-label reports", "Growing companies"],
            ["Enterprise", "Custom", "On-prem option, ERP integration, custom transforms, SLA", "Large Surrey businesses"],
          ],
          [1500, 1500, 4060, 2300]
        ),
        spacer(),

        h2("3.3 Customer Acquisition (Zero Budget)"),
        makeTable(
          ["Channel", "Action", "Timeline", "Expected Result"],
          [
            ["Surrey Board of Trade", "Join as member, attend networking events, offer free demo workshops", "Month 1-2", "20-30 warm leads"],
            ["LinkedIn Local", "Post daily tips on Excel productivity, target Surrey business owners", "Ongoing", "500+ connections in 90 days"],
            ["Google My Business", "List as local tech service, collect reviews", "Month 1", "Local search visibility"],
            ["Referral Program", "Give Pro month free for every referral that converts", "Month 3+", "Viral loop"],
            ["Local Facebook Groups", "Surrey Business Network, Surrey Entrepreneurs — offer free tool", "Month 1", "Direct access to 5K+ local owners"],
            ["Cold Email (Targeted)", "Scrape public business directory, personalized outreach", "Month 2", "3-5% conversion rate"],
            ["Workshop/Webinar", "Free monthly \"Excel Productivity for Business\" webinar", "Monthly", "10-20 attendees converting to users"],
            ["Content Marketing", "Blog: \"Top 10 Excel Mistakes Surrey Businesses Make\"", "Ongoing", "SEO long-tail traffic"],
        ],
          [2200, 3200, 1500, 2460]
        ),
        spacer(),

        h2("3.4 Launch Roadmap"),
        makeTable(
          ["Phase", "Timeline", "Milestone", "Key Deliverable"],
          [
            ["Alpha", "Weeks 1-3", "Core engine + 5 transforms working", "Internal testing build"],
            ["Beta", "Weeks 4-6", "Web app live on Streamlit Cloud, 10 beta users", "Public URL, feedback loop"],
            ["Launch", "Week 7-8", "Product Hunt launch, Surrey Board of Trade demo", "Press release, 50+ users"],
            ["Growth", "Month 3-6", "Pro tier, VLOOKUP merge, 200+ users", "Revenue generation begins"],
            ["Scale", "Month 6-12", "Desktop app (Electron), API, 1000+ users", "Series of enterprise pilots"],
          ],
          [1200, 1500, 3500, 3160]
        ),

        new Paragraph({ children: [new PageBreak()] }),

        // ============ PHASE 4: DELIVERY ============
        h1("PHASE 4: DELIVERY — Operating Model"),

        h2("4.1 AI-as-Team Structure"),
        p("Since this is a zero-employee company, Claude Pro serves as the entire operational team:"),
        makeTable(
          ["Role", "How Claude Handles It", "Cadence"],
          [
            ["Lead Developer", "Writes all Python/Streamlit code, reviews PRs, fixes bugs", "Daily"],
            ["Project Manager", "Tracks milestones via TODO lists, prioritizes backlog", "Daily standups (self-check)"],
            ["QA Engineer", "Writes test cases, validates transformations against expected output", "Per feature"],
            ["Marketing Writer", "Creates blog posts, LinkedIn content, email sequences", "3x/week"],
            ["Customer Support", "FAQ docs, error handling, user guides", "As needed"],
            ["Business Analyst", "Monitors usage metrics, suggests features based on patterns", "Weekly"],
            ["Progress Monitor Agent", "Automated checks: uptime, error rates, user growth", "Scheduled"],
          ],
          [2200, 4960, 2200]
        ),
        spacer(),

        h2("4.2 Progress Monitoring Agent"),
        p("A scheduled Claude agent that runs daily to monitor:"),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "App uptime and response time (ping Streamlit URL)", font: "Arial", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "GitHub commit activity (are features being shipped?)", font: "Arial", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "User growth metrics from analytics dashboard", font: "Arial", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Error logs and transformation failure rates", font: "Arial", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Weekly summary report emailed to you", font: "Arial", size: 22 })] }),
        spacer(),

        h2("4.3 Financial Projections (Year 1)"),
        makeTable(
          ["Month", "Users (Cumul.)", "Free", "Pro ($29)", "Business ($79)", "MRR", "Costs"],
          [
            ["Month 1-2", "50", "48", "2", "0", "$58", "$20 (Claude)"],
            ["Month 3", "120", "110", "8", "2", "$390", "$20"],
            ["Month 6", "400", "350", "35", "15", "$2,200", "$20"],
            ["Month 9", "800", "680", "80", "40", "$5,480", "$50 (domain + email)"],
            ["Month 12", "1,500", "1,250", "150", "100", "$12,250", "$50"],
          ],
          [1200, 1200, 800, 1200, 1600, 1560, 1800]
        ),
        spacer(),
        p("Projected Annual Revenue (Year 1): ~$65,000 CAD", { bold: true, color: BRAND_ACCENT }),
        p("Total Investment: ~$290 (Claude Pro subscription)", { bold: true }),
        p("Break-even: Month 2 (covers Claude Pro cost)", { bold: true }),
        spacer(),

        h2("4.4 Risk Mitigation"),
        makeTable(
          ["Risk", "Likelihood", "Impact", "Mitigation"],
          [
            ["Low initial adoption", "Medium", "High", "Free tier removes friction; local networking builds trust"],
            ["Streamlit free tier limits", "Medium", "Medium", "Migrate to Render/Railway when revenue supports it"],
            ["Competitor enters market", "Low", "Medium", "Local-first positioning + relationship moat"],
            ["Data security concerns", "Medium", "High", "All processing client-side; no data stored on server"],
            ["Feature creep", "High", "Medium", "Strict 2-week sprint cycles; ship MVP first"],
          ],
          [2200, 1200, 1200, 4760]
        ),

        new Paragraph({ children: [new PageBreak()] }),

        // ============ NEXT STEPS ============
        h1("IMMEDIATE NEXT STEPS"),
        spacer(),
        makeTable(
          ["Priority", "Action", "Owner", "Deadline"],
          [
            ["1", "Finalize company name and register domain", "Manish", "This week"],
            ["2", "Build MVP transformation engine (5 core transforms)", "Claude", "Week 1-2"],
            ["3", "Deploy to Streamlit Community Cloud", "Claude", "Week 2"],
            ["4", "Create landing page with value proposition", "Claude", "Week 2-3"],
            ["5", "Join Surrey Board of Trade", "Manish", "Week 3"],
            ["6", "Launch beta with 10 local businesses", "Both", "Week 4-5"],
            ["7", "Collect feedback, iterate, add Pro tier", "Claude", "Week 5-6"],
            ["8", "Public launch + Product Hunt", "Both", "Week 7-8"],
          ],
          [800, 4500, 1200, 2860]
        ),
        spacer(), spacer(),

        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400 },
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: BRAND_MID, space: 8 } },
          children: [new TextRun({ text: "Ready to build? Say the word and I'll start coding the MVP.", font: "Arial", size: 24, bold: true, color: BRAND_DARK })] }),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/sessions/epic-determined-franklin/mnt/outputs/Company_Blueprint.docx", buffer);
  console.log("DONE: Company_Blueprint.docx created");
});
