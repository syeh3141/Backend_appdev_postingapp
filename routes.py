import json
from db import db, Post, Comment
from flask import Flask, request


db_filename = "posts.db"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
  db.create_all()

@app.route('/')
@app.route('/api/posts/')
def get_posts():
  posts = Post.query.all()
  res = {'success': True, 'data': [post.serialize() for post in posts]}
  return json.dumps(res), 200

@app.route('/api/posts/', methods = ['POST'])
def create_post():
  body = json.loads(request.data)
  
  post = Post(
    text=body.get('text'),
    username=body.get('username')
  )
  db.session.add(post)
  db.session.commit()
  return json.dumps({'success': True, 'data': post.serialize()}), 201

@app.route('/api/post/<int:post_id>/')
def get_post(post_id):
  post = Post.query.filter_by(id=post_id).first()
  if post is not None:
    return json.dumps({'success': True, 'data': post.serialize()}), 200    
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

@app.route('/api/post/<int:post_id>/', methods = ['POST'])
def edit_post(post_id):
  
  post = Post.query.filter_by(id=post_id).first()
  if post is not None:
    body = json.loads(request.data)
    post.text = body.get('text', post.text)
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 200    
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

@app.route('/api/post/<int:post_id>/', methods = ['DELETE'])
def delete_post(post_id):
  post = Post.query.filter_by(id=post_id).first()
  if post is not None:
    db.session.delete(post)
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 200    
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

@app.route('/api/post/<int:post_id>/vote/', methods = ['POST'])
def vote_post(post_id):
  post = Post.query.filter_by(id=post_id).first()
  if post is not None:
    body = json.loads(request.data)
    vote = body.get('vote')
    if vote == False:
      post.score -= 1
    else:
      post.score += 1
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 200    
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

@app.route('/api/post/<int:post_id>/comments/')
def get_comments(post_id):
  post = Post.query.filter_by(id=post_id).first()
  if post is not None:
    comments = [comment.serialize() for comment in post.comments]
    return json.dumps({'success': True, 'data': comments}), 200
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

@app.route('/api/post/<int:post_id>/comment/', methods = ['POST'])
def post_comment(post_id):
  post = Post.query.filter_by(id=post_id).first()
  if post is not None:
    body = json.loads(request.data)
    comment = Comment(
      text= body.get('text'),
      username= body.get('username'),
      post_id= post.id
    )
    post.comments.append(comment)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({'success': True, 'data': comment.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

@app.route('/api/comment/<int:comment_id>/vote/', methods = ['POST'])
def vote_comment(comment_id):
  comment = Comment.query.filter_by(id=comment_id).first()
  if comment is not None:
    body = json.loads(request.data)
    vote = body.get('vote')
    if vote == False:
      comment.score -= 1
    else:
      comment.score += 1
    db.session.commit()
    return json.dumps({'success': True, 'data': comment.serialize()}), 200    
  return json.dumps({'success': False, 'error': 'Comment not found!'}), 404

if __name__ == '__main__':
  app.run(host = '0.0.0.0', port = 5000, debug = True)