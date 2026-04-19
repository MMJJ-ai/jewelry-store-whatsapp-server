from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime
import urllib.parse

app = Flask(__name__)
CORS(app)

# رقم الهاتف الخاص بك على WhatsApp
OWNER_PHONE = "218914587353"  # بدون 00 أو +

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
        
        # إنشاء رسالة الطلب
        order_message = f"""🎉 طلب جديد من متجر المجوهرات

📱 رقم الهاتف: {phone}
📍 العنوان/المدينة: {address}
⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

المنتج: {product}
💰 السعر: {price}
🚚 التوصيل: {delivery}"""
        
        # حفظ الطلب في ملف أولاً
        save_order_to_file(phone, address, product, price)
        
        # محاولة إرسال الرسالة عبر عدة طرق
        send_whatsapp_message(OWNER_PHONE, order_message)
        
        return jsonify({
            'success': True,
            'message': 'تم تأكيد الطلب بنجاح! سيتصل بك المندوب قريباً'
        }), 200
    
    except Exception as e:
        print(f"خطأ عام: {str(e)}")
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500

def send_whatsapp_message(phone, message):
    """إرسال رسالة WhatsApp باستخدام عدة طرق"""
    
    # الطريقة الأولى: استخدام Click to WhatsApp
    try:
        # رابط WhatsApp المباشر
        whatsapp_url = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(message)}"
        print(f"WhatsApp URL: {whatsapp_url}")
    except Exception as e:
        print(f"خطأ في الطريقة الأولى: {str(e)}")
    
    # الطريقة الثانية: استخدام CallMeBot
    try:
        params = {
            'phone': phone,
            'text': message,
            'apikey': 'apikey'  # CallMeBot API
        }
        response = requests.get('https://api.callmebot.com/whatsapp.php', params=params, timeout=10)
        print(f"CallMeBot Response: {response.status_code}")
    except Exception as e:
        print(f"خطأ في CallMeBot: {str(e)}")
    
    # الطريقة الثالثة: استخدام Twilio (إذا كان متاحاً)
    try:
        # يمكن إضافة Twilio API هنا لاحقاً
        pass
    except Exception as e:
        print(f"خطأ في Twilio: {str(e)}")

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
        
        print(f"تم حفظ الطلب: {phone}")
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

@app.route('/test-whatsapp', methods=['POST'])
def test_whatsapp():
    """اختبار إرسال رسالة WhatsApp"""
    try:
        data = request.json
        phone = data.get('phone', OWNER_PHONE)
        message = data.get('message', 'اختبار رسالة من الخادم')
        
        send_whatsapp_message(phone, message)
        
        return jsonify({
            'success': True,
            'message': 'تم إرسال الرسالة'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
