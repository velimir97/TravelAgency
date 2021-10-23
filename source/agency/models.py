from agency import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# table for connecting tourists and arrangements 
# meny to meny
tourist_arangement_table = db.Table('tourist_arangement_table',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('ang_id', db.Integer, db.ForeignKey('arangement.id'), primary_key=True)
)

class UserModel(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    desired_type = db.Column(db.String(15), nullable=False)
    current_type = db.Column(db.String(15), nullable=False)
    guide_arangements = db.relationship('ArangementModel', backref='guide', lazy=True)
    tourist_arangements = db.relationship("ArangementModel", secondary=tourist_arangement_table, lazy=True, backref=db.backref('tourists', lazy = 'dynamic'))

    # password hashing 
    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password_hash(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"User(name = {self.name}, surname = {self.surname}, username = {self.username})"

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "desired_type": self.desired_type,
            "current_type": self.current_type,
            "guide_arangements": self.guide_arangements,
            "tourist_arangements": self.tourist_arangements
        }

@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))

class ArangementModel(db.Model):
    __tablename__ = "arangement"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False, unique=True)
    destination = db.Column(db.String(50), nullable=False)
    number_of_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    guide_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    admin_id = db.Column(db.Integer, nullable=False)
    free_seats = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Arangement(start = {start_date}, end = {end_date}, description = {description})"

    def to_json(self):
        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "description": self.description,
            "destination": self.destination,
            "number_of_seats": self.number_of_seats,
            "price": self.price,
            "guide_id": self.guide_id,
            "admin_id": self.admin_id,
            "free_seats": self.free_seats,
        }