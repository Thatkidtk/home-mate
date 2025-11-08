
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Asset
from ..utils.dates import parse_iso_date

bp = Blueprint("assets", __name__)

@bp.get("/")
@login_required
def list_assets():
    q = request.args.get("q", "").strip()
    query = Asset.query.filter_by(user_id=current_user.id)
    if q:
        like = f"%{q}%"
        query = query.filter(Asset.name.ilike(like))
    assets = query.order_by(Asset.created_at.desc()).all()
    template = "assets/_table.html" if request.headers.get("HX-Request") else "assets/list.html"
    return render_template(template, assets=assets, q=q)

@bp.route("/create", methods=["GET","POST"])
@login_required
def create_asset():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required", "error")
            return redirect(request.url)
        asset = Asset(
            user_id=current_user.id,
            name=name,
            type=request.form.get("type") or None,
            make=request.form.get("make") or None,
            model=request.form.get("model") or None,
            serial=request.form.get("serial") or None,
            purchase_date=parse_iso_date(request.form.get("purchase_date")),
            warranty_expiration=parse_iso_date(request.form.get("warranty_expiration")),
            notes=request.form.get("notes") or None,
        )
        db.session.add(asset)
        db.session.commit()
        flash("Asset created", "success")
        return redirect(url_for("assets.list_assets"))
    return render_template("assets/form.html", asset=None)

@bp.route("/<int:asset_id>/edit", methods=["GET","POST"])
@login_required
def edit_asset(asset_id):
    asset = Asset.query.filter_by(id=asset_id, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        asset.name = request.form.get("name", "").strip() or asset.name
        asset.type = request.form.get("type") or None
        asset.make = request.form.get("make") or None
        asset.model = request.form.get("model") or None
        asset.serial = request.form.get("serial") or None
        asset.purchase_date = parse_iso_date(request.form.get("purchase_date"))
        asset.warranty_expiration = parse_iso_date(request.form.get("warranty_expiration"))
        asset.notes = request.form.get("notes") or None
        db.session.commit()
        flash("Asset updated", "success")
        return redirect(url_for("assets.list_assets"))
    return render_template("assets/form.html", asset=asset)

@bp.post("/<int:asset_id>/delete")
@login_required
def delete_asset(asset_id):
    asset = Asset.query.filter_by(id=asset_id, user_id=current_user.id).first_or_404()
    db.session.delete(asset)
    db.session.commit()
    flash("Asset deleted", "success")
    return redirect(url_for("assets.list_assets"))
