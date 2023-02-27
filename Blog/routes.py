from flask import render_template, request, redirect, url_for, flash
from Blog import app, db
from Blog.models import Entry
from Blog.forms import EntryForm



@app.route('/')
def main():
    entries = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())
    return render_template('homepage.html', entries = entries)


def entries(entry_id = None):
    errors = None
    if entry_id is None:
        form = EntryForm()
        if request.method == 'POST':     
            
            if form.validate_on_submit():
                entry = Entry(
                    title=form.title.data,
                    body=form.body.data,
                    is_published=form.is_published.data
                    )
                db.session.add(entry)
                db.session.commit()
                flash(f"Dodano nowy post!")
            else:
                errors = form.errors
            return redirect(url_for('main'))
        return render_template("entry_form.html", form=form, errors=errors)
    elif entry_id is not None:
        entry = Entry.query.filter_by(id=entry_id).first_or_404()
        form = EntryForm(obj=entry)
        if request.method == 'POST':
            
            if form.validate_on_submit():
                form.populate_obj(entry)
                db.session.commit()
            else:
                errors = form.errors
            return redirect(url_for('main'))
        return render_template("entry_form.html", form=form, errors=errors)


@app.route("/new-post/", methods=["GET", "POST"])
def create_entry():
   return entries()



@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
   return entries(entry_id)