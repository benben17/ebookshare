from datetime import datetime
from flask_jwt_extended import create_access_token
from book.dicts import UserRole
from book.utils import gen_userid, commUtil, model_to_dict, get_file_name
from book import User, db
import json
import urllib
from flask import request, redirect, url_for, Blueprint
from rauth import OAuth2Service
import config

blueprint = Blueprint(
    get_file_name(__file__),
    __name__,
    url_prefix='/user/google'
)


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = config.OAUTH_CREDENTIALS[provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('googleUser.oauth_callback', provider=self.provider_name, _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        googleinfo = urllib.request.urlopen('https://accounts.google.com/.well-known/openid-configuration')
        google_params = json.load(googleinfo)
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=google_params.get('authorization_endpoint'),
            base_url=google_params.get('userinfo_endpoint'),
            access_token_url=google_params.get('token_endpoint')
        )

    def authorize(self):
        print(self.get_callback_url())
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()
                  },
            decoder=json.loads
        )
        return oauth_session.get('').json()


@blueprint.route('/authorize/<provider>')
def oauth_authorize(provider):
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@blueprint.route('/<provider>/callback')
def oauth_callback(provider):
    oauth = OAuthSignIn.get_provider(provider)
    data = oauth.callback()
    if 'email' not in data or data['email'] is None:
        # I need a valid email address for my user identification
        return redirect('https://rss2ebook.com/user/login')
    email = data['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create the user. Try and use their name returned by Google,
        name = str(email).split('@')[0]
        user = User(id=gen_userid(), name=name, email=email, kindle_email=email, role=UserRole.role_name(),
                    create_time=datetime.utcnow(), is_reg_rss=True)
        if commUtil.sync_user(user):
            db.session.add(user)
            db.session.commit()
            user_info = model_to_dict(user)
            access_token = create_access_token(identity=user_info)
            # data = {"user": user_info, "token": access_token}
            return redirect('https://rss2ebook.com/subscribe/my?token='+access_token)
        else:
            return redirect('https://rss2ebook.com/user/login')
    else:
        user_info = model_to_dict(user)
        access_token = create_access_token(identity=user_info)
        return redirect('https://rss2ebook.com/subscribe/my?token='+access_token)
