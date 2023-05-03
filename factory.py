import os

from flask import Flask, render_template
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from blueprints.admin import admin_bp
from blueprints.auth import auth_bp
from blueprints.blog import blog_bp
from extensions import db, ckeditor, mail, moment, bootstrap, login_manager, csrf_protect
from models import Admin, Category, Link, Comment
from settings import config
import click


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('myblog2')
    app.config.from_object(config[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errors(app)
    register_shell_context(app)
    register_template_context(app)

    return app


def register_logging(app):
    pass


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    csrf_protect.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
        user = Admin.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
        return user  # 返回用户对象


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(
            admin=admin, categories=categories,
            links=links, unread_comments=unread_comments)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html"), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_exception(e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command('forge')
    @click.option('--category', default=10, help='Quantity of categories, default is 10')
    @click.option('--post', default=50, help='Quantity of posts, default is 50')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500')
    def forge(category, post, comment):
        from fakes import fake_admin, fake_categories, fake_posts, fake_comments, create_links

        db.drop_all()
        db.create_all()

        click.echo("Generating the administrator...")
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        create_links()

        click.echo('Done.')
