import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import smtplib
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
import io
import contextlib
import os


# ========= SETTINGS =========
BASE_URL = os.getenv("BASE_URL_NAME")
CK = os.getenv("WC_CK")
CS = os.getenv("WC_CS")


LOW_STOCK_THRESHOLD = 30
ORDER_STATUSES = "processing,completed,on-hold"  # option: pending
PER_PAGE = 100
TIMEZONE = ZoneInfo("Europe/Budapest")

# ============================


def huf(amount: float) -> str:
    return f"{int(round(amount)):,} Ft".replace(",", " ")


def wc_get(endpoint: str, params: dict | None = None):
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    r = requests.get(url, params=params, auth=(CK, CS), timeout=30)
    r.raise_for_status()
    return r


def fetch_all_pages(endpoint: str, params: dict) -> list:
    """Downloads all pages using pagination (per_page, page)."""
    all_items = []
    page = 1
    while True:
        p = dict(params)
        p["per_page"] = PER_PAGE
        p["page"] = page

        r = wc_get(endpoint, p)
        items = r.json()
        if not items:
            break

        all_items.extend(items)

        total_pages = int(r.headers.get("X-WP-TotalPages", "0") or "0")
        if total_pages and page >= total_pages:
            break

        page += 1

    return all_items


def yesterday_range_iso_budapest():
    """Yesterday 00:00:00 -> today 00:00:00 in Europe/Budapest timezone, ISO format (with offset)."""
    now = datetime.now(TIMEZONE)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    y_start = today_start - timedelta(days=1)
    y_end = today_start
    return y_start.isoformat(), y_end.isoformat(), y_start, y_end


def get_yesterday_orders():
    after_iso, before_iso, y_start, y_end = yesterday_range_iso_budapest()

    params = {
        "after": after_iso,
        "before": before_iso,
        "status": ORDER_STATUSES,
        "orderby": "date",
        "order": "asc",
    }

    orders = fetch_all_pages("/orders", params)
    return orders, y_start, y_end


def print_orders_report(orders: list, y_start: datetime, y_end: datetime):
    print("====== Yesterday's WooCommerce Report ======")
    print(f"Period (Budapest): {y_start:%Y-%m-%d %H:%M}  →  {y_end:%Y-%m-%d %H:%M}")
    print(f"Statuses: {ORDER_STATUSES}")
    print()

    total_revenue = 0.0

    if not orders:
        print("No orders from yesterday matched this status filter.")
        return 0, 0.0

    print("— — — — — New Orders (Detailed) — — — — —")
    for o in orders:
        order_number = o.get("number") or o.get("id")
        status = o.get("status", "unknown")
        payment_method = o.get("payment_method_title") or o.get("payment_method") or "unknown"

        billing = o.get("billing") or {}
        first_name = (billing.get("first_name") or "").strip()
        last_name = (billing.get("last_name") or "").strip()
        customer_name = (first_name + " " + last_name).strip() or "No name provided"

        total = float(o.get("total") or 0)
        total_revenue += total

        print(f"\nOrder #{order_number} | {customer_name}")
        print(f"  Payment: {payment_method} | Status: {status} | Amount: {huf(total)}")

        line_items = o.get("line_items") or []
        if not line_items:
            print("  Items: (no line_items)")
        else:
            print("  Items:")
            for li in line_items:
                name = li.get("name", "Unknown product")
                qty = li.get("quantity", 0)
                print(f"   - {name} × {qty}")

    print("\n— — — — — Summary — — — — —")
    print(f"Number of orders yesterday: {len(orders)}")
    print(f"Gross revenue yesterday:    {huf(total_revenue)}")

    return len(orders), total_revenue


def get_low_stock_products(threshold: int):
    """
    Low stock: manage_stock = true and stock_quantity < threshold.
    The Woo API does not always support server-side "<" filtering,
    so we fetch stock-managed products and filter them client-side.
    """
    params = {
        "status": "publish",
        "stock_status": "instock",
        "orderby": "title",
        "order": "asc",
    }

    products = fetch_all_pages("/products", params)

    low = []
    for p in products:
        manage_stock = bool(p.get("manage_stock"))
        stock_qty = p.get("stock_quantity", None)

        # Only list products where Woo actually manages stock and a quantity is available.
        if manage_stock and isinstance(stock_qty, int) and stock_qty < threshold:
            low.append({
                "name": p.get("name", "Unknown product"),
                "sku": p.get("sku") or "",
                "qty": stock_qty,
            })

    # sort by ascending stock quantity
    low.sort(key=lambda x: x["qty"])
    return low


def print_low_stock(low_stock: list, threshold: int):
    print("\n====== Low Stock ( < {} pcs ) ======".format(threshold))
    if not low_stock:
        print("There are no stock-managed products below {} units.".format(threshold))
        return

    for item in low_stock:
        sku_part = f" | SKU: {item['sku']}" if item["sku"] else ""
        print(f"- {item['name']}{sku_part} -> {item['qty']} pcs")


def main():
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            orders, y_start, y_end = get_yesterday_orders()
            print_orders_report(orders, y_start, y_end)

            low_stock = get_low_stock_products(LOW_STOCK_THRESHOLD)
            print_low_stock(low_stock, LOW_STOCK_THRESHOLD)

        report_text = buf.getvalue()
        return report_text, y_start

    except requests.HTTPError as e:
        # you can also send the error by email
        return f"HTTP error: {e}", datetime.now(TIMEZONE)

    except Exception as e:
        return f"Error: {e}", datetime.now(TIMEZONE)


SMTP_HOST = os.getenv("SMTP_HOST_NAME")
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER_NAME")
SMTP_PASS = os.getenv("SMTP_PASS")
TO_EMAIL = os.getenv("TO_EMAIL_ADDRESS")


def send_report_email(subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = formataddr(("Python Project", SMTP_USER))
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()
    msg["Reply-To"] = SMTP_USER
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)

        # Important: the envelope sender should also match (spam filters check this!)
        server.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())


if __name__ == "__main__":
    report_text, y_start = main()

    subject = f"WooCommerce daily report – {y_start:%Y-%m-%d} (yesterday)"
    send_report_email(subject, report_text)
    print("Report email sent to:", TO_EMAIL)
