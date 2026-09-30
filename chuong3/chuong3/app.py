from flask import Flask, request, jsonify, render_template_string, url_for
from markupsafe import escape

app = Flask(__name__)

BOOKS = [
    {"id": 1, "title": "Lập trình Python Căn Bản", "author": "Nguyễn Văn A", "year": 2021, "category": "Lập trình", "available": True},
    {"id": 2, "title": "Flask Web Development", "author": "Trần Thị B", "year": 2022, "category": "Lập trình", "available": False},
    {"id": 3, "title": "Cấu trúc dữ liệu & Giải thuật", "author": "Lê Văn C", "year": 2020, "category": "Khoa học máy tính", "available": True},
    {"id": 4, "title": "Hệ quản trị Cơ sở dữ liệu", "author": "Phạm Văn D", "year": 2023, "category": "Cơ sở dữ liệu", "available": True},
]

BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LibraryMS v0.1</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        nav { background: #f4f4f4; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
        nav a { margin-right: 15px; text-decoration: none; color: #333; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .filter-bar { margin-bottom: 15px; }
        .filter-bar a { margin-right: 10px; text-decoration: none; }
    </style>
</head>
<body>
    <nav>
        <a href="{{ url_for('home') }}">Trang chủ</a>
        <a href="{{ url_for('get_books') }}">Danh sách sách</a>
        <a href="{{ url_for('api_books') }}">API Books</a>
    </nav>
    <hr>
    <div>
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    total_books = len(BOOKS)
    available_books = sum(1 for b in BOOKS if b["available"])
    
    content = f"""
    <h2>Thống kê thư viện</h2>
    <p>Tổng số đầu sách: <strong>{total_books}</strong></p>
    <p>Số sách sẵn sàng cho mượn: <strong>{available_books}</strong></p>
    """
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", content))

@app.route("/books")
def get_books():
    category_filter = request.args.get("category")
    
    categories = sorted(list(set(b["category"] for b in BOOKS)))
    
    filtered_books = BOOKS
    if category_filter:
        filtered_books = [b for b in BOOKS if b["category"].lower() == category_filter.lower()]

    filter_links = [f'<a href="{url_for("get_books")}">Tất cả</a>']
    for cat in categories:
        filter_links.append(f'<a href="{url_for("get_books", category=cat)}">{escape(cat)}</a>')
    filter_bar_html = " | ".join(filter_links)

    rows = ""
    for b in filtered_books:
        detail_url = url_for("book_detail", book_id=b["id"])
        status = "Có sẵn" if b["available"] else "Đã mượn"
        rows += f"""
        <tr>
            <td>{b["id"]}</td>
            <td><a href="{detail_url}">{escape(b["title"])}</a></td>
            <td>{escape(b["author"])}</td>
            <td>{b["year"]}</td>
            <td>{escape(b["category"])}</td>
            <td>{status}</td>
        </tr>
        """

    content = f"""
    <h2>Danh sách sách</h2>
    <div class="filter-bar">
        <strong>Lọc theo thể loại:</strong> {filter_bar_html}
    </div>
    <table>
        <tr>
            <th>ID</th><th>Tên sách</th><th>Tác giả</th><th>Năm xuất bản</th><th>Thể loại</th><th>Trạng thái</th>
        </tr>
        {rows if rows else '<tr><td colspan="6">Không có sách nào thuộc thể loại này.</td></tr>'}
    </table>
    """
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", content))

@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        error_msg = f"<h1>404 Not Found</h1><p>Không có sách với ID = {escape(str(book_id))}</p>"
        return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", error_msg)), 404

    status = "Có sẵn" if book["available"] else "Đã mượn"
    content = f"""
    <h2>Chi tiết sách #{book["id"]}</h2>
    <p><strong>Tên sách:</strong> {escape(book["title"])}</p>
    <p><strong>Tác giả:</strong> {escape(book["author"])}</p>
    <p><strong>Năm xuất bản:</strong> {book["year"]}</p>
    <p><strong>Thể loại:</strong> {escape(book["category"])}</p>
    <p><strong>Trạng thái:</strong> {status}</p>
    <br>
    <a href="{url_for("get_books")}">← Quay lại danh sách sách</a>
    """
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", content))

@app.route("/api/books", methods=["GET"])
def api_books():
    return jsonify({"books": BOOKS, "total": len(BOOKS)})

@app.route("/api/books/<int:book_id>", methods=["GET"])
def api_book_detail(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": f"Không có sách với ID = {book_id}"}), 404
    return jsonify(book)

@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Đường dẫn API không tồn tại"}), 404
    
    content = "<h2>404 - Trang không tồn tại</h2><p>Đường dẫn bạn truy cập không hợp lệ.</p>"
    return render_template_string(BASE_HTML.replace("{% block content %}{% endblock %}", content)), 404

if __name__ == "__main__":
    app.run(debug=True)