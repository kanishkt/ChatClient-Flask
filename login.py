from flask import render_template
from flask.ext.user import SQLAlchemyAdapter, UserManager, login_required, roles_required
from setup import app
from login_model import User, UserAuth, Role, db

__author__ = 'kanishk'

'''
Class to create the database and set routes for the Flask-Login
'''
def create_app():

    #Reset all the database tables
    db.create_all()

    # Setup Flask-User
    db_adapter = SQLAlchemyAdapter(db,  User, UserAuthClass=UserAuth)
    user_manager = UserManager(db_adapter, app)

    # Create 'user007' user with 'secret' and 'agent' roles
    if not UserAuth.query.filter(UserAuth.username=='user007').first():
        admin_User = User(email='kanishkthareja@gmail.com', first_name='James', last_name='Bond', active=True)
        db.session.add(admin_User)
        user_auth1 = UserAuth(user=admin_User, username='user007',
                password=user_manager.hash_password('Password1')
                )
        db.session.add(user_auth1)
        admin_User.roles.append(Role(name='secret'))
        admin_User.roles.append(Role(name='agent'))
        db.session.commit()

    '''
    The Home page is accessible to anyone
    '''
    @app.route('/')
    def home_page():
        return render_template('pages/home_page.html')

    '''
    The Members page is only accessible to authenticated users
    '''
    @app.route('/member_page')
    @login_required
    def members_page():
        return render_template('pages/member_page.html')

    '''
    The Special page requires a user with 'special' and 'sauce' roles or with 'special' and 'agent' roles.
    '''
    @app.route('/special')
    @roles_required('secret', ['sauce', 'agent'])
    def special_page():
       return render_template('pages/admin_page.html')