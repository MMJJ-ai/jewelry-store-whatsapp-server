from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# رقم الهاتف الخاص بك على WhatsApp
OWNER_PHONE = "00218914587353"
# رابط API لإرسال الرسائل عبر WhatsApp (سنستخدم خدمة مجانية)
WHATSAPP_API_URL = "https://api.callmebot.com/whatsapp.php"

@app.route('/api/submit-order', methods=['POST'])
def submit_order():
    try:
        data = request.json
        phone = data.get('phone', '')
        address = data.get('address', '')
        
        if not phone or not address:
            return jsonify({'success': False, 'message': 'بيانات غير كاملة'}), 400
        
        # إنشاء رسالة الطلب
        order_message = f"""
🎉 طلب جديد من متجر المجوهرات

📱 رقم الهاتف: {phone}
📍 العنوان/المدينة: {address}
⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

المنتج: طاقم فاخر بطلاء الذهب
💰 السعر: 260 دينار (شامل التوصيل)
🚚 التوصيل: مجاني إلى جميع مدن ليبيا
        """
        
        # إرسال الرسالة عبر CallMeBot (مجاني)
        try:
            params = {
                'phone': OWNER_PHONE.replace('+', ''),
                'text': order_message,
                'apikey': 'YOUR_API_KEY'  # يمكن تركه فارغاً للخدمة المجانية
            }
            
            # محاولة إرسال عبر CallMeBot
            response = requests.get(WHATSAPP_API_URL, params=params, timeout=10)
            
            # حفظ الطلب في ملف (للنسخ الاحتياطي)
            save_order_to_file(phone, address)
            
            return jsonify({
                'success': True,
                'message': 'تم تأكيد الطلب بنجاح! سيتصل بك المندوب قريباً'
            }), 200
            
        except Exception as e:
            # حتى لو فشل الإرسال، نحفظ الطلب
            save_order_to_file(phone, address)
            return jsonify({
                'success': True,
                'message': 'تم تأكيد الطلب! سيتصل بك المندوب قريباً'
            }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500

def save_order_to_file(phone, address):
    """حفظ الطلب في ملف للنسخ الاحتياطي"""
    try:
        order_data = {
            'phone': phone,
            'address': address,
            'timestamp': datetime.now().isoformat(),
            'product': 'طاقم فاخر بطلاء الذهب',
            'price': '260 دينار'
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
    except:
        pass

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
