from flask import Blueprint, request, current_app, render_template
from flask_login import current_user

from models import Post, Category, Comment

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page)
    posts = pagination.items
    return render_template('front/index.html')


@blog_bp.route('/about')
def about():
    return render_template('front/about.html')

