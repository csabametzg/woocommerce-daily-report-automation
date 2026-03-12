\# WooCommerce Daily Report Automation


Python automation script that connects to the WooCommerce REST API, retrieves the previous day's order data, checks low-stock products, and sends an automated email report.



\## Features


\- Connects to the WooCommerce REST API
\- Retrieves all orders from yesterday using pagination
\- Filters orders by status
\- Calculates gross daily revenue
\- Prints a detailed order summary
\- Detects products below a low-stock threshold
\- Sends the full report by email automatically


\## Use Case


This script was built to automate repetitive daily reporting tasks for WooCommerce stores.

It can help store owners or marketers quickly see:


\- how many orders arrived yesterday
\- total gross revenue
\- detailed order items
\- products that are running low on stock



\## Tech Stack


\- Python
\- Requests
\- WooCommerce REST API
\- SMTP email sending



\## Environment Variables


Create a `.env` file based on `.env.example` and fill in your own credentials.


Required variables:


\- `BASE\_URL\_NAME`
\- `WC\_CK`
\- `WC\_CS`
\- `SMTP\_HOST\_NAME`
\- `SMTP\_USER\_NAME`
\- `SMTP\_PASS`
\- `TO\_EMAIL\_ADDRESS`



\## Installation


```bash

pip install -r requirements.txt



\## Run

python main.py



\## Example Output

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



\## Notes

- Credentials are loaded from environment variables.
- Do not commit real API keys or SMTP passwords to GitHub.
- The script uses the Europe/Budapest timezone.
- The script sends plain-text email reports.


\## Future Improvements

- Export report to CSV
- Add HTML email formatting
- Add logging
- Add retry handling for failed requests
- Add separate product sales summary
