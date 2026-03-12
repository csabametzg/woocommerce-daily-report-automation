# WooCommerce Daily Report Automation

Python automation script that retrieves WooCommerce order data, calculates daily revenue, checks low-stock products and sends an automated email report.

## 🚀 Features

• Connects to WooCommerce REST API  
• Retrieves yesterday's orders with pagination  
• Calculates total daily revenue  
• Detects low-stock products  
• Sends automated email report via SMTP  

## 🧰 Tech Stack

Python  
WooCommerce REST API  
SMTP email automation  
Environment variables (.env)

## 📦 Example Use Case

Online store owners often need a daily report about:

- how many orders were placed yesterday
- total daily revenue
- which products are running out of stock

This script automates the entire process and sends a daily report via email.



```markdown
![WooCommerce Daily Report](images/report_example.png)
![WooCommerce Daily Report](images/report_example2.png)
![WooCommerce Daily Report](images/report_example3.png)



## ⚙️ Installation

```bash
git clone https://github.com/csabametzg/woocommerce-daily-report-automation.git
cd woocommerce-daily-report-automation
pip install -r requirements.txt


## ▶ Run

python main.py


## Example Output

====== Yesterday's WooCommerce Report ======
Period (Budapest): 2026-03-11 00:00  →  2026-03-12 00:00
Statuses: processing,completed,on-hold

— — — — — New Orders (Detailed) — — — — —

Order #1234 | John Smith
  Payment: Credit Card | Status: completed | Amount: 19 900 Ft
  Items:
   - Python Workbook × 1
   - Cheat Sheet × 1

— — — — — Summary — — — — —
Number of orders yesterday: 5
Gross revenue yesterday:    89 500 Ft

====== Low Stock ( < 30 pcs ) ======
- Python Workbook | SKU: PW-001 -> 12 pcs
- ChatGPT Ebook | SKU: CGPT-01 -> 8 pcs



## Notes

- Credentials are loaded from environment variables.
- Do not commit real API keys or SMTP passwords to GitHub.
- The script uses the Europe/Budapest timezone.
- The script sends plain-text email reports.


## Future Improvements

- Export report to CSV
- Add HTML email formatting
- Add logging
- Add retry handling for failed requests
- Add separate product sales summary







