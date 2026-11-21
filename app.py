import os
from flask import Flask, render_template_string, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# إعدادات قاعدة البيانات
db_url = os.environ.get('DATABASE_URL', 'sqlite:///orders.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================== جدول قاعدة البيانات ==================
class ClientOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    wilaya = db.Column(db.String(50), nullable=False)
    baladiya = db.Column(db.String(50), nullable=False)
    source = db.Column(db.String(20), default='Website')

# ================== واجهة الموقع (HTML) ==================
HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Khaled Store - طلبات الزبائن</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        body { font-family: 'Cairo', sans-serif; background-color: #f4f6f9; padding: 20px; }
        .form-container { background: white; padding: 30px; border-radius: 15px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .form-control { padding: 12px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #ddd; width: 100%; box-sizing: border-box; }
        .btn-primary { background: #a855f7; color: white; border: none; padding: 12px; font-weight: bold; width: 100%; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .btn-primary:hover { background: #9333ea; }
        h2 { color: #a855f7; text-align: center; margin-bottom: 25px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Khaled Store</h2>
        <form method="POST" action="/submit">
            <input type="text" name="name" class="form-control" placeholder="الاسم الكامل" required>
            <input type="text" name="phone" class="form-control" placeholder="رقم الهاتف" required>
            
            <select name="wilaya" class="form-control" required>
                <option value="" disabled selected>اختر الولاية</option>
                <option value="الجزائر">الجزائر</option>
                <option value="وهران">وهران</option>
                <option value="قسنطينة">قسنطينة</option>
                <option value="سطيف">سطيف</option>
                <option value="عنابة">عنابة</option>
                <option value="البليدة">البليدة</option>
                <option value="تلمسان">تلمسان</option>
                <option value="بجاية">بجاية</option>
            </select>
            
            <input type="text" name="baladiya" class="form-control" placeholder="البلدية" required>
            
            <button type="submit" class="btn-primary">تأكيد الطلب</button>
        </form>
    </div>
</body>
</html>
"""

# ================== المسارات (Routes) ==================
@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    phone = request.form.get('phone')
    wilaya = request.form.get('wilaya')
    baladiya = request.form.get('baladiya')
    
    new_order = ClientOrder(name=name, phone=phone, wilaya=wilaya, baladiya=baladiya, source='Website')
    db.session.add(new_order)
    db.session.commit()
    
    return """
    <div style="text-align:center; padding:50px; font-family:'Cairo';">
        <h2 style="color:#10b981;">تم استلام طلبك بنجاح! ✅</h2>
        <p style="font-size:18px;">راح نتواصلوا معاك قريباً.</p>
        <a href="/" style="color:#a855f7; text-decoration:none;">← العودة للصفحة الرئيسية</a>
    </div>
    """

@app.route('/facebook_webhook', methods=['GET', 'POST'])
def facebook_webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        VERIFY_TOKEN = "khaled_store_secret_123"
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    if request.method == 'POST':
        data = request.json
        try:
            print("Facebook Data:", data)
            return "EVENT_RECEIVED", 200
        except Exception as e:
            return "Error", 500

@app.route('/admin')
def admin():
    orders = ClientOrder.query.order_by(ClientOrder.id.desc()).all()
    rows = ""
    for o in orders:
        rows += f"<tr><td>{o.name}</td><td>{o.phone}</td><td>{o.wilaya}</td><td>{o.baladiya}</td><td>{o.source}</td></tr>"
    
    return f"""
    <div style="padding:20px; font-family:'Cairo'; background:#f4f6f9; min-height:100vh;">
        <h2 style="color:#a855f7; text-align:center;">لوحة الطلبات (Admin)</h2>
        <table class="table table-bordered" style="background:white; text-align:right;">
            <thead class="table-dark">
                <tr><th>الاسم</th><th>الهاتف</th><th>الولاية</th><th>البلدية</th><th>المصدر</th></tr>
            </thead>
            <tbody>{rows or '<tr><td colspan="5" style="text-align:center;">لا توجد طلبات حالياً.</td></tr>'}</tbody>
        </table>
    </div>
    """

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
