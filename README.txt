Sample repoze.who middleware config and plugins for TG2.  This package
depends on repoze.who 0.8 or better.

Trying it Out

 - Install TG2 into a virtualenv.

 - Install this package into the same virtualenv via "setup.py
   install".

 - Create a TG2 quickstart project using the virtualenv's python.

 - In the development.ini of you project...

 - In the config.middleware module of your project, add the following
   just under "CUSTOM MIDDLEWARE HERE"::

     # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)

     from tgrepozewho.middleware import make_who_middleware
     app = make_who_middleware(app, config, User, user_criterion, user_id_col,
            DBSession)

 - Add the following definitions in you model.__init__::

groups_table = Table('tg_group', metadata,
    Column('group_id', Integer, primary_key=True),
    Column('group_name', Unicode(16), unique=True),
    Column('display_name', Unicode(255)),
    Column('created', DateTime, default=datetime.datetime.now)
)

users_table = Table('tg_user', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('user_name', Unicode(16), unique=True),
    Column('email_address', Unicode(255), unique=True),
    Column('display_name', Unicode(255)),
    Column('password', Unicode(40)),
    Column('created', DateTime, default=datetime.datetime.now)
)

permissions_table = Table('tg_permission', metadata,
    Column('permission_id', Integer, primary_key=True),
    Column('permission_name', Unicode(16), unique=True),
    Column('description', Unicode(255))
)

user_group_table = Table('tg_user_group', metadata,
    Column('user_id', Integer, ForeignKey('tg_user.user_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('tg_group.group_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

group_permission_table = Table('tg_group_permission', metadata,
    Column('group_id', Integer, ForeignKey('tg_group.group_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('tg_permission.permission_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

# identity model
class Group(object):
    """An ultra-simple group definition.
    """
    def __repr__(self):
        return '<Group: name=%s>' % self.group_name

class User(object):
    """Reasonably basic User definition. Probably would want additional
    attributes.
    """
    def __repr__(self):
        return '<User: email="%s", display name="%s">' % (
                self.email_address, self.display_name)

    def permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
    permissions = property(permissions)

    def by_email_address(klass, email):
        """A class method that can be used to search users
        based on their email addresses since it is unique.
        """
        session = DBSession()
        return session.query(klass).filter(klass.email_address==email).first()

    by_email_address = classmethod(by_email_address)

    def by_user_name(klass, username):
        """A class method that permits to search users
        based on their user_name attribute.
        """
        session = DBSession()
        return session.query(klass).filter(klass.user_name==username).first()

    by_user_name = classmethod(by_user_name)

    def _set_password(self, password):
        """encrypts password on the fly using the encryption
        algo defined in the configuration
        """
        algorithm = config.get('authorize.hashmethod', None)
        self._password = self.__encrypt_password(algorithm, password)

    def _get_password(self):
        """returns password
        """
        return self._password

    password = property(_get_password, _set_password)

    def __encrypt_password(self, algorithm, password):
        """Hash the given password with the specified algorithm. Valid values
        for algorithm are 'md5' and 'sha1'. All other algorithm values will
        be essentially a no-op."""
        hashed_password = password

        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')

        else:
            password_8bit = password

        if "md5" == algorithm:
            hashed_password = md5.new(password_8bit).hexdigest()

        elif "sha1" == algorithm:
            hashed_password = sha.new(password_8bit).hexdigest()

        # TODO: re-add the possibility to provide own hasing algo
        # here... just get the real config...

        #elif "custom" == algorithm:
        #    custom_encryption_path = turbogears.config.get(
        #        "identity.custom_encryption", None )
        #
        #    if custom_encryption_path:
        #        custom_encryption = turbogears.util.load_class(
        #            custom_encryption_path)

        #    if custom_encryption:
        #        hashed_password = custom_encryption(password_8bit)

        # make sure the hased password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode columns
        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        return hashed_password

    def validate_password(self, password):
        """Check the password against existing credentials.
        """
        algorithm = config.get('authorize.hashmethod', None)
        return self.password == self.__encrypt_password(algorithm, password)

class Permission(object):
    """A relationship that determines what each Group can do
    """
    pass

mapper(User, users_table,
        properties=dict(_password=users_table.c.password))

mapper(Group, groups_table,
        properties=dict(users=relation(User,
                secondary=user_group_table, backref='groups')))

mapper(Permission, permissions_table,
        properties=dict(groups=relation(Group,
                secondary=group_permission_table, backref='permissions')))


 - Add the following import in you controllers.root file::

   from tgrepozewho import authorize

 - Add the following methods to your controllers.root:RootController
   class::

    @expose('whotg.templates.about')
    @authorize.require(authorize.has_permission('manage'))
    def manage_permission_only(self, **kw):
        return dict(now=now, page='about')
    
    @expose('whotg.templates.about')
    @authorize.require(authorize.is_user('editor'))
    def editor_user_only(self, **kw):
        return dict(now=now, page='about')

    @expose('whotg.templates.login')
    def login(self, **kw):
        came_from = kw.get('came_from', '/')
        return dict(now=now, page='login', header=lambda *arg: None,
                    footer=lambda *arg: None, came_from=came_from)



 - Add the following template as "login.html" into your project's
   'templates' directory::

      <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
                            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
      <html xmlns="http://www.w3.org/1999/xhtml"
            xmlns:py="http://genshi.edgewall.org/"
            xmlns:xi="http://www.w3.org/2001/XInclude">

      <xi:include href="master.html" />

      <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
        <title>Login Form</title>
      </head>

      <body>

        <form action="/login_handler?came_from=${came_from}" method="POST">
            Login: <input type="text" name="login"></input><br/>
            Password: <input type="password" name="password"></input><br/>
            <input type="submit" name="submit"/>
        </form>

      </body>
      </html>

 - Setup you database config in the normal way by tweaking the development.ini file

 - Create the necessary tables by using::

   paster setup-app development.ini

 - Create a user manually in your database

 - Create a group (any name), and a permission named "manage", link this permission
   to the group you just created and also add a user to your group.

 - Create another user which is in no group but is named "editor"

 - Start the project's server via paster serve::

   paster server --reload development.ini

 - Visit http://localhost:8080/editor_user_only in your browser.  You
   will be presented with the login form.  The "right"
   username/password combination is "editor/editpass" (this user has the
   username 'editor').  Submitting this set of credentials will show
   the about page.  Any other username/password combination will
   result in the user being presented the login form again.  Note that
   once you've obtained the credentials for the first time, if you
   visit the /editor_user_only page again, you are not asked to
   reauthenticate.  Log out forcibly by visiting
   http://localhost:8080/logout_handler.

 - Visit http://localhost:8080/manage_permission_only in your browser.
   You will be presented with the login form.  The "right"
   username/password combination is "manager/managepass" (this user
   possesses the manage permission).  Submitting this set of
   credentials will show the about page.  Any other username/password
   combination will result in the user being presented the login form
   again.  Note that if you've authenticated as the 'editor' user, and
   you visit the /manage_permission_only page, you will be logged out
   and asked for credentials (editors cannot see this page).  Note
   that once you've obtained the credentials for the first time, if
   you visit the /manage_permission_only page again, you are not asked
   to reauthenticate.  Log out forcibly by visiting
   http://localhost:8080/logout_handler.

Misc

  If you start "paster serve" in a shell with the WHO_LOG environment
  variable set to "1", you will see repoze.who logging output on the
  console.

Not yet finished

  You can run the unit tests by using "python setup.py test" in the
  source package.


