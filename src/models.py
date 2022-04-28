#from msilib.schema import InstallUISequence
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(280), unique=False, nullable=False)
    

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password":self.password
            # do not serialize the password, its a security breach
        }
    @classmethod
    def create(cls,name,email,password):
        instance =cls(
            name=name,
            email=email,
            password=password
        )
        if isinstance(instance,cls):
            return instance 
        else:
            return None    
    
    # @classmethod
    # def login(cls,email1,password):
    #     user=cls.query.filter_by(email=email1).one_or_none()
    #     if (not isinstance(user,cls)):
    #         return user
    #     if user.password==password:
    #         return user
    #     else:
    #         return False       
