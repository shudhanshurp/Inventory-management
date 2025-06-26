from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

class PdfService:
    def generate_sales_order_pdf(self, order_data: dict) -> bytes:
        # print("[PdfService] order_data received:", order_data)
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # 1. Global Layout Constants & Margins
        left_margin = 25 * mm
        right_margin = 25 * mm
        content_top_y = height - 20 * mm
        table_width = width - left_margin - right_margin

        # 2. Customer Information Block Placement
        customer_info_y_start = content_top_y - 20 * mm
        info_line_height = 7 * mm
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, content_top_y, "Sales Order Form")
        c.setFont("Helvetica", 10)
        # Customer Name
        c.drawString(left_margin, customer_info_y_start, f"Customer Name: {order_data.get('c_name', '')}")
        # Delivery Date
        delivery_date = order_data.get('o_delivery_date', '')
        if delivery_date:
            if isinstance(delivery_date, datetime):
                delivery_date = delivery_date.strftime("%Y-%m-%d")
            else:
                try:
                    delivery_date = datetime.strptime(str(delivery_date)[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
                except Exception:
                    delivery_date = str(delivery_date)
        c.drawString(left_margin, customer_info_y_start - info_line_height, f"Delivery Date: {delivery_date}")
        # Address
        c.drawString(left_margin, customer_info_y_start - 2 * info_line_height, f"Address: {order_data.get('c_address', '')}")

        # 3. Table Dimensions and Column Widths
        table_header_top_y = customer_info_y_start - (info_line_height * 4)
        table_header_height = 10 * mm
        table_data_row_height = 10 * mm
        num_data_rows = 10
        col_widths = [25*mm, 50*mm, 15*mm, 20*mm, 25*mm, 25*mm]  # 160mm total
        col_titles = ["Product Code", "Product Name", "Qty", "Price", "Total", "Remarks"]
        table_left = left_margin
        table_right = table_left + sum(col_widths)
        table_bottom_y = table_header_top_y - (table_header_height + (num_data_rows * table_data_row_height))

        # 4. Table Header Text Placement
        header_text_y = table_header_top_y - (table_header_height / 2) + 1*mm
        c.setFont("Helvetica-Bold", 10)
        current_x = table_left
        for i, title in enumerate(col_titles):
            c.drawString(current_x + 2, header_text_y, title)
            current_x += col_widths[i]
        c.setFont("Helvetica", 10)

        # 5. Table Data Text Placement
        items = order_data.get('items', [])
        # print("[PdfService] items:", items)
        total_amount = 0
        for row in range(num_data_rows):
            data_y = table_header_top_y - table_header_height - (row * table_data_row_height)
            current_x = table_left
            if row < len(items):
                item = items[row]
                code = str(item.get('p_id') or item.get('product_code', ''))
                name = str(item.get('p_name') or item.get('product_name', ''))
                qty = item.get('oi_qty') if 'oi_qty' in item else item.get('quantity', '')
                price = item.get('oi_price') if 'oi_price' in item else item.get('price', 0)
                total = item.get('oi_total') if 'oi_total' in item else (float(price) * float(qty or 0))
                remarks = str(item.get('remarks', ''))
                total_amount += float(total or 0)
                values = [code, name, str(qty), f"{price:.2f}", f"{total:.2f}", remarks]
            else:
                values = ["" for _ in col_titles]
            for i, value in enumerate(values):
                c.drawString(current_x + 2, data_y - (table_data_row_height / 2) + 1*mm, value)
                current_x += col_widths[i]

        # 6. Draw Table Grid (including missing top border)
        # Top border
        c.line(table_left, table_header_top_y, table_right, table_header_top_y)
        # Horizontal lines (header bottom + data rows)
        for r in range(num_data_rows + 1):
            y = table_header_top_y - table_header_height - (r * table_data_row_height)
            c.line(table_left, y, table_right, y)
        # Header bottom border
        c.line(table_left, table_header_top_y - table_header_height, table_right, table_header_top_y - table_header_height)
        # Vertical lines
        x_pos = table_left
        for w in col_widths:
            c.line(x_pos, table_header_top_y, x_pos, table_bottom_y)
            x_pos += w
        c.line(x_pos, table_header_top_y, x_pos, table_bottom_y)  # last right border

        # 7. Footer Placement
        total_sales_y = table_bottom_y - 12 * mm
        remarks_y = total_sales_y - 8 * mm
        # Total Sales Order Amount label
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_margin, total_sales_y, "Total Sales Order Amount:")
        # Value aligned to start of Total column
        total_col_x = table_left + sum(col_widths[:4]) + 2
        c.drawString(total_col_x, total_sales_y, f"{total_amount:.2f}")
        c.setFont("Helvetica", 10)
        # Remarks
        c.drawString(left_margin, remarks_y, f"Remarks: {order_data.get('remarks', '')}")

        c.showPage()
        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf 