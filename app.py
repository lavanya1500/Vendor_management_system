from flask import Flask, request, redirect, render_template, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid, string, secrets

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Vendor(db.Model):
    vendor_code = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    contact_details = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)
    on_time_delivery_rate = db.Column(db.Float, nullable=False)
    quality_rating_avg = db.Column(db.Float, nullable=False)
    average_response_time = db.Column(db.Float, nullable=False)
    fulfillment_rate = db.Column(db.Float, nullable=False)

class PO(db.Model):
    po_id = db.Column(db.String, primary_key=True)
    vendor_code = db.Column(db.Integer, db.ForeignKey('Vendor.vendor_code'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
    items = db.Column(json, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    quality_rating = db.Column(db.Float)
    issue_date = db.Column(db.DateTime, nullable=False)
    acknowledgment_date = db.Column(db.DateTime)

def generate_unique_vendor_code():
    alphabet = string.ascii_letters + string.digits
    while True:
        po_id = ''.join(secrets.choice(alphabet) for _ in range(12))
        if not PO.query.filter_by(po_id=po_id).first():
            return po_id

@app.route('/')
def vendor_form():
    return render_template("vendor.html")

@app.route('/api/vendor/', methods=['POST'])
def vendor_info():
    name = request.form.get("name")
    contact = request.form.get("contact")
    address = request.form.get("address")

    if name and contact and address:
        vendor_code = str(uuid.uuid4())
        info = Vendor(vendor_code=vendor_code, name=name, contact=contact, address=address)
        db.session.add(info)
        db.session.commit()
        return redirect(f'/api/vendors/{vendor_code}')
    else:
        return redirect('/')

@app.route('/api/vendors/<vendor_code>', methods=['GET'])
def get_vendor(vendor_code):
    vendor = Vendor.query.get_or_404(vendor_code)
    return render_template("vendor_detail.html", vendor=vendor)

@app.route('/api/vendors/', methods=['GET'])
def all_vendors():
    vendors = Vendor.query.all()
    return render_template("all_vendor.html", vendors=vendors)

@app.route('/api/vendor/<vendor_code>', methods=['POST'])
def delete_vendor(vendor_code):
    vendor = Vendor.query.get(vendor_code)
    db.session.delete(vendor)
    db.session.commit()
    return redirect('/api/vendors/')

@app.route('/update/vendor/<vendor_code>/', methods=['GET', 'POST'])
def update_vendor(vendor_code):
    vendor = Vendor.query.get_or_404(vendor_code)
    if request.method == 'POST':
        vendor.name = request.form.get('name')
        vendor.contact = request.form.get('contact')
        vendor.address = request.form.get('address')
        db.session.commit()
        return redirect(f'/api/vendors/{vendor_code}')
    return render_template('update_vendor.html', vendor=vendor)

@app.route('/purchase/')
def purchase():
    return render_template('purchase.html')

@app.route('/api/purchase_order/', methods=['POST'])
def purchase_info():
    vendor_code = request.form.get('vendor_code')
    items = request.form.get('items')
    order_date = request.form.get('order_date')
    delivery_date= request.form.get('delivery_date')
    quality_rating = request.form.get('quality_rating')
    issue_date= request.form.get('issue_date')
    acknowledgment_date= request.form.get('acknowledgment_date')
    quantity = request.form.get('quantity')
    status = request.form.get('status')

    if order_date and delivery_date and issue_date and items and order_date and quantity and status:
        po_id = generate_unique_vendor_code()
        info_ = PO(po_id=po_id, delivery_date=delivery_date, issue_date=issue_date, acknowledgment_date=acknowledgment_date, quality_rating=quality_rating, items=items, order_date=order_date, quantity=quantity, status=status)
        db.session.add(info_)
        db.session.commit()
        return redirect(f'/api/purchase_order/{po_id}')
    return render_template('purchase.html')

@app.route('/api/purchase_order/<po_id>')
def one_purchase(po_id):
    po = PO.query.get_or_404(po_id)
    return render_template('purchase_detail.html', po=po)

@app.route('/api/purchase_orders/')
def all_purchases():
    po = PO.query.all()
    all_names = db.session.query(PO.vendor_name).distinct().all()
    unique_names = [name[0] for name in all_names]
    return render_template('all_purchase.html', po=po, unique_names=unique_names)

@app.route('/api/purchase_orders/vendor/<vendor_name>')
def purchases_by_vendor(vendor_name):
    if vendor_name == 'All':
        po = PO.query.all()
    else:
        po = PO.query.filter_by(vendor_name=vendor_name).all()
    all_names = db.session.query(PO.vendor_name).distinct().all()
    unique_names = [name[0] for name in all_names]
    return render_template('all_purchase.html', po=po, unique_names=unique_names, selected_vendor=vendor_name)

@app.route('/update/purchase_order/<po_id>', methods=['GET', 'POST'])
def update_po(po_id):
    po = PO.query.get_or_404(po_id)
    if request.method == 'POST':
        po.vendor_name = request.form.get('vendor_name')
        po.order_date = request.form.get('order_date')
        po.items = request.form.get('items')
        po.quantity = request.form.get('quantity')
        po.status = request.form.get('status')
        db.session.commit()
        return redirect(f'/api/purchase_order/{po_id}')
    return render_template('update_purchase.html', po=po, po_id=po_id)

@app.route('/delete/purchase_order/<po_id>', methods=['POST'])
def delete_po(po_id):
    po = PO.query.get(po_id)
    db.session.delete(po)
    db.session.commit()
    return redirect('/api/purchase_orders/')

if __name__ == "__main__":
    app.run(debug=True)
