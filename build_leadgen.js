const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cm = { top: 80, bottom: 80, left: 120, right: 120 };
const LB = "EBF2FA";

function h(text, w) {
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA },
    shading: { fill: "1B2A4A", type: ShadingType.CLEAR }, margins: cm,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })] });
}
function d(text, w, o) {
  o = o || {};
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA },
    shading: o.s ? { fill: o.s, type: ShadingType.CLEAR } : undefined, margins: cm,
    children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 20, bold: o.b, color: o.c, italics: o.i })] })] });
}

var calRows = [
  ["1","Pain Point","Time wasted on spreadsheets","I watched a PM spend 4 hours copy-pasting between Excel files..."],
  ["2","How-To","Remove duplicates without formulas","Here is how to clean 10,000 rows in 60 seconds (no VBA):"],
  ["3","Story","Why I built Cellshift","Every business in Surrey runs on Excel. But nobody loves it."],
  ["4","Stat","12.4 hrs/week on manual data work","The average SMB manager loses 12 hours a week to spreadsheets."],
  ["5","Soft CTA","Free tool announcement","We just launched a free Excel cleanup tool for Surrey businesses."],
  ["8","Pain Point","VLOOKUP errors cost real money","A $14K billing error. Caused by one wrong VLOOKUP."],
  ["9","How-To","Unpivot data without pivot tables","Your supplier sent a wide matrix. Here is how to fix it:"],
  ["10","Testimonial","Beta user feedback","It saved me 3 hours this week. - Surrey retail manager"],
  ["11","Industry","Construction data challenges","Construction PMs in Surrey: your PO spreadsheets are fixable."],
  ["12","Value","5 Excel mistakes costing you money","These 5 spreadsheet habits are silently eating your margins:"],
  ["15","Story","Surrey business ecosystem","17,000 businesses in Surrey. Most run on spreadsheets."],
  ["16","How-To","Standardize date formats","MM/DD vs DD/MM broke your report? Here is the fix:"],
  ["17","Social Proof","User count milestone","50 Surrey businesses now use Cellshift. Here is what we learned:"],
  ["18","Pain Point","Manual reporting kills weekends","Friday at 4 PM. Your boss needs the report. Your data is a mess."],
  ["19","Soft CTA","Free vs paid comparison","What you get for $0 vs $29/month with Cellshift:"],
  ["22","Value","Data quality checklist","Before you send that report, check these 7 things:"],
  ["23","Industry","Retail inventory challenges","Multi-location inventory in Excel? Stop suffering."],
  ["24","How-To","Merge two Excel files by key","VLOOKUP alternative: match and merge in 3 clicks:"],
  ["25","Story","Behind the scenes of building","Building a SaaS with $0 investment. Week 4 update:"],
  ["26","Soft CTA","Partner program launch","Bookkeepers and accountants: earn 20% recurring commission."],
  ["29","Value","Month-end close automation","Month-end close in Excel? Here is your cleanup shortcut."],
  ["30","Milestone","Month 1 recap + next steps","30 days of Cellshift. Here is what happened:"]
];

var calTableRows = [new TableRow({ children: [h("Day",1170), h("Type",1560), h("Topic",3120), h("Hook / First Line",3510)] })];
calRows.forEach(function(row, i) {
  var bg = i % 2 ? LB : undefined;
  calTableRows.push(new TableRow({ children: [
    d(row[0],1170,{b:true,s:bg}), d(row[1],1560,{s:bg}), d(row[2],3120,{s:bg}), d(row[3],3510,{s:bg,i:true})
  ]}));
});

var doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: "1B2A4A" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 } },
    ]
  },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ]},
  sections: [
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      children: [
        new Paragraph({ spacing: { before: 3000 }, children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [
          new TextRun({ text: "CELLSHIFT", font: "Arial", size: 72, bold: true, color: "1B2A4A" }) ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [
          new TextRun({ text: "Lead Generation Playbook", font: "Arial", size: 36, color: "2E75B6" }) ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [
          new TextRun({ text: "Cold Email Templates, Follow-Up Sequences & Content Calendar", font: "Arial", size: 22, color: "64748B", italics: true }) ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, border: { top: { style: BorderStyle.SINGLE, size: 3, color: "2E75B6", space: 8 } }, children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400 }, children: [
          new TextRun({ text: "Version 1.0 | May 2026", font: "Arial", size: 20, color: "64748B" }) ]}),
      ]
    },
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      headers: { default: new Header({ children: [new Paragraph({
        children: [new TextRun({ text: "Cellshift -- Lead Generation Playbook", font: "Arial", size: 16, color: "94A3B8", italics: true })],
        border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: "E2E8F0", space: 4 } }
      })] }) },
      footers: { default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "Cellshift Confidential | Page ", font: "Arial", size: 16, color: "94A3B8" }),
          new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "94A3B8" }),
        ]
      })] }) },
      children: [
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Cold Email Templates")] }),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("Three industry-specific templates for Surrey businesses. Each follows the AIDA framework and keeps the ask small: try the free tool, not buy a subscription.")
        ]}),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Template 1: Construction Sector")] }),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun({ text: "Subject: ", bold: true }), new TextRun("Your Friday PO spreadsheet cleanup? We automated it.") ]}),
        new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Hi {FirstName},", italics: true })] }),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun("I know this sounds specific, but most construction PMs in Surrey spend Friday afternoons cleaning up purchase order spreadsheets -- matching PO numbers, removing duplicate line items, reconciling subcontractor billing.") ]}),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun("We built Cellshift to do that in under 60 seconds. Upload your Excel file, toggle the cleanup you need (remove duplicates, merge data from two files, fix date formats), and download the clean version. No formulas. No macros.") ]}),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun({ text: "Free to try: ", bold: true }), new TextRun("[link]") ]}),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("If it saves you even one hour this week, that is a win.\n\nBest,\nManish\nCellshift | cellshift.org") ]}),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Template 2: Retail / Wholesale")] }),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun({ text: "Subject: ", bold: true }), new TextRun("Matching supplier invoices to POs without VLOOKUP nightmares") ]}),
        new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Hi {FirstName},", italics: true })] }),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun("Quick question: how many hours does your team spend each week matching SKUs across supplier spreadsheets, reconciling inventory counts, or fixing the date formats that every system exports differently?") ]}),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun("Cellshift does all of that automatically. Upload two files, pick the match column, and merge the data -- no VLOOKUP formulas, no #N/A errors.") ]}),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun({ text: "Free to try, no signup needed: ", bold: true }), new TextRun("[link]") ]}),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("Worth 60 seconds to see if it fits your workflow.\n\nManish\nCellshift | cellshift.org") ]}),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Template 3: Professional Services")] }),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun({ text: "Subject: ", bold: true }), new TextRun("Your bookkeeper sends reports in 4 different date formats. We fix that.") ]}),
        new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Hi {FirstName},", italics: true })] }),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun("Every accounting firm in Surrey has the same problem: client data arrives in a dozen different formats. QuickBooks exports, bank CSVs, payroll reports -- each with different date conventions and data quirks.") ]}),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun("Cellshift standardizes all of it in one upload. Normalize dates, clean blank rows, split merged columns, and flag exceptions -- all with simple toggles.") ]}),
        new Paragraph({ spacing: { after: 80 }, children: [
          new TextRun({ text: "Try it free: ", bold: true }), new TextRun("[link]") ]}),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("Happy to jump on a 10-minute call if it looks useful.\n\nManish\nCellshift | cellshift.org") ]}),

        // FOLLOW-UP
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Follow-Up Email Sequence")] }),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("After the initial cold email, follow up 4 times over 3 weeks. Each adds new value rather than just checking in.") ]}),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [1170, 1560, 2340, 4290],
          rows: [
            new TableRow({ children: [h("Email",1170), h("Timing",1560), h("Subject Line",2340), h("Core Message",4290)] }),
            new TableRow({ children: [d("#1",1170,{b:true}), d("Day 0",1560), d("(initial cold email)",2340,{i:true}), d("Industry-specific pain + free CTA",4290)] }),
            new TableRow({ children: [d("#2",1170,{b:true,s:LB}), d("Day 3",1560,{s:LB}), d("Quick follow-up + use case",2340,{s:LB}), d("Share concrete example: one Surrey contractor saved 6 hrs/week",4290,{s:LB})] }),
            new TableRow({ children: [d("#3",1170,{b:true}), d("Day 7",1560), d("Would a 2-min video help?",2340), d("Offer a short Loom demo tailored to their industry",4290)] }),
            new TableRow({ children: [d("#4",1170,{b:true,s:LB}), d("Day 14",1560,{s:LB}), d("Last one + free resource",2340,{s:LB}), d("Attach a free Excel Cleanup Checklist PDF",4290,{s:LB})] }),
            new TableRow({ children: [d("#5",1170,{b:true}), d("Day 21",1560), d("Breaking up (with value)",2340), d("Final touch. Here is the free tool link if you ever need it.",4290)] }),
          ]
        }),

        // LINKEDIN CALENDAR
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("30-Day LinkedIn Content Calendar")] }),
        new Paragraph({ spacing: { after: 200 }, children: [
          new TextRun("Post 5 days a week (Mon-Fri). Mix of value posts, stories, and soft CTAs.") ]}),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [1170, 1560, 3120, 3510],
          rows: calTableRows
        }),

        // LEAD SOURCES
        new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Surrey Business Lead Sources")] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("All free sources for building targeted outreach lists:")] }),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({ children: [h("Source",3120), h("What You Get",3120), h("Best For",3120)] }),
            new TableRow({ children: [d("Surrey Board of Trade Directory",3120,{b:true}), d("Business name, category, contact",3120), d("High-quality local leads",3120)] }),
            new TableRow({ children: [d("BC Registry",3120,{b:true,s:LB}), d("Registered company details",3120,{s:LB}), d("Verifying company status",3120,{s:LB})] }),
            new TableRow({ children: [d("Google Maps Search",3120,{b:true}), d("Name, phone, website, reviews",3120), d("Finding active businesses",3120)] }),
            new TableRow({ children: [d("LinkedIn Sales Navigator",3120,{b:true,s:LB}), d("Decision-maker names/titles",3120,{s:LB}), d("Finding the right person",3120,{s:LB})] }),
            new TableRow({ children: [d("Industry Canada",3120,{b:true}), d("Federal business registry",3120), d("Cross-referencing info",3120)] }),
            new TableRow({ children: [d("Surrey Business Licence Open Data",3120,{b:true,s:LB}), d("Active licences in Surrey",3120,{s:LB}), d("Comprehensive local coverage",3120,{s:LB})] }),
            new TableRow({ children: [d("Yelp / Yellow Pages",3120,{b:true}), d("Business listings with categories",3120), d("Quick sector-based filtering",3120)] }),
          ]
        }),

        // PARTNERSHIP
        new Paragraph({ spacing: { before: 400 }, heading: HeadingLevel.HEADING_1, children: [new TextRun("Partnership & Referral Strategy")] }),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Channel Partner Program")] }),
        new Paragraph({ spacing: { after: 100 }, children: [
          new TextRun("Target: bookkeepers, accountants, IT consultants who serve Surrey SMBs. They already handle their clients Excel problems.") ]}),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "Commission: ", bold: true }), new TextRun("20% recurring on all referred subscriptions") ]}),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "Partner Dashboard: ", bold: true }), new TextRun("Track referrals, commissions, and client usage") ]}),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "Co-Marketing: ", bold: true }), new TextRun("Joint LinkedIn posts, case studies, and webinars") ]}),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "Target: ", bold: true }), new TextRun("10 active partners by month 6") ]}),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("User Referral Program")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "Referrer: ", bold: true }), new TextRun("1 month free Pro for each paid conversion") ]}),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "Referee: ", bold: true }), new TextRun("Extended 30-day free trial (instead of 14)") ]}),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
          new TextRun({ text: "Viral Mechanic: ", bold: true }), new TextRun("Share link embedded in every downloaded file footer") ]}),

        new Paragraph({ spacing: { before: 400 }, border: { top: { style: BorderStyle.SINGLE, size: 3, color: "2E75B6", space: 8 } }, children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [
          new TextRun({ text: "Cellshift -- Shift your data. Shift your business.", font: "Arial", size: 24, bold: true, color: "1B2A4A", italics: true }) ]}),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(function(buffer) {
  fs.writeFileSync("/sessions/epic-determined-franklin/mnt/outputs/Lead_Generation_Playbook.docx", buffer);
  console.log("Lead_Generation_Playbook.docx created successfully");
});
