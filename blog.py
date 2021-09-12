# -*- coding: utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import os
import pandas as pd
import textract
import pickle
import numpy as np
from zipfile import ZipFile
import os.path
import shutil


bp = Blueprint('blog', __name__)
tpath="/home/dhruv/Desktop/instance/uploads"


def score(x):
    if x>=0.5:
        score=100
    else:
        score=round(x/(1-x)*100,2)
    return score

@bp.route('/')
@login_required
def index():
    db = get_db()
    
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username,sales, cosec, fund, operations, corpfinance, investment'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/views.html',posts=posts)

@bp.route('/Fund_accountant')
@login_required
def fundac():
    db=get_db()
    posts = db.execute(
        'SELECT fund,title'
        ' FROM post'
        ' ORDER BY fund DESC'
    ).fetchall()
    return render_template('blog/fundac.html',posts=posts)

@bp.route('/Company_secretary')
@login_required
def cosec():
    db=get_db()
    posts = db.execute(
        'SELECT cosec,title'
        ' FROM post'
        ' ORDER BY cosec DESC'
    ).fetchall()
    return render_template('blog/cosec.html',posts=posts)

@bp.route('/Financial_Sales')
@login_required
def sales():
    db=get_db()
    posts = db.execute(
        'SELECT sales,title'
        ' FROM post'
        ' ORDER BY sales DESC'
    ).fetchall()
    return render_template('blog/sales.html',posts=posts)

@bp.route('/Operations')
@login_required
def operations():
    db=get_db()
    posts = db.execute(
        'SELECT operations,title'
        ' FROM post'
        ' ORDER BY operations DESC'
    ).fetchall()
    return render_template('blog/operations.html',posts=posts)

@bp.route('/Investment_banker')
@login_required
def invbanker():
    db=get_db()
    posts = db.execute(
        'SELECT investment,title'
        ' FROM post'
        ' ORDER BY investment DESC'
    ).fetchall()
    return render_template('blog/invbank.html',posts=posts)

@bp.route('/Corporate_accounting_&_finance')
@login_required
def corpac():
    db=get_db()
    posts = db.execute(
        'SELECT corpfinance,title'
        ' FROM post'
        ' ORDER BY corpfinance DESC'
    ).fetchall()
    return render_template('blog/corpfinance.html',posts=posts)



@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        
        file = request.files["file"]
        
        if request.files:
           if file.filename == '':
              flash('No selected file')
              return redirect(request.url)
               
               
           

           file.save(os.path.join(tpath,file.filename))
               
           if file.filename.rsplit('.', 1)[1].lower()=="zip":
              with ZipFile(os.path.join(tpath, file.filename),"r") as zip_ref:
                  zip_ref.extractall(tpath)
                  os.remove(os.path.join(tpath,file.filename))
           
                  
           #title = file.filename.rsplit('.', 1)[0]
        body = " "
           
        model2 = pickle.load(open('/home/dhruv/Downloads/model2', 'rb'))
        model3 = pickle.load(open('/home/dhruv/Downloads/model3', 'rb'))
        model4 = pickle.load(open('/home/dhruv/Downloads/model4', 'rb'))
        model5 = pickle.load(open('/home/dhruv/Downloads/model5', 'rb'))
        model6 = pickle.load(open('/home/dhruv/Downloads/model6', 'rb'))
        model7 = pickle.load(open('/home/dhruv/Downloads/model7', 'rb'))
           
        X_train_tf=pickle.load(open('/home/dhruv/Downloads/Xtraintf', 'rb'))
    
        db = get_db()       
        countit=set()    
        if os.path.isdir(os.path.join(tpath,file.filename)):
           for dp, dn, filenames in os.walk(os.path.join(tpath,file.filename)):
              for f in filenames:
                  if f in countit:
                      continue
                  else:
                     countit.add(f)
                     title=f.rsplit('.',1)[0]
                     thefile=os.path.join(dp,f)
                  
                     yes=textract.process(thefile)
                    
           #print(yes)
           #tfile=nlp(yes)
           #tftxt=" ".join([i.text.lower() for i in tfile.noun_chunks])

                     tfex=X_train_tf.transform([yes])

                     pred2=model2.predict_proba(tfex)
                     pred3=model3.predict_proba(tfex)
                     pred4=model4.predict_proba(tfex)
                     pred5=model5.predict_proba(tfex)
                     pred6=model6.predict_proba(tfex)
                     pred7=model7.predict_proba(tfex)
        
             #db = get_db()
                     db.execute(
                'INSERT INTO post (title, body, author_id, sales, cosec, fund, operations, corpfinance, investment)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (title, body, g.user['id'],score(pred7[:,1][0]),score(pred3[:,1][0]),score(pred4[:,1][0]),score(pred6[:,1][0]),score(pred2[:,1][0]),score(pred5[:,1][0]))
                )
        else:
            title=file.filename.rsplit('.',1)[0]
            thefile=os.path.join(tpath,file.filename)
                  
            yes=textract.process(thefile)
                    
           #print(yes)
           #tfile=nlp(yes)
           #tftxt=" ".join([i.text.lower() for i in tfile.noun_chunks])

            tfex=X_train_tf.transform([yes])

            pred2=model2.predict_proba(tfex)
            pred3=model3.predict_proba(tfex)
            pred4=model4.predict_proba(tfex)
            pred5=model5.predict_proba(tfex)
            pred6=model6.predict_proba(tfex)
            pred7=model7.predict_proba(tfex)
        
             #db = get_db()
            db.execute(
        'INSERT INTO post (title, body, author_id, sales, cosec, fund, operations, corpfinance, investment)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (title, body, g.user['id'],score(pred7[:,1][0]),score(pred3[:,1][0]),score(pred4[:,1][0]),score(pred6[:,1][0]),score(pred2[:,1][0]),score(pred5[:,1][0]))
        )
        
        db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/index')
@login_required
def home():
   return render_template('blog/index.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))