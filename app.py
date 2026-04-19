from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# بيانات البريد الإلكتروني
OWNER_EMAIL = "gooogle.e.r.1@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# يمكن استخدام متغيرات البيئة للأمان
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'jewelry.store.orders@gmail.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', '')

@app.route('/send-order', methods=['POST', 'OPTIONS'])
def send_order():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        phone = data.get('phone', '')
        address = data.get('address', '')
        product = data.get('product', 'طاقم فاخر بطلاء الذهب')
        price = data.get('price', '260 دينار')
        delivery = data.get('delivery', 'مجاني إلى جميع مدن ليبيا')
        
        if not phone or not address:
            return jsonify({'success': False, 'message': 'بيانات غير كاملة'}), 400
        
        # حفظ الطلب في ملف أولاً
        save_order_to_file(phone, address, product, price)
        
        # إرسال البريد الإلكتروني
        send_email_order(phone, address, product, price, delivery)
        
        return jsonify({
            'success': True,
            'message': 'تم تأكيد الطلب بنجاح! سيتصل بك المندوب قريباً'
        }), 200
    
    except Exception as e:
        print(f"خطأ عام: {str(e)}")
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500

def send_email_order(phone, address, product, price, delivery):
    """إرسال الطلب إلى البريد الإلكتروني بتنسيق جميل"""
    try:
        # إنشاء رسالة البريد
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎉 طلب جديد من متجر المجوهرات - {phone}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = OWNER_EMAIL
        
        # إنشاء محتوى HTML جميل
        html_content = f"""
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f5f5f5;
                    direction: rtl;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #B8860B 0%, #8B4513 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    padding: 30px;
                }}
                .order-info {{
                    background-color: #f9f9f9;
                    border-right: 4px solid #B8860B;
                    padding: 20px;
                    margin: 15px 0;
                    border-radius: 5px;
                }}
                .info-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 12px 0;
                    font-size: 16px;
                }}
                .label {{
                    font-weight: bold;
                    color: #333;
                    flex: 0 0 150px;
                }}
                .value {{
                    color: #666;
                    flex: 1;
                    text-align: left;
                }}
                .product-section {{
                    background-color: #fff9e6;
                    border: 2px solid #B8860B;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .product-title {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #B8860B;
                    margin-bottom: 15px;
                }}
                .footer {{
                    background-color: #f5f5f5;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    border-top: 1px solid #ddd;
                }}
                .timestamp {{
                    color: #999;
                    font-size: 12px;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 طلب جديد من متجر المجوهرات</h1>
                </div>
                
                <div class="content">
                    <h2 style="color: #B8860B; text-align: center;">بيانات الطلب</h2>
                    
                    <div class="order-info">
                        <div class="info-row">
                            <span class="label">📱 رقم الهاتف:</span>
                            <span class="value">{phone}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">📍 العنوان/المدينة:</span>
                            <span class="value">{address}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">⏰ وقت الطلب:</span>
                            <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                    </div>
                    
                    <div class="product-section">
                        <div class="product-title">📦 تفاصيل المنتج</div>
                        <div class="info-row">
                            <span class="label">المنتج:</span>
                            <span class="value">{product}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">💰 السعر:</span>
                            <span class="value" style="font-weight: bold; color: #B8860B;">{price}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">🚚 التوصيل:</span>
                            <span class="value" style="color: #27ae60; font-weight: bold;">{delivery}</span>
                        </div>
                    </div>
                    
                    <div style="background-color: #e8f5e9; border-left: 4px solid #27ae60; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <strong style="color: #27ae60;">✓ الطلب محفوظ بنجاح</strong><br>
                        <span style="color: #666; font-size: 14px;">يرجى التواصل مع العميل في أقرب وقت</span>
                    </div>
                </div>
                
                <div class="footer">
                    <p>هذا البريد تم إرساله تلقائياً من نظام متجر المجوهرات</p>
                    <p class="timestamp">التاريخ والوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # إضافة محتوى HTML
        part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part)
        
        # محاولة إرسال البريد
        try:
            # استخدام Gmail SMTP
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            
            # إذا كانت هناك بيانات اعتماد
            if SENDER_PASSWORD:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
                server.quit()
                print(f"✓ تم إرسال البريد بنجاح إلى {OWNER_EMAIL}")
            else:
                print("⚠ لم يتم تعيين كلمة مرور البريد")
        except Exception as e:
            print(f"⚠ لم يتمكن من إرسال البريد: {str(e)}")
            # حتى لو فشل الإرسال، الطلب محفوظ في الملف
    
    except Exception as e:
        print(f"خطأ في إرسال البريد: {str(e)}")

def save_order_to_file(phone, address, product, price):
    """حفظ الطلب في ملف للنسخ الاحتياطي"""
    try:
        order_data = {
            'phone': phone,
            'address': address,
            'timestamp': datetime.now().isoformat(),
            'product': product,
            'price': price
        }
        
        # إضافة الطلب إلى ملف JSON
        try:
            with open('orders.json', 'r', encoding='utf-8') as f:
                orders = json.load(f)
        except:
            orders = []
        
        orders.append(order_data)
        
        with open('orders.json', 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)
        
        print(f"✓ تم حفظ الطلب: {phone}")
    except Exception as e:
        print(f"خطأ في حفظ الطلب: {str(e)}")

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """الحصول على جميع الطلبات (للمسؤول فقط)"""
    try:
        with open('orders.json', 'r', encoding='utf-8') as f:
            orders = json.load(f)
        return jsonify(orders), 200
    except:
        return jsonify([]), 200

@app.route('/health', methods=['GET'])
def health():
    """التحقق من حالة الخادم"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
