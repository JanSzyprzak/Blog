import functools
from flask import render_template, request, redirect, url_for, flash, session
from Blog import app, db
from Blog.models import Entry
from Blog.forms import EntryForm, LoginForm, ValidationError









@app.route('/', methods=['GET', 'POST'])
def main():
    entries = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())
    if request.method == "POST":
        entry_id = request.form.data
        delete_entry(entry_id)
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


def login_required(view_func):
   @functools.wraps(view_func)
   def check_permissions(*args, **kwargs):
       if session.get('logged_in'):
           return view_func(*args, **kwargs)
       return redirect(url_for('login', next=request.path))
   return check_permissions

@app.route("/login/", methods=['GET', 'POST'])
def login():
   form = LoginForm()
   errors = None
   next_url = request.args.get('next')
   if request.method == 'POST':
        try:        
            if form.validate_on_submit():
                session['logged_in'] = True
                session.permanent = True  
                flash('You are now logged in.', 'success')
                return redirect(next_url or url_for('main'))
            else:
                errors = form.errors
        except ValidationError:
            flash("Wrong credentials!")
             
            
   return render_template("login_form.html", form=form, errors=errors)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
   if request.method == 'POST':
       session.clear()
       flash('You are now logged out.', 'success')
   return redirect(url_for('main'))



@app.route("/new-post/", methods=["GET", "POST"])
@login_required
def create_entry():
   return entries()


@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
   return entries(entry_id)


@app.route("/drafts/", methods=["GET", "POST"])
@login_required
def list_drafts():
    entries = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
    entry_id = None
    if request.method == "POST":
        entry_id = request.form.get('entry_id')
        return delete_entry(entry_id)

    return render_template('drafts.html', entries = entries)
    

def delete_entry(entry_id):
    entry_to_delete = Entry.query.filter_by(id=entry_id).first_or_404()
    
    if entry_to_delete:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return redirect(url_for('main'))
    return redirect(url_for('main'))
        
    

