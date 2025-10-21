# 📎 Proof Management System Guide

## Overview
The TEDx Finance Hub now includes a comprehensive proof management system that allows users to upload proof documents (receipts, invoices, agreements) for transactions and sponsors, and automatically includes them in export reports for submission.

---

## 🎯 Features

### 1. **Upload Proof Documents**
- **Transaction Proofs**: Upload receipts/invoices when adding transactions
- **Sponsor Agreements**: Upload signed agreements when adding sponsors
- **Supported Formats**: Images (JPG, PNG, GIF), PDFs, and other documents
- **Automatic Storage**: Files organized in `media/proofs/` and `media/sponsors/` folders

### 2. **View Proof Documents**
- **Desktop Table View**: 
  - Image thumbnails (64x64px) with hover zoom effect
  - PDF/document icons for non-image files
  - Click to open full proof in new tab
  - Shown in dedicated "Proof" column (visible on XL screens)

- **Mobile Card View**:
  - Image preview (80x80px) below transaction details
  - File indicator badge for PDFs/documents
  - Direct tap to view full proof

- **Actions Column**:
  - Purple eye icon for quick proof viewing
  - Available on all screen sizes

### 3. **Export with Proofs**

#### **📊 Excel Export** (Standard)
- Transaction data with "Proof File" column
- Shows filename or "No proof uploaded"
- Does NOT include actual image files

#### **📄 PDF Export** (Standard)
- Formatted transaction report
- Proof filenames referenced
- Does NOT embed images (xhtml2pdf limitation)

#### **🗜️ ZIP Export with Proofs** (NEW! ⭐)
This is the **recommended export method for submission** as it includes all proof files.

**What's Included:**
```
tedx_report_with_proofs_20250121_143022.zip
├── tedx_transactions_20250121_143022.xlsx (Excel report)
├── README.txt (Export information)
└── proofs/
    ├── Marketing_Materials_2025-01-15/
    │   └── proof.jpg
    ├── Speaker_Travel_2025-01-20/
    │   └── proof.pdf
    └── Venue_Booking_2025-02-01/
        └── proof.png
```

**File Structure:**
- Each transaction with a proof gets its own folder
- Folder naming: `TransactionTitle_Date`
- Original file extensions preserved
- Only approved transactions included

**Export Process:**
1. Go to Dashboard → Click "Export Report ▼"
2. Select "ZIP with Proofs 📎"
3. Download starts automatically
4. Extract ZIP to access Excel + all proofs

---

## 📋 Usage Examples

### Example 1: Submit Monthly Report
**Scenario**: Finance team needs to submit proof of all expenses to management.

**Steps:**
1. Filter transactions by date range (e.g., January 2025)
2. Click "Export Report ▼" → "ZIP with Proofs 📎"
3. Download `tedx_report_with_proofs_20250121.zip`
4. Submit entire ZIP file to management
5. Management can:
   - Review Excel for transaction summary
   - Verify each proof in organized folders
   - Cross-reference amounts with receipts

### Example 2: Audit Compliance
**Scenario**: External auditor requests proof documents for specific categories.

**Steps:**
1. Go to "Transactions Table" page
2. Filter by category (e.g., "Marketing")
3. Export filtered results with proofs
4. Auditor receives:
   - Excel with all marketing transactions
   - Individual proof folders for each expense
   - README explaining structure

### Example 3: Sponsor Report
**Scenario**: Create report showing all sponsorships with signed agreements.

**Steps:**
1. Filter by date range covering sponsorship period
2. Export ZIP with proofs
3. Sponsor agreements are in separate folders
4. Use for financial reconciliation

---

## 🎨 Visual Indicators

### Proof Status Icons
| Icon | Meaning | Action |
|------|---------|--------|
| 🖼️ Thumbnail | Image proof uploaded | Click to view full image |
| 📄 Blue badge | PDF/document uploaded | Click to view document |
| 👁️ Purple eye | Quick view action | Opens proof in new tab |
| ❌ "No proof" | No file uploaded | Upload via edit transaction |

### Export Options
| Option | Icon | Color | Contents |
|--------|------|-------|----------|
| Excel Report | 📊 | Green | Spreadsheet only |
| PDF Report | 📄 | Red | Formatted report only |
| ZIP with Proofs | 🗜️ | Blue | Excel + all proof files |

---

## 🔧 Technical Details

### File Storage
```python
# Django settings
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File paths
Transaction proofs: media/proofs/filename.ext
Sponsor agreements: media/sponsors/filename.ext
```

### ZIP Export Algorithm
1. **Query approved transactions** (with optional date filtering)
2. **Generate Excel report** with proof filename column
3. **Create in-memory ZIP** using zipfile module
4. **Iterate through transactions**:
   - Skip if no proof file
   - Sanitize transaction title for folder name
   - Create folder: `proofs/Title_Date/`
   - Copy proof file to folder
5. **Add README.txt** with export metadata
6. **Return ZIP response** as downloadable attachment

### Image Detection Logic
```django
{% if tx.proof.name|lower|slice:"-4:" in ".jpg,.png,.gif.jpeg" or tx.proof.name|lower|slice:"-5:" == ".jpeg" %}
    <!-- Show image thumbnail -->
{% else %}
    <!-- Show document icon -->
{% endif %}
```

### Security
- Only approved transactions exported
- Proof files protected by Django authentication
- File upload validation in forms
- Sanitized filenames in ZIP export

---

## 📊 Statistics

**Export Summary Example:**
```
✅ Exported 45 transactions with 38 proof files!
```

**README.txt Contents:**
```
TEDx Finance Report with Proofs
=====================================

Export Date: 2025-01-21 14:30:22
Date Range: 2025-01-01 to 2025-01-31

Contents:
---------
1. tedx_transactions_20250121_143022.xlsx - Full transaction report
2. proofs/ folder - 38 proof images organized by transaction

File Structure:
---------------
proofs/
  ├── TransactionTitle_Date/
  │   └── proof.jpg (or .pdf, .png, etc.)
  └── ...

Notes:
------
- Only approved transactions are included
- Proof images are organized by transaction title and date
- If a transaction has no proof, it won't appear in the proofs folder
- All amounts are in Indian Rupees (₹)
```

---

## 🚀 Quick Reference

### Uploading Proofs
1. Add/Edit Transaction → Choose proof file → Save
2. Supported: JPG, PNG, PDF, GIF, etc.
3. Max file size: Check settings (default 5MB)

### Viewing Proofs
- **Desktop**: Hover over thumbnail in Proof column
- **Mobile**: Tap proof preview in card
- **All**: Click purple eye icon in Actions

### Exporting Proofs
- **Quick**: Export dropdown → "ZIP with Proofs 📎"
- **Filtered**: Set date range → Export → ZIP option
- **Result**: Download ZIP with Excel + proof folders

### Best Practices
✅ Always upload proofs for expenses > ₹5,000  
✅ Use ZIP export for official submissions  
✅ Name files descriptively before upload  
✅ Keep original receipts as backup  
✅ Review proof column before approving transactions  

---

## ❓ FAQ

**Q: Can I export proofs without Excel?**  
A: Currently, ZIP export includes both Excel and proofs. You can extract and delete the Excel file if needed.

**Q: What if a transaction has no proof?**  
A: It will appear in Excel with "No proof uploaded" but won't have a folder in the proofs directory.

**Q: Can I upload multiple proofs per transaction?**  
A: Currently one proof per transaction. For multiple receipts, combine them into a single PDF first.

**Q: Why don't I see thumbnails on mobile?**  
A: Mobile view shows proofs below transaction details (scroll down in card). Desktop table has a dedicated Proof column (XL screens).

**Q: Can I re-upload a proof?**  
A: Yes! Edit the transaction and choose a new file. The old proof will be replaced.

**Q: What's the file size limit?**  
A: Check with your admin. Default is typically 5MB per file.

**Q: How do I submit reports to management?**  
A: Export ZIP with proofs, then email/share the entire ZIP file. Recipients can extract and review.

**Q: Are proofs included in PDF exports?**  
A: No, PDF exports only show filenames. Use ZIP export for actual proof files.

---

## 🎓 Training Tips

### For Team Members
1. **Always upload proofs** when submitting expenses
2. **Use descriptive filenames** (e.g., `venue_invoice_jan2025.pdf`)
3. **Check proof column** before treasurer review
4. **Keep backup copies** of important receipts

### For Treasurers
1. **Review proofs** before approving transactions
2. **Use ZIP export** for monthly reports
3. **Filter by category** to check specific budgets
4. **Verify proof quality** and completeness

### For Management
1. **Request ZIP exports** for comprehensive review
2. **Cross-reference** Excel amounts with proof images
3. **Organize folders** by category for easy analysis
4. **Archive ZIPs** for annual audits

---

## 📞 Support

For technical issues or questions:
- Check this guide first
- Contact TEDx Finance Team
- Review transaction documentation
- Check deployment guides

---

**Last Updated**: January 21, 2025  
**Version**: 2.0  
**Feature**: Proof Management System
