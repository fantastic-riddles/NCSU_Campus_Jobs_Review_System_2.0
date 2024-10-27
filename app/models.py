from app import db

class Reviews(db.Model):
    """Model which stores the information of the reviews submitted"""
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(64), index=True, nullable=False)
    locations = db.Column(db.String(120), index=True, nullable=False)
    job_title = db.Column(db.String(64), index=True, nullable=False)
    job_description = db.Column(db.String(120), index=True, nullable=False)
    hourly_pay = db.Column(db.Integer, nullable=False)
    benefits = db.Column(db.String(120), index=True, nullable=False)
    review = db.Column(db.String(120), index=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    recommendation = db.Column(db.Integer, nullable=False)
    
class User(db.Model):
    """Model which stores the information of the reviews submitted"""
    __tablename__ = 'users'
    user_name = db.Column(db.String(10), nullable=False, primary_key=True)
    name = db.Column(db.String(64),  index=True, nullable=False)
    email = db.Column(db.String(64), index=True, nullable=False)
    password = db.Column(db.String(24), index=True, nullable=False)
    type = db.Column(db.String(10), index=True, nullable=False)
    

    
class Application(db.Model):
    """Model which stores the information of the reviews submitted"""
    __tablename__ = 'applications'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))